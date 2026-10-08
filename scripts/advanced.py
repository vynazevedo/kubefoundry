"""Optional labs. All mutations target the dedicated kind-kubefoundry context."""
import contextlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ['KUBECONFIG']=str(ROOT/'.state/kubeconfig')
K=['kubectl','--context','kind-kubefoundry']
NS='kf-platform'
VERSIONS=dict(line.split('=',1) for line in (ROOT/'versions.env').read_text().splitlines() if line and not line.startswith('#'))

def k(*args,obj=None,binary=False,stdin=None,check=True):
    p=subprocess.run(K+list(args),input=(json.dumps(obj).encode() if binary else json.dumps(obj)) if obj is not None else stdin,capture_output=True,text=not binary,timeout=360)
    if check and p.returncode:raise RuntimeError(str(p.stderr))
    return p.stdout if check else p

def get(kind,name=None,ns=NS):
    return json.loads(k('-n',ns,'get',kind,*([name] if name else []),'-o','json'))

def wait(label,predicate,timeout=180):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if predicate(): print('PASS '+label,flush=True);return
        time.sleep(3)
    raise AssertionError('Timeout: '+label)

def apply_items(items):
    for item in items.get('items',[items]):
        if item['kind']=='Namespace':
            existing=k('get','namespace',item['metadata']['name'],'-o','json',check=False)
            if existing.returncode==0 and json.loads(existing.stdout)['metadata'].get('labels',{}).get('kubefoundry.io/managed')!='advanced':
                raise RuntimeError('Refusing to adopt existing namespace '+item['metadata']['name'])
    k('apply','-f','-',obj=items)

def apply_file(name):
    apply_items(json.loads((ROOT/'labs/advanced'/name).read_text()))

def rollout(name,ns=NS,kind='deployment'):
    k('-n',ns,'rollout','status',kind+'/'+name,'--timeout=240s')

def exec_http(path,method='get',body=None,pod='deployment/workbench'):
    args=['-n',NS,'exec',pod,'--','/workbench',method,'http://127.0.0.1:8080'+path]
    if body is not None:args.append(body)
    return k(*args)

@contextlib.contextmanager
def forward(service,port,ns=NS):
    with socket.socket() as s:s.bind(('127.0.0.1',0));local=s.getsockname()[1]
    with open(ROOT/'.state/port-forward.log','a') as log:
        process=subprocess.Popen(K+['-n',ns,'port-forward','service/'+service,f'{local}:{port}','--address','127.0.0.1'],stdout=log,stderr=log)
        try:
            for _ in range(100):
                if process.poll() is not None:raise RuntimeError('Port-forward exited')
                try:
                    with socket.create_connection(('127.0.0.1',local),timeout=.1):break
                except OSError:time.sleep(.2)
            else:raise RuntimeError('Port-forward unavailable')
            yield f'http://127.0.0.1:{local}'
        finally:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()

def http_json(url):
    with urllib.request.urlopen(url,timeout=10) as r:return json.load(r)

def base():
    apply_file('base.json');rollout('workbench');rollout('storage',kind='statefulset')

def configuration():
    initial=json.loads(exec_http('/config'))
    marker='config-'+uuid.uuid4().hex[:8]
    k('-n',NS,'patch','configmap','settings','--type=merge','-p',json.dumps({'data':{'message':marker}}))
    wait('mounted ConfigMap updates without restart',lambda:json.loads(exec_http('/config'))['mounted']==marker,180)
    assert json.loads(exec_http('/config'))['environment']==initial['environment']
    print('PASS environment remains unchanged before restart',flush=True)
    k('-n',NS,'rollout','restart','deployment/workbench');rollout('workbench')
    assert json.loads(exec_http('/config'))['environment']==marker
    assert exec_http('/secret-status').strip()=='credential configured'
    print('PASS restart refreshes environment and fixture Secret is mounted without exposing it',flush=True)

def storage():
    marker='persistent-'+uuid.uuid4().hex
    exec_http('/data','put',marker,pod='storage-0')
    old=get('pod','storage-0')['metadata']['uid']
    k('-n',NS,'delete','pod','storage-0','--wait=true')
    k('-n',NS,'wait','--for=condition=Ready','pod/storage-0','--timeout=180s')
    assert get('pod','storage-0')['metadata']['uid']!=old
    assert exec_http('/data',pod='storage-0')==marker
    print('PASS PVC preserves data across pod replacement',flush=True)

def telemetry_up():
    apply_file('observability.json')
    for name in ['jaeger','collector','prometheus']:rollout(name,'kf-observability')
    k('-n',NS,'patch','deployment','workbench','--type=strategic','--patch-file','labs/advanced/workbench-tracing.json')
    rollout('workbench')

def telemetry_test():
    with forward('prometheus',9090,'kf-observability') as prom, forward('jaeger',16686,'kf-observability') as jaeger:
        def query(q):return http_json(prom+'/api/v1/query?query='+urllib.parse.quote(q))['data']['result']
        wait('Prometheus scrapes a healthy target',lambda:any(x['value'][1]=='1' for x in query('up{job="workbench"}')))
        # Let a baseline sample exist before incrementing the failure counter.
        time.sleep(6)
        failed=k('-n',NS,'exec','deployment/workbench','--','/workbench','get','http://127.0.0.1:8080/fail',check=False)
        assert failed.returncode and 'HTTP 503' in failed.stderr,failed.stderr
        wait('controlled failure visible in metrics',lambda: bool(query('workbench_failures_total > 0')))
        wait('alert fires on the controlled failure',lambda:bool(query('ALERTS{alertname="WorkbenchIntentionalFailure",alertstate="firing"}')))
        logs=k('-n',NS,'logs','-l','app=workbench','--all-containers=true','--tail=100')
        entries=[json.loads(line) for line in logs.splitlines() if line.startswith('{')]
        failures=[e for e in entries if e.get('path')=='/fail' and e.get('trace_id') not in (None,'0'*32)]
        assert failures, 'No failure log with trace ID'
        trace_id=failures[-1]['trace_id']
        def stored():
            try:return bool(http_json(jaeger+'/api/traces/'+trace_id).get('data'))
            except urllib.error.HTTPError as exc:
                if exc.code==404:return False
                raise
        wait('exact failure trace is queryable in Jaeger',stored)
        print('PASS failure log includes a nonzero trace ID',flush=True)

def autoscaling():
    # kind uses self-signed kubelet certificates. This is a local lab exception only.
    manifest=ROOT/'.state/metrics-server.yaml'
    subprocess.run(['curl','-fsSL','https://github.com/kubernetes-sigs/metrics-server/releases/download/'+VERSIONS['METRICS_SERVER_VERSION']+'/components.yaml','-o',str(manifest)],check=True)
    k('apply','-f',str(manifest))
    patch={'spec':{'template':{'spec':{'containers':[{'name':'metrics-server','args':['--cert-dir=/tmp','--secure-port=10250','--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname','--kubelet-use-node-status-port','--metric-resolution=15s','--kubelet-insecure-tls']}]}}}}
    k('-n','kube-system','patch','deployment','metrics-server','--type=strategic','-p',json.dumps(patch));rollout('metrics-server','kube-system')
    apply_file('hpa.json')
    def metric_ready():
        return bool(get('hpa','workbench').get('status',{}).get('currentMetrics'))
    wait('HPA receives resource metrics',metric_ready,180)
    # This bounded load runs inside the storage Pod, outside the HPA target.
    load=subprocess.Popen(K+['-n',NS,'exec','storage-0','--','/workbench','load','http://workbench:8080/work','150'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:wait('HPA scales above one replica under load',lambda:get('deployment','workbench')['spec']['replicas']>1,180)
    finally:
        load.wait(timeout=180)
    wait('HPA returns to one replica after load',lambda:get('deployment','workbench')['spec']['replicas']==1,300)
    k('-n',NS,'delete','hpa','workbench')

def main():
    actions={'up':base,'config':configuration,'storage':storage,'telemetry-up':telemetry_up,'telemetry-test':telemetry_test,'autoscaling':autoscaling}
    if len(sys.argv)!=2 or sys.argv[1] not in actions:raise SystemExit('Usage: advanced.py '+ '|'.join(actions))
    actions[sys.argv[1]]()
if __name__=='__main__':main()
