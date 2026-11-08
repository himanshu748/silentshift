from pathlib import Path
import subprocess,json,sys,time,os,re,datetime,argparse
root=Path(__file__).resolve().parent;clone=root/'fresh-clone';sys.path.insert(0,str(clone/'scripts'))
from bootstrap import read_env
from verify_ipm_clean import space
from verify_native import Client
container='silentshift-bonus-load-030-replay-nov8';original=clone/'.local/ipm/bonus-runs'/container;docker=['docker','--context','colima-silentshift'];plan=json.loads((original/'plan.json').read_text());runtime=read_env(original/'runtime.env')
receipt={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'container':container,'scope':'Complete the SAME freshly created isolated candidate container after storage-preflight stop; no new source load or reset','passed':False,'steps':[]}
def run(cmd,label,data=None,env=None):
 start=time.monotonic();p=subprocess.run(cmd,cwd=clone,input=data,text=True,env=env,capture_output=True,timeout=600);(root/('resume-'+label+'-output.txt')).write_text(p.stdout+p.stderr);receipt['steps'].append({'label':label,'command':cmd,'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-start,3)});(root/'replay-resume.json').write_text(json.dumps(receipt,indent=2)+'\n')
 if p.returncode:raise RuntimeError('Resume failed at '+label)
 return p.stdout
identity=json.loads(run([*docker,'inspect',container],'identity'))[0]
assert identity['Id']==(original/'01-create.log').read_text().strip() and identity['Image']==plan['image_id'] and identity['Mounts']==[]
assert identity['Config']['Labels']['silentshift.scope']=='bonus-release-verification'
network=json.loads(run([*docker,'network','inspect',container],'network'))[0];assert network['Id']==(original/'18-network.log').read_text().strip()
assert 'SS_RUNTIME_SETUP_OK' in (original/'20-setup.log').read_text().splitlines()
assert runtime['SILENTSHIFT_PROVIDER_MODE']=='recorded-replay'
args=argparse.Namespace(vm_profile='silentshift',min_host_free_gib=1.8,min_vm_free_gib=3)
receipt['resume_space']=space(args)
existing=subprocess.run([*docker,'inspect',container+'-gateway'],capture_output=True,text=True)
if existing.returncode==0:
 gateway=json.loads(existing.stdout)[0];assert gateway['Id']==(root/'resume-gateway-output.txt').read_text().strip()
else:
 gateway=None
for name in ['CSP.conf','CSP.ini']:assert (original/name).is_file()
if gateway is None:
 run([*docker,'run','-d','--pull','never','--init','--name',container+'-gateway','--network',container,'--network-alias','gateway','--publish','127.0.0.1:52933:80','--env','ISC_CSP_CONF_FILE=/silentshift-gateway/CSP.conf','--env','ISC_CSP_INI_FILE=/silentshift-gateway/CSP.ini','--mount','type=bind,src='+str(original/'CSP.conf')+',dst=/silentshift-gateway/CSP.conf,readonly','--mount','type=bind,src='+str(original/'CSP.ini')+',dst=/silentshift-gateway/CSP.ini','--log-opt','max-size=10m','--log-opt','max-file=2','containers.intersystems.com/intersystems/webgateway:2026.1'],'gateway')
client=Client('http://127.0.0.1:52933/silentshift/api',runtime['SILENTSHIFT_IRIS_USERNAME'],runtime['SILENTSHIFT_IRIS_PASSWORD'])
for _ in range(30):
 try:
  status,health=client.call('/health')
  if status==200 and health.get('production',{}).get('running'):break
 except OSError:pass
 time.sleep(1)
else:raise RuntimeError('Fresh replay API unavailable')
receipt['production_health_verified']=True
run([*docker,'exec','--user','0',container,'mkdir','-p','/var/opt/silentshift/partner-inbox'],'inbox-directory')
run([*docker,'exec','--user','0',container,'chown','51773:51773','/var/opt/silentshift/partner-inbox'],'inbox-owner')
run([*docker,'exec',container,'chmod','700','/var/opt/silentshift/partner-inbox'],'inbox-mode')
script='set ^UnitTestRoot="/home/irisowner/silentshift-bonus/tests/"\nset manager=##class(%UnitTest.Manager).%New()\nset passed=manager.RunTest("","/nodelete")\nwrite "SS_UNIT_RESULT=",passed,!\nif \'passed halt\nwrite "SS_UNIT_OK",!\nhalt\n'
(root/'resume-unit-command.cos').write_text(script)
unit=run([*docker,'exec','-i',container,'iris','session','IRIS','-U','SILENTSHIFT'],'unit',script)
assert 'SS_UNIT_OK' in unit.splitlines() and '**FAILED**' not in unit and 'Some tests FAILED' not in unit
classes=re.findall(r'SilentShift.Test.\w+ passed',unit);methods=re.findall(r'^\s+Test\w+ passed$',unit,re.M);assert len(classes)==5 and len(methods)==12
receipt['native_classes_passed']=len(classes);receipt['native_methods_passed']=len(methods)
for label in ['first','second']:
 print('Running candidate replay '+label,flush=True)
 target=root/('resume-replay-'+label+'.json')
 run(['uv','run','python','scripts/trace_example.py','--api','http://127.0.0.1:52933/silentshift/api','--context','colima-silentshift','--container',container,'--output',str(target)],'replay-'+label,env={**os.environ,**runtime})
 result=json.loads(target.read_text());assert result['passed'] and len(result['checks'])==12;receipt['replay_'+label]=result
receipt['passed']=True;receipt['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(root/'replay-resume.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'passed':True,'native_classes':len(classes),'native_methods':len(methods),'replays':[{'session_id':receipt['replay_'+label]['session_id'],'passed_checks':sum(receipt['replay_'+label]['checks'].values())} for label in ['first','second']]}),flush=True)
