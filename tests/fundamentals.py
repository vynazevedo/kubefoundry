"""Exercise the raw-manifest learning path in an isolated, temporary namespace."""
import json
from pathlib import Path
import subprocess
import time
import uuid

NAMESPACE = 'fundamentos-test-' + uuid.uuid4().hex[:8]
BASE = ['kubectl', '--context', 'kind-kubefoundry']

def k(*args, obj=None, check=True):
    result = subprocess.run(BASE + list(args), input=json.dumps(obj) if obj is not None else None,
                            text=True, capture_output=True, timeout=120)
    if check and result.returncode:
        raise RuntimeError(result.stderr + result.stdout)
    return result

def wait_for(description, predicate):
    deadline = time.monotonic() + 100
    while time.monotonic() < deadline:
        if predicate():
            print('PASS ' + description, flush=True)
            return
        time.sleep(1)
    raise AssertionError('Timed out: ' + description)

def apply(name):
    obj = json.loads(k('create', '--dry-run=client', '--validate=false', '-f',
                      str(Path('labs/fundamentos') / name), '-o', 'json').stdout)
    if obj['kind'] == 'Namespace':
        obj['metadata']['name'] = NAMESPACE
    else:
        obj['metadata']['namespace'] = NAMESPACE
    k('apply', '-f', '-', obj=obj)

def pods():
    return json.loads(k('-n', NAMESPACE, 'get', 'pods', '-l', 'app=primeiro-deployment', '-o', 'json').stdout)['items']

def endpoints():
    slices = json.loads(k('-n', NAMESPACE, 'get', 'endpointslices', '-l',
                         'kubernetes.io/service-name=primeiro-service', '-o', 'json').stdout)['items']
    return [ep for s in slices for ep in (s.get('endpoints') or []) if ep.get('conditions', {}).get('ready') is True]

created = False
try:
    apply('namespace.yaml')
    created = True
    apply('network.yaml')
    apply('pod.yaml')
    k('-n', NAMESPACE, 'wait', '--for=condition=Ready', 'pod/primeiro-pod', '--timeout=90s')
    k('-n', NAMESPACE, 'delete', 'pod', 'primeiro-pod', '--wait=true')
    result = k('-n', NAMESPACE, 'get', 'pod', 'primeiro-pod', check=False)
    assert result.returncode and 'NotFound' in result.stderr, result.stderr
    print('PASS standalone pod remains deleted', flush=True)
    apply('pod.yaml')
    k('-n', NAMESPACE, 'wait', '--for=condition=Ready', 'pod/primeiro-pod', '--timeout=90s')
    apply('deployment.yaml')
    k('-n', NAMESPACE, 'rollout', 'status', 'deployment/primeiro-deployment', '--timeout=100s')
    old = pods()[0]['metadata']
    k('-n', NAMESPACE, 'delete', 'pod', old['name'], '--wait=true')
    def replaced():
        current = pods()
        return len(current) == 2 and all(p['metadata']['uid'] != old['uid'] and
            any(c['type'] == 'Ready' and c['status'] == 'True' for c in p.get('status', {}).get('conditions', [])) for p in current)
    wait_for('deployment recreates a ready pod with a new UID', replaced)
    apply('service.yaml')
    wait_for('service has two ready endpoints', lambda: len(endpoints()) == 2)
    ip = k('-n', NAMESPACE, 'get', 'service', 'primeiro-service', '-o', 'jsonpath={.spec.clusterIP}').stdout
    k('-n', NAMESPACE, 'exec', 'primeiro-pod', '--', '/demo', 'probe', f'http://{ip}:8080/healthz')
    print('PASS in-cluster HTTP request succeeds', flush=True)
    k('-n', NAMESPACE, 'patch', 'service', 'primeiro-service', '--type=merge', '-p', '{"spec":{"selector":{"app":"nao-existe"}}}')
    wait_for('wrong service selector removes ready endpoints', lambda: len(endpoints()) == 0)
    failed = k('-n', NAMESPACE, 'exec', 'primeiro-pod', '--', '/demo', 'probe', f'http://{ip}:8080/healthz', check=False)
    assert failed.returncode and ('connect: connection refused' in failed.stderr or 'timeout' in failed.stderr or 'deadline exceeded' in failed.stderr), failed.stderr
    print('PASS service without endpoints rejects HTTP request', flush=True)
    # Restore manifests and prove recovery rather than accepting the failure alone.
    apply('service.yaml')
    wait_for('restoring selector recovers ready endpoints', lambda: len(endpoints()) == 2)
    k('-n', NAMESPACE, 'exec', 'primeiro-pod', '--', '/demo', 'probe', f'http://{ip}:8080/healthz')
    patch = {'spec': {'strategy': {'type': 'Recreate', 'rollingUpdate': None}, 'template': {'spec': {'containers': [{'name': 'demo',
             'readinessProbe': {'httpGet': {'path': '/nao-existe'}}}]}}}}
    # Recreate replaces all replicas only in this temporary test namespace.
    k('-n', NAMESPACE, 'patch', 'deployment', 'primeiro-deployment', '--type=strategic', '-p', json.dumps(patch))
    def unready():
        current = pods()
        return len(current) >= 2 and all(p['spec']['containers'][0]['readinessProbe']['httpGet']['path'] == '/nao-existe' and
            any(c['type'] == 'Ready' and c['status'] == 'False' for c in p.get('status', {}).get('conditions', [])) for p in current) and len(endpoints()) == 0
    wait_for('failed readiness removes service traffic endpoints', unready)
    apply('deployment.yaml')
    k('-n', NAMESPACE, 'rollout', 'status', 'deployment/primeiro-deployment', '--timeout=100s')
    wait_for('restoring readiness recovers service endpoints', lambda: len(endpoints()) == 2)
    k('-n', NAMESPACE, 'exec', 'primeiro-pod', '--', '/demo', 'probe', f'http://{ip}:8080/healthz')
finally:
    if created:
        k('delete', 'namespace', NAMESPACE, '--wait=false')
