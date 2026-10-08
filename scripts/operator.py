import json
import advanced as lab
ns='kf-operator'
schema={'type':'object','required':['spec'],'properties':{
    'spec':{'type':'object','required':['replicas'],'properties':{'replicas':{'type':'integer','minimum':1,'maximum':3}}},
    'status':{'type':'object','properties':{'ready':{'type':'boolean'},'observedGeneration':{'type':'integer'}}}
}}
crd={'apiVersion':'apiextensions.k8s.io/v1','kind':'CustomResourceDefinition',
     'metadata':{'name':'studyapps.learning.kubefoundry.io'},
     'spec':{'group':'learning.kubefoundry.io','scope':'Namespaced',
             'names':{'plural':'studyapps','singular':'studyapp','kind':'StudyApp'},
             'versions':[{'name':'v1alpha1','served':True,'storage':True,
                          'subresources':{'status':{}},'schema':{'openAPIV3Schema':schema}}]}}

namespace={'apiVersion':'v1','kind':'Namespace','metadata':{'name':ns,'labels':{'kubefoundry.io/managed':'advanced','pod-security.kubernetes.io/enforce':'restricted'}}}
sa={'apiVersion':'v1','kind':'ServiceAccount','metadata':{'name':'study-controller','namespace':ns}}
role={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'Role','metadata':{'name':'study-controller','namespace':ns},'rules':[{'apiGroups':['learning.kubefoundry.io'],'resources':['studyapps'],'verbs':['get','list']},{'apiGroups':['learning.kubefoundry.io'],'resources':['studyapps/status'],'verbs':['patch']},{'apiGroups':['apps'],'resources':['deployments'],'verbs':['get','create','patch']}]}
rb={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'RoleBinding','metadata':{'name':'study-controller','namespace':ns},'roleRef':{'apiGroup':'rbac.authorization.k8s.io','kind':'Role','name':'study-controller'},'subjects':[{'kind':'ServiceAccount','name':'study-controller','namespace':ns}]}
dep={'apiVersion':'apps/v1','kind':'Deployment','metadata':{'name':'study-controller','namespace':ns},'spec':{'replicas':1,'strategy':{'type':'Recreate'},'selector':{'matchLabels':{'app':'study-controller'}},'template':{'metadata':{'labels':{'app':'study-controller'}},'spec':{'serviceAccountName':'study-controller','securityContext':{'runAsNonRoot':True,'runAsUser':65532,'seccompProfile':{'type':'RuntimeDefault'}},'containers':[{'name':'controller','image':'kubefoundry/study-operator:0.1.0','imagePullPolicy':'Never','env':[{'name':'WATCH_NAMESPACE','value':ns}],'resources':{'requests':{'cpu':'25m','memory':'32Mi'},'limits':{'memory':'64Mi'}},'securityContext':{'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}}}]}}}}
lab.apply_items({'apiVersion':'v1','kind':'List','items':[crd,namespace,sa,role,rb,dep]})
lab.k('wait','--for=condition=Established','crd/studyapps.learning.kubefoundry.io','--timeout=60s');lab.rollout('study-controller',ns)
example={'apiVersion':'learning.kubefoundry.io/v1alpha1','kind':'StudyApp','metadata':{'name':'example','namespace':ns},'spec':{'replicas':1}}
for invalid_spec in (None, {'replicas':0}, {'replicas':4}):
    invalid={'apiVersion':example['apiVersion'],'kind':'StudyApp','metadata':{'name':'invalid-example','namespace':ns}}
    if invalid_spec is not None:invalid['spec']=invalid_spec
    result=lab.k('create','--dry-run=server','-f','-',obj=invalid,check=False)
    assert result.returncode!=0 and 'spec' in result.stderr and 'Invalid' in result.stderr,result.stderr
print('PASS CRD rejects missing specification and out-of-range replicas',flush=True)
lab.k('apply','-f','-',obj=example)
def ready():
    cr=lab.get('studyapp','example',ns)
    return cr.get('status',{}).get('ready') and cr['status'].get('observedGeneration')==cr['metadata']['generation']
lab.wait('operator reconciles a ready application',ready)
lab.k('-n',ns,'patch','studyapp','example','--type=merge','-p','{"spec":{"replicas":2}}')
lab.wait('operator reconciles the new generation',ready)
assert lab.get('deployment','study-example',ns)['spec']['replicas']==2
old=lab.get('deployment','study-example',ns)['metadata']['uid']
lab.k('-n',ns,'delete','deployment','study-example','--wait=true')
def replaced():
    result=lab.k('-n',ns,'get','deployment','study-example','-o','json',check=False)
    return result.returncode==0 and json.loads(result.stdout)['metadata']['uid']!=old
lab.wait('operator recreates removed owned deployment',replaced);lab.rollout('study-example',ns)
lab.k('-n',ns,'delete','studyapp','example')
lab.wait('garbage collection removes owned deployment',lambda:'NotFound' in lab.k('-n',ns,'get','deployment','study-example',check=False).stderr)
identity='system:serviceaccount:'+ns+':study-controller'
assert lab.k('-n','kube-system','auth','can-i','create','deployments','--as',identity,check=False).stdout.strip()=='no'
print('PASS controller cannot create deployments outside its namespace',flush=True)
