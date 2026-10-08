"""Logical backup/restore drill using synthetic data and two temporary CNPG clusters."""
import json
import os
from pathlib import Path
import time
import uuid
import advanced as lab

prefix='recovery-'+uuid.uuid4().hex[:8]
source=prefix+'-source';target=prefix+'-target';namespace='databases';created=[]
started=time.monotonic()
def cluster(name):
    template=json.loads(lab.k('-n',namespace,'get','cluster','study','-o','json'))
    spec={key:template['spec'][key] for key in ['instances','storage','resources']}
    spec['enableSuperuserAccess']=False
    obj={'apiVersion':'postgresql.cnpg.io/v1','kind':'Cluster','metadata':{'name':name,'namespace':namespace},'spec':spec}
    lab.k('create','-f','-',obj=obj);created.append(name)
    lab.k('-n',namespace,'wait','--for=condition=Ready','cluster/'+name,'--timeout=300s')
    return lab.get('cluster',name,namespace)['status']['currentPrimary']
def sql(pod,command):
    return lab.k('-n',namespace,'exec',pod,'--','psql','-U','postgres','-d','app','-At','-v','ON_ERROR_STOP=1','-c',command).strip()
try:
    src=cluster(source)
    sql(src,"CREATE TABLE learning_marker (id integer PRIMARY KEY, note text NOT NULL); INSERT INTO learning_marker VALUES (1, 'before-backup');")
    dump=lab.k('-n',namespace,'exec',src,'--','pg_dump','-U','postgres','-d','app','-Fc',binary=True)
    assert dump.startswith(b'PGDMP'), 'Not a custom-format PostgreSQL backup'
    path=Path('.state')/(prefix+'.dump')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(dump)
    sql(src,"INSERT INTO learning_marker VALUES (2, 'after-backup');")
    dst=cluster(target)
    restore_start=time.monotonic()
    lab.k('-n',namespace,'exec','-i',dst,'--','pg_restore','-U','postgres','-d','app','--no-owner','--exit-on-error',binary=True,stdin=dump)
    assert sql(dst,'SELECT id || chr(58) || note FROM learning_marker ORDER BY id;')=='1:before-backup'
    assert sql(src,'SELECT count(*) FROM learning_marker;')=='2'
    report={'source':source,'target':target,'backup':str(path),'backup_bytes':len(dump),'restore_and_validation_seconds':round(time.monotonic()-restore_start,2),'whole_drill_seconds':round(time.monotonic()-started,2),'restored_rows':1,'rows_written_after_backup_not_restored':1,'scope':'Logical database backup of synthetic data; no PITR or cloud disaster-recovery claim'}
    Path('.state/recovery-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS independent database restore preserves pre-backup data and excludes later writes',flush=True)
    print(json.dumps(report,indent=2))
finally:
    for name in created:lab.k('-n',namespace,'delete','cluster',name,'--wait=false')
