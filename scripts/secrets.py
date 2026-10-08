import base64
import json
import uuid
import advanced as lab
source='kf-secret-source';target=lab.NS
ns={'apiVersion':'v1','kind':'Namespace','metadata':{'name':source,'labels':{'kubefoundry.io/managed':'advanced','pod-security.kubernetes.io/enforce':'restricted'}}}
sa={'apiVersion':'v1','kind':'ServiceAccount','metadata':{'name':'external-reader','namespace':target},'automountServiceAccountToken':False}
role={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'Role','metadata':{'name':'fixture-reader','namespace':source},'rules':[{'apiGroups':[''],'resources':['secrets'],'verbs':['get','list','watch']},{'apiGroups':['authorization.k8s.io'],'resources':['selfsubjectrulesreviews'],'verbs':['create']}]}
rb={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'RoleBinding','metadata':{'name':'fixture-reader','namespace':source},'roleRef':{'apiGroup':'rbac.authorization.k8s.io','kind':'Role','name':'fixture-reader'},'subjects':[{'kind':'ServiceAccount','name':'external-reader','namespace':target}]}
store={'apiVersion':'external-secrets.io/v1','kind':'SecretStore','metadata':{'name':'fixture-source','namespace':target},'spec':{'provider':{'kubernetes':{'remoteNamespace':source,'server':{'caProvider':{'type':'ConfigMap','name':'kube-root-ca.crt','key':'ca.crt'}},'auth':{'serviceAccount':{'name':'external-reader'}}}}}}
es={'apiVersion':'external-secrets.io/v1','kind':'ExternalSecret','metadata':{'name':'rotated-credential','namespace':target},'spec':{'refreshInterval':'5s','secretStoreRef':{'name':'fixture-source','kind':'SecretStore'},'target':{'name':'rotated-credential','creationPolicy':'Owner'},'data':[{'secretKey':'token','remoteRef':{'key':'fixture','property':'token'}}]}}
lab.apply_items({'apiVersion':'v1','kind':'List','items':[ns,sa,role,rb,store,es]})
for revision in (1,2):
    value='FICTITIOUS-'+str(revision)+'-'+uuid.uuid4().hex
    lab.k('apply','-f','-',obj={'apiVersion':'v1','kind':'Secret','metadata':{'name':'fixture','namespace':source},'stringData':{'token':value}})
    def synced():
        p=lab.k('-n',target,'get','secret','rotated-credential','-o','json',check=False)
        if p.returncode:return False
        data=json.loads(p.stdout).get('data',{}).get('token','')
        return base64.b64decode(data).decode()==value
    lab.wait('ExternalSecret synchronizes revision '+str(revision)+' without exposing its value',synced)
identity='system:serviceaccount:'+target+':external-reader'
r=lab.k('-n','kube-system','auth','can-i','get','secrets','--as',identity,check=False)
assert r.stdout.strip()=='no',r.stdout+r.stderr
print('PASS provider identity cannot read secrets outside its source namespace',flush=True)
