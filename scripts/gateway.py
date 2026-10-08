import base64
import copy
import json
import ssl
import urllib.request
import advanced as lab
from pathlib import Path
ns=lab.NS
def resource(kind,name,spec,api):return {'apiVersion':api,'kind':kind,'metadata':{'name':name,'namespace':ns},'spec':spec}
resources=[resource('Issuer','local-selfsigned',{'selfSigned':{}},'cert-manager.io/v1'),resource('Certificate','workbench-local',{'secretName':'workbench-tls','dnsNames':['localhost'],'issuerRef':{'name':'local-selfsigned','kind':'Issuer'}},'cert-manager.io/v1')]
# Explicit ClusterIP keeps the lab off public load balancers.
resources += [resource('EnvoyProxy','local-proxy',{'provider':{'type':'Kubernetes','kubernetes':{'envoyService':{'type':'ClusterIP'}}}},'gateway.envoyproxy.io/v1alpha1')]
gc={'apiVersion':'gateway.networking.k8s.io/v1','kind':'GatewayClass','metadata':{'name':'kubefoundry'},'spec':{'controllerName':'gateway.envoyproxy.io/gatewayclass-controller'}}
resources += [gc,resource('Gateway','workbench',{'gatewayClassName':'kubefoundry','infrastructure':{'parametersRef':{'group':'gateway.envoyproxy.io','kind':'EnvoyProxy','name':'local-proxy'}},'listeners':[{'name':'https','protocol':'HTTPS','port':443,'hostname':'localhost','tls':{'mode':'Terminate','certificateRefs':[{'name':'workbench-tls'}]},'allowedRoutes':{'namespaces':{'from':'Same'}}}]},'gateway.networking.k8s.io/v1')]
route=resource('HTTPRoute','workbench',{'parentRefs':[{'name':'workbench'}],'hostnames':['localhost'],'rules':[{'backendRefs':[{'name':'workbench','port':8080,'weight':100}]}]},'gateway.networking.k8s.io/v1')
resources.append(route)
lab.k('apply','-f','-',obj={'apiVersion':'v1','kind':'List','items':resources})
lab.k('-n',ns,'wait','--for=condition=Ready','certificate/workbench-local','--timeout=180s')
lab.k('-n',ns,'wait','--for=condition=Programmed','gateway/workbench','--timeout=180s')
def proxy_service():
    services=json.loads(lab.k('-n','envoy-gateway-system','get','services','-l','gateway.envoyproxy.io/owning-gateway-name=workbench','-o','json'))['items']
    return services[0]['metadata']['name'] if services else None
lab.wait('Envoy proxy Service exists',lambda:proxy_service() is not None)
cert=base64.b64decode(lab.get('secret','workbench-tls')['data']['tls.crt']).decode()
ctx=ssl.create_default_context(cadata=cert)
with lab.forward(proxy_service(),443,'envoy-gateway-system') as url:
    https=url.replace('http://127.0.0.1','https://localhost')
    def check():
        try:
            with urllib.request.urlopen(https,context=ctx,timeout=10) as r:return r.status==200
        except urllib.error.HTTPError as e:
            if e.code in (500,502,503):return False
            raise
    lab.wait('HTTPS gateway serves application with verified hostname and CA',check)
    try:
        urllib.request.urlopen(https,timeout=5)
    except urllib.error.URLError as e:
        assert isinstance(e.reason,ssl.SSLCertVerificationError),str(e)
    else:raise AssertionError('Unexpected system trust for local self-signed certificate')
    print('PASS untrusted certificate is rejected without the lab CA',flush=True)
# Persist only public routing objects and no private key.
Path('.state/gateway-route.json').write_text(json.dumps(route,indent=2))
