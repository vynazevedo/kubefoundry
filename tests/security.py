"""Live positive and negative controls. Requires the dedicated lab cluster."""
import copy
import json
import subprocess
import time

BASE = ["kubectl", "--context", "kind-kubefoundry", "-n", "playground"]
def kubectl(*args, obj=None):
    return subprocess.run(BASE + list(args), input=json.dumps(obj) if obj else None,
                          text=True, capture_output=True, timeout=90)
def require(result):
    if result.returncode:
        raise RuntimeError(result.stderr + result.stdout)
    return result.stdout

pod = {
    "apiVersion": "v1", "kind": "Pod",
    "metadata": {"name": "security-test", "labels": {"kubefoundry.io/client": "allowed"}},
    "spec": {
        "restartPolicy": "Never", "automountServiceAccountToken": False,
        "securityContext": {"runAsNonRoot": True, "runAsUser": 65532,
                            "seccompProfile": {"type": "RuntimeDefault"}},
        "containers": [{"name": "probe", "image": "kubefoundry/demo:0.1.0",
            "imagePullPolicy": "Never",
            "args": ["probe", "http://demo:8080/healthz"],
            "securityContext": {"readOnlyRootFilesystem": True,
                                "allowPrivilegeEscalation": False, "capabilities": {"drop": ["ALL"]}},
            "resources": {"requests": {"cpu": "10m", "memory": "16Mi"}, "limits": {"memory": "32Mi"}}}]
    }
}
require(kubectl("create", "--dry-run=server", "-f", "-", obj=pod))
for name, mutate, expected in [
    ("privileged", lambda p: p["spec"]["containers"][0]["securityContext"].update(privileged=True, allowPrivilegeEscalation=True), "PodSecurity"),
    ("writable", lambda p: p["spec"]["containers"][0]["securityContext"].update(readOnlyRootFilesystem=False), "read-only root filesystem"),
    ("token", lambda p: p["spec"].update(automountServiceAccountToken=True), "service account token"),
    ("init-writable", lambda p: p["spec"].update(initContainers=[dict(copy.deepcopy(p["spec"]["containers"][0]), name="init", securityContext={"runAsNonRoot": True, "allowPrivilegeEscalation": False, "capabilities": {"drop": ["ALL"]}, "readOnlyRootFilesystem": False})]), "Init containers"),
]:
    bad = copy.deepcopy(pod)
    mutate(bad)
    result = kubectl("create", "--dry-run=server", "-f", "-", obj=bad)
    assert result.returncode != 0 and expected in result.stderr, (name, result.stderr)
    print(f"PASS admission rejects {name}")

ip = require(kubectl("get", "svc", "demo", "-o", "jsonpath={.spec.clusterIP}"))
# Use the same destination IP for both probes, so DNS failure cannot masquerade as isolation.
for allowed in (True, False):
    obj = copy.deepcopy(pod)
    name = "probe-allowed" if allowed else "probe-denied"
    obj["metadata"]["name"] = name
    obj["metadata"]["labels"]["kubefoundry.io/client"] = "allowed" if allowed else "denied"
    obj["spec"]["containers"][0]["args"] = ["probe", f"http://{ip}:8080/healthz"]
    require(kubectl("delete", "pod", name, "--ignore-not-found", "--wait=true"))
    try:
        require(kubectl("create", "-f", "-", obj=obj))
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            current = json.loads(require(kubectl("get", "pod", name, "-o", "json")))
            phase = current.get("status", {}).get("phase")
            if phase in ("Succeeded", "Failed"):
                break
            time.sleep(1)
        else:
            raise AssertionError(f"{name} did not finish; image/scheduling failures are not a successful test")
        logs = require(kubectl("logs", name))
        if allowed:
            assert phase == "Succeeded", logs
        else:
            assert phase == "Failed" and ("timeout" in logs or "deadline exceeded" in logs), logs
        print(f"PASS network {'allows labeled client' if allowed else 'blocks unlabeled client'}")
    finally:
        require(kubectl("delete", "pod", name, "--ignore-not-found", "--wait=false"))

identity = "system:serviceaccount:playground:developer-observer"
for verb, resource, allowed in [("get", "pods/log", True), ("get", "secrets", False), ("create", "deployments", False)]:
    result = kubectl("auth", "can-i", verb, resource, "--as", identity)
    assert result.stdout.strip() == ("yes" if allowed else "no"), result.stderr + result.stdout
    print(f"PASS RBAC {verb} {resource} is {allowed}")
