import copy
import json
from pathlib import Path
import advanced as lab

names=['kf-team-a','kf-team-b']
for ns in names:
    items=[]
    for original in json.loads(Path('labs/advanced/base.json').read_text())['items']:
        if original['kind']=='StatefulSet' or original['metadata']['name']=='storage':continue
        item=copy.deepcopy(original)
        if item['kind']=='Namespace':item['metadata']['name']=ns
        else:item['metadata']['namespace']=ns
        if item['kind']=='NetworkPolicy':
            item['spec']['ingress']=[{'from':[{'podSelector':{}}],'ports':[{'port':8080}]}]
            item['spec']['egress']=item['spec']['egress'][:2]
        items.append(item)
    existing=lab.k('get','namespace',ns,'-o','json',check=False)
    if existing.returncode==0:
        assert json.loads(existing.stdout)['metadata'].get('labels',{}).get('kubefoundry.io/managed')=='advanced','Refusing to adopt namespace'
    lab.k('apply','-f','-',obj={'apiVersion':'v1','kind':'List','items':items})
    role={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'Role','metadata':{'name':'observer','namespace':ns},'rules':[{'apiGroups':[''],'resources':['pods','pods/log'],'verbs':['get','list','watch']}]}
    sa={'apiVersion':'v1','kind':'ServiceAccount','metadata':{'name':'observer','namespace':ns},'automountServiceAccountToken':False}
    rb={'apiVersion':'rbac.authorization.k8s.io/v1','kind':'RoleBinding','metadata':{'name':'observer','namespace':ns},'subjects':[{'kind':'ServiceAccount','name':'observer','namespace':ns}],'roleRef':{'apiGroup':'rbac.authorization.k8s.io','kind':'Role','name':'observer'}}
    quota={'apiVersion':'v1','kind':'ResourceQuota','metadata':{'name':'budget','namespace':ns},'spec':{'hard':{'requests.cpu':'1','requests.memory':'512Mi','limits.memory':'1Gi','pods':'8','services.loadbalancers':'0','services.nodeports':'0'}}}
    lab.k('apply','-f','-',obj={'apiVersion':'v1','kind':'List','items':[role,sa,rb,quota]});lab.rollout('workbench',ns)
for source in names:
    own=lab.get('service','workbench',source)['spec']['clusterIP']
    other=names[1] if source==names[0] else names[0]
    remote=lab.get('service','workbench',other)['spec']['clusterIP']
    lab.k('-n',source,'exec','deployment/workbench','--','/workbench','get',f'http://{own}:8080/')
    def rejected():
        p=lab.k('-n',source,'exec','deployment/workbench','--','/workbench','get',f'http://{remote}:8080/',check=False)
        return p.returncode!=0 and 'http://' in p.stderr and ('timeout' in p.stderr or 'deadline exceeded' in p.stderr)
    lab.wait(source+' cannot reach '+other,rejected)
    identity='system:serviceaccount:'+source+':observer'
    for ns,resource,allowed in [(source,'pods',True),(source,'secrets',False),(other,'pods',False)]:
        p=lab.k('-n',ns,'auth','can-i','get',resource,'--as',identity,check=False)
        assert p.stdout.strip()==('yes' if allowed else 'no'),p.stderr+p.stdout
    print('PASS '+source+' can read own pods but not secrets or another team',flush=True)
