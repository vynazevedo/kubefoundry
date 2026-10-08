package main

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"
)

func handler(settings, data string) http.Handler {
	var requests, failures atomic.Uint64
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(200) })
	mux.HandleFunc("GET /config", func(w http.ResponseWriter, r *http.Request) {
		message, err := os.ReadFile(settings + "/message")
		if err != nil {
			http.Error(w, "configuration unavailable", 503)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"mounted": string(message), "environment": os.Getenv("APP_MESSAGE")})
	})
	mux.HandleFunc("GET /secret-status", func(w http.ResponseWriter, r *http.Request) {
		b, err := os.ReadFile("/credentials/token")
		if err != nil || len(b) == 0 {
			http.Error(w, "credential not configured", 503)
			return
		}
		fmt.Fprint(w, "credential configured")
	})
	var fileMu sync.Mutex
	mux.HandleFunc("POST /data", func(w http.ResponseWriter, r *http.Request) {
		r.Body = http.MaxBytesReader(w, r.Body, 1024)
		b, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, "payload too large", 413)
			return
		}
		fileMu.Lock()
		defer fileMu.Unlock()
		if err = os.WriteFile(data+"/message.tmp", b, 0600); err == nil {
			err = os.Rename(data+"/message.tmp", data+"/message")
		}
		if err != nil {
			http.Error(w, "storage unavailable", 503)
			return
		}
		w.WriteHeader(201)
	})
	mux.HandleFunc("GET /data", func(w http.ResponseWriter, r *http.Request) {
		fileMu.Lock()
		defer fileMu.Unlock()
		b, err := os.ReadFile(data + "/message")
		if err != nil {
			http.Error(w, "no stored data", 404)
			return
		}
		w.Write(b)
	})
	mux.HandleFunc("GET /fail", func(w http.ResponseWriter, r *http.Request) {
		failures.Add(1)
		http.Error(w, "intentional lab failure", 503)
	})
	mux.HandleFunc("GET /work", func(w http.ResponseWriter, r *http.Request) {
		// Fixed per-request budget; only internal ClusterIP access is enabled by default.
		until := time.Now().Add(25 * time.Millisecond)
		b := []byte("bounded-work")
		for time.Now().Before(until) {
			select {
			case <-r.Context().Done():
				return
			default:
			}
			sum := sha256.Sum256(b)
			b = sum[:]
		}
		fmt.Fprint(w, "work completed")
	})
	mux.HandleFunc("GET /metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		fmt.Fprintf(w, "# TYPE workbench_requests_total counter\nworkbench_requests_total %d\n# TYPE workbench_failures_total counter\nworkbench_failures_total %d\n", requests.Load(), failures.Load())
	})
	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		revision := os.Getenv("APP_REVISION")
		if revision == "" {
			revision = "stable"
		}
		fmt.Fprint(w, "kubefoundry workbench "+revision)
	})
	observed := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requests.Add(1)
		// Do not log URL query strings, bodies, headers or credentials.
		slog.Info("request", "method", r.Method, "path", r.URL.Path, "trace_id", trace.SpanContextFromContext(r.Context()).TraceID().String())
		mux.ServeHTTP(w, r)
	})
	return otelhttp.NewHandler(observed, "workbench.request")
}

func request(method, url, body string) (string, error) {
	c := http.Client{Timeout: 5 * time.Second, CheckRedirect: func(r *http.Request, v []*http.Request) error { return http.ErrUseLastResponse }}
	req, err := http.NewRequest(method, url, strings.NewReader(body))
	if err != nil {
		return "", err
	}
	res, err := c.Do(req)
	if err != nil {
		return "", err
	}
	defer res.Body.Close()
	b, err := io.ReadAll(io.LimitReader(res.Body, 1<<20))
	if err != nil {
		return "", err
	}
	if res.StatusCode >= 300 {
		return string(b), fmt.Errorf("HTTP %d", res.StatusCode)
	}
	return string(b), nil
}
func main() {
	if len(os.Args) >= 3 && os.Args[1] == "get" {
		b, e := request("GET", os.Args[2], "")
		fmt.Print(b)
		if e != nil {
			slog.Error("request failed", "error", e)
			os.Exit(1)
		}
		return
	}
	if len(os.Args) == 4 && os.Args[1] == "put" {
		_, e := request("POST", os.Args[2], os.Args[3])
		if e != nil {
			slog.Error("request failed", "error", e)
			os.Exit(1)
		}
		return
	}
	if len(os.Args) == 4 && os.Args[1] == "load" {
		seconds, e := strconv.Atoi(os.Args[3])
		if e != nil || seconds < 1 || seconds > 180 {
			slog.Error("load duration must be 1..180 seconds")
			os.Exit(1)
		}
		deadline := time.Now().Add(time.Duration(seconds) * time.Second)
		var wg sync.WaitGroup
		for i := 0; i < 4; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for time.Now().Before(deadline) {
					request("GET", os.Args[2], "")
					time.Sleep(10 * time.Millisecond)
				}
			}()
		}
		wg.Wait()
		return
	}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, nil)))
	var tp *sdktrace.TracerProvider
	if os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT") != "" {
		exporter, err := otlptracehttp.New(ctx)
		if err != nil {
			slog.Error("telemetry setup failed", "error", err)
			os.Exit(1)
		}
		tp = sdktrace.NewTracerProvider(sdktrace.WithBatcher(exporter), sdktrace.WithResource(resource.NewWithAttributes("", attribute.String("service.name", "kubefoundry-workbench"))))
		otel.SetTracerProvider(tp)
		otel.SetTextMapPropagator(propagation.TraceContext{})
	}
	srv := http.Server{Addr: ":8080", Handler: handler("/settings", "/data"), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second, WriteTimeout: 10 * time.Second, IdleTimeout: 30 * time.Second, MaxHeaderBytes: 16 << 10}
	done := make(chan struct{})
	go func() {
		<-ctx.Done()
		shutdown, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		srv.Shutdown(shutdown)
		if tp != nil {
			tp.Shutdown(shutdown)
		}
		close(done)
	}()
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		slog.Error("server stopped", "error", err)
		os.Exit(1)
	}
	<-done
}
