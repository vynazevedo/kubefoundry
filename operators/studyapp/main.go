package main

import (
	"bytes"
	"context"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

type object = map[string]any

var client *http.Client
var base, namespace string

func api(method, path string, body any) (object, int, error) {
	b, _ := json.Marshal(body)
	req, err := http.NewRequest(method, base+path, bytes.NewReader(b))
	if err != nil {
		return nil, 0, err
	}
	token, err := os.ReadFile("/var/run/secrets/kubernetes.io/serviceaccount/token")
	if err != nil {
		return nil, 0, err
	}
	req.Header.Set("Authorization", "Bearer "+string(token))
	req.Header.Set("Content-Type", "application/json")
	if method == "PATCH" {
		req.Header.Set("Content-Type", "application/merge-patch+json")
	}
	r, err := client.Do(req)
	if err != nil {
		return nil, 0, err
	}
	defer r.Body.Close()
	var out object
	json.NewDecoder(io.LimitReader(r.Body, 2<<20)).Decode(&out)
	if r.StatusCode >= 300 && r.StatusCode != 404 {
		return out, r.StatusCode, fmt.Errorf("API returned %d for %s", r.StatusCode, path)
	}
	return out, r.StatusCode, nil
}
func owned(meta object, uid string) bool {
	refs, _ := meta["ownerReferences"].([]any)
	for _, ref := range refs {
		m, ok := ref.(map[string]any)
		if ok && m["uid"] == uid && m["controller"] == true {
			return true
		}
	}
	return false
}
func reconcile(cr object) error {
	meta := cr["metadata"].(map[string]any)
	name := meta["name"].(string)
	uid := meta["uid"].(string)
	replicas := cr["spec"].(map[string]any)["replicas"]
	path := "/apis/apps/v1/namespaces/" + namespace + "/deployments/study-" + name
	dep, code, err := api("GET", path, nil)
	if err != nil {
		return err
	}
	if code != 404 && !owned(dep["metadata"].(map[string]any), uid) {
		return fmt.Errorf("refusing to adopt deployment owned by another actor")
	}
	owner := []any{object{"apiVersion": "learning.kubefoundry.io/v1alpha1", "kind": "StudyApp", "name": name, "uid": uid, "controller": true, "blockOwnerDeletion": false}}
	if code == 404 {
		desired := object{"apiVersion": "apps/v1", "kind": "Deployment", "metadata": object{"name": "study-" + name, "namespace": namespace, "ownerReferences": owner}, "spec": object{"replicas": replicas, "selector": object{"matchLabels": object{"app": "study-" + name}}, "template": object{"metadata": object{"labels": object{"app": "study-" + name}}, "spec": object{"automountServiceAccountToken": false, "securityContext": object{"runAsNonRoot": true, "runAsUser": 65532, "seccompProfile": object{"type": "RuntimeDefault"}}, "containers": []any{object{"name": "app", "image": "kubefoundry/workbench:0.1.0", "imagePullPolicy": "Never", "ports": []any{object{"containerPort": 8080}}, "securityContext": object{"allowPrivilegeEscalation": false, "readOnlyRootFilesystem": true, "capabilities": object{"drop": []string{"ALL"}}}, "resources": object{"requests": object{"cpu": "25m", "memory": "32Mi"}, "limits": object{"memory": "64Mi"}}, "readinessProbe": object{"httpGet": object{"path": "/healthz", "port": 8080}, "periodSeconds": 2}}}}}}}
		_, _, err = api("POST", "/apis/apps/v1/namespaces/"+namespace+"/deployments", desired)
		return err
	}
	spec := dep["spec"].(map[string]any)
	if spec["replicas"] != replicas {
		_, _, err = api("PATCH", path, object{"metadata": object{"resourceVersion": dep["metadata"].(map[string]any)["resourceVersion"]}, "spec": object{"replicas": replicas}})
		return err
	}
	status, _ := dep["status"].(map[string]any)
	ready := status["availableReplicas"] == replicas && status["observedGeneration"] == dep["metadata"].(map[string]any)["generation"]
	current, _ := cr["status"].(map[string]any)
	if current["ready"] == ready && current["observedGeneration"] == meta["generation"] {
		return nil
	}
	_, _, err = api("PATCH", "/apis/learning.kubefoundry.io/v1alpha1/namespaces/"+namespace+"/studyapps/"+name+"/status", object{"metadata": object{"resourceVersion": meta["resourceVersion"]}, "status": object{"ready": ready, "observedGeneration": meta["generation"]}})
	return err
}
func main() {
	namespace = os.Getenv("WATCH_NAMESPACE")
	if namespace == "" {
		panic("WATCH_NAMESPACE required")
	}
	ca, err := os.ReadFile("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
	if err != nil {
		panic(err)
	}
	pool := x509.NewCertPool()
	if !pool.AppendCertsFromPEM(ca) {
		panic("invalid CA")
	}
	client = &http.Client{Timeout: 10 * time.Second, Transport: &http.Transport{TLSClientConfig: &tls.Config{RootCAs: pool, MinVersion: tls.VersionTLS12}}}
	base = "https://kubernetes.default.svc"
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, syscall.SIGINT)
	defer stop()
	ticker := time.NewTicker(3 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			list, _, err := api("GET", "/apis/learning.kubefoundry.io/v1alpha1/namespaces/"+namespace+"/studyapps", nil)
			if err != nil {
				slog.Error("list failed", "error", err)
				continue
			}
			items, _ := list["items"].([]any)
			for _, item := range items {
				if err := reconcile(item.(map[string]any)); err != nil {
					slog.Error("reconcile failed", "error", err)
				}
			}
		}
	}
}
