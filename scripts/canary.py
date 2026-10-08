"""Canary routing exercise with two configuration revisions and verified TLS."""
import base64
import collections
import copy
import json
import ssl
import urllib.request
from pathlib import Path
import advanced as lab
base=json.loads(Path('labs/advanced/base.json').read_text())['items']
dep=copy.deepcopy(next(o for o in base if o['kind']=='Deployment'))
dep['metadata']['name']='canary';dep['spec']['selector']['matchLabels']={'app':'canary'};dep['spec']['template']['metadata']['labels']={'app':'canary'}
dep['spec']['template']['spec']['containers'][0]['env'].append({'name':'APP_REVISION','value':'canary'})
svc={'apiVersion':'v1','kind':'Service','metadata':{'name':'canary','namespace':lab.NS},'spec':{'selector':{'app':'canary'},'ports':[{'port':8080,'targetPort':8080}]}}
lab.k('apply','-f','-',obj={'apiVersion':'v1','kind':'List','items':[dep,svc]})
lab.k('-n',lab.NS,'rollout','restart','deployment/workbench');lab.rollout('workbench');lab.rollout('canary')
services=json.loads(lab.k('-n','envoy-gateway-system','get','services','-l','gateway.envoyproxy.io/owning-gateway-name=workbench','-o','json'))['items']
assert len(services)==1
cert=base64.b64decode(lab.get('secret','workbench-tls')['data']['tls.crt']).decode()
ctx=ssl.create_default_context(cadata=cert)
def weights(stable,canary):
    lab.k('-n',lab.NS,'patch','httproute','workbench','--type=merge','-p',json.dumps({'spec':{'rules':[{'backendRefs':[{'name':'workbench','port':8080,'weight':stable},{'name':'canary','port':8080,'weight':canary}]}]}}))
with lab.forward(services[0]['metadata']['name'],443,'envoy-gateway-system') as url:
    endpoint=url.replace('http://127.0.0.1','https://localhost')
    def sample():
        counts=collections.Counter()
        for _ in range(30):
            with urllib.request.urlopen(endpoint,context=ctx,timeout=10) as r:counts[r.read().decode().split()[-1]]+=1
        return counts
    try:
        weights(100,0)
        lab.wait('baseline routes only to stable configuration',lambda:sample()=={'stable':30})
        weights(50,50)
        def both():
            c=sample()
            return c['stable']>0 and c['canary']>0
        lab.wait('canary and stable both receive real HTTPS requests',both)
    finally:
        weights(100,0)
    lab.wait('rollback routes only to stable again',lambda:sample()=={'stable':30})
lab.k('-n',lab.NS,'delete','deployment,service','canary')
