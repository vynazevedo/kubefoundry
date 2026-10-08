package main

import (
	"net/http/httptest"
	"os"
	"strings"
	"testing"
)

func TestConfigurationAndStorage(t *testing.T) {
	settings := t.TempDir()
	data := t.TempDir()
	t.Setenv("APP_MESSAGE", "initial")
	if err := os.WriteFile(settings+"/message", []byte("mounted"), 0600); err != nil {
		t.Fatal(err)
	}
	h := handler(settings, data)
	for _, c := range []struct {
		method, path, body string
		code               int
		contains           string
	}{
		{"GET", "/config", "", 200, "mounted"}, {"POST", "/data", "persistent", 201, ""}, {"GET", "/data", "", 200, "persistent"},
		{"POST", "/data", strings.Repeat("x", 1025), 413, ""}, {"GET", "/data", "", 200, "persistent"},
		{"GET", "/fail", "", 503, "intentional"}, {"GET", "/metrics", "", 200, "workbench_failures_total 1"},
	} {
		w := httptest.NewRecorder()
		h.ServeHTTP(w, httptest.NewRequest(c.method, c.path, strings.NewReader(c.body)))
		if w.Code != c.code || !strings.Contains(w.Body.String(), c.contains) {
			t.Fatalf("%s: %d %s", c.path, w.Code, w.Body.String())
		}
	}
}
func TestClientRejectsHTTPFailure(t *testing.T) {
	s := httptest.NewServer(handler(t.TempDir(), t.TempDir()))
	defer s.Close()
	if _, err := request("GET", s.URL+"/fail", ""); err == nil {
		t.Fatal("accepted failure")
	}
}
