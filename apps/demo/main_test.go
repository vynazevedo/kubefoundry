package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRoutes(t *testing.T) {
	for _, tc := range []struct {
		method, path string
		code         int
	}{
		{"GET", "/", 200}, {"GET", "/healthz", 200}, {"GET", "/readyz", 200},
		{"GET", "/missing", 404}, {"POST", "/", 405},
	} {
		t.Run(tc.method+tc.path, func(t *testing.T) {
			r := httptest.NewRecorder()
			handler().ServeHTTP(r, httptest.NewRequest(tc.method, tc.path, nil))
			if r.Code != tc.code {
				t.Fatalf("got %d, want %d", r.Code, tc.code)
			}
		})
	}
}
func TestProbeRejectsErrorsAndRedirects(t *testing.T) {
	for _, code := range []int{200, 302, 403, 500} {
		s := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Location", "/")
			w.WriteHeader(code)
		}))
		err := probe(s.URL)
		s.Close()
		if (err == nil) != (code == 200) {
			t.Fatalf("code %d produced %v", code, err)
		}
	}
}
