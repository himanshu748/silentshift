from pathlib import Path
import sys,json,subprocess,os
from types import SimpleNamespace
repo=Path.cwd();fresh=repo/'.local/backend-polish/final-source';sys.path.insert(0,str(fresh/'scripts'))
from verify_ipm_clean import activate,command
from bootstrap import read_env
c='silentshift-bonus-load-backend-final-nov10';D=['docker','--context','colima-silentshift']
original=fresh/'.local/ipm/bonus-runs'/c
output=fresh/'.local/ipm/resume-backend-final';output.mkdir(parents=True,mode=0o700)
net=json.loads((repo/'.local/backend-polish/explicit-network.json').read_text());plan=json.loads((original/'plan.json').read_text())
actual=json.loads(subprocess.check_output([*D,'inspect',c],text=True))[0]
assert actual['Image']==plan['image_id'] and actual['Mounts']==[]
assert 'SS_PRISTINE_OK' in (original/'03-pristine.log').read_text()
assert '18-network.log' in list(p.name for p in original.glob('*.log'))
assert 'all predefined address pools' in (original/'18-network.log').read_text()
def run(argv,label,**kw):return command(argv,log=output/(label+'.log'),**kw).stdout
def session(script,label,namespace='SILENTSHIFT',marker=None):
 t=run([*D,'exec','-i',c,'iris','session','IRIS','-U',namespace],label,data=script+'\nhalt\n')
 if marker and marker not in t.splitlines():raise RuntimeError('Missing '+marker+' in '+label)
 return t
script='set sc=##class(SilentShift.IPM).RequireStopped()\nif $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nset q=##class(%SQL.Statement).%ExecDirect(,"SELECT COUNT(*) AS N FROM SilentShift_Data.CaseRecord")\nif \'q.%Next() halt\nif q.%Get("N")\'=0 halt\nwrite "SS_EMPTY_BEFORE_ACTIVATION",!'
session(script,'01-still-empty',marker='SS_EMPTY_BEFORE_ACTIVATION')
runtime=read_env(original/'runtime.env')
a=SimpleNamespace(container=c,api_port=53003,context='colima-silentshift',vm_profile='silentshift',gateway_image='containers.intersystems.com/intersystems/webgateway:2026.1',min_host_free_gib=1.8,min_vm_free_gib=3)
activate(a,output,runtime,D,session,run,network_id=net['id']);print('RESUMED_PRODUCTION_STARTED',flush=True)
run([*D,'cp',str(fresh/'tests/iris'),c+':/home/irisowner/final-tests'],'23-copy-tests')
run([*D,'exec','--user','0',c,'mkdir','-p','/var/opt/silentshift/partner-inbox'],'24-inbox')
run([*D,'exec','--user','0',c,'chown','51773:51773','/var/opt/silentshift/partner-inbox'],'25-inbox-owner')
run([*D,'exec',c,'chmod','700','/var/opt/silentshift/partner-inbox'],'26-inbox-mode')
unit=session('set ^UnitTestRoot="/home/irisowner/final-tests/"\nset manager=##class(%UnitTest.Manager).%New()\nset ok=manager.RunTest("","/nodelete")\nwrite "SS_UNIT_RESULT=",ok,!','27-unit-tests')
assert 'All PASSED' in unit and '**FAILED**' not in unit
print('NATIVE_UNIT_ALL_PASSED',flush=True)
replays=[]
for number in (1,2):
 path=output/f'replay-{number}.json'
 run([sys.executable,str(fresh/'scripts/trace_example.py'),'--api','http://127.0.0.1:53003/silentshift/api','--context','colima-silentshift','--container',c,'--output',str(path)],f'28-replay-{number}',env={**os.environ,**runtime},timeout=300)
 replays.append(json.loads(path.read_text()));print('REPLAY_'+str(number)+'_PASSED',flush=True)
receipt={'kind':'fresh-local-branch-source-load-with-resumed-activation','source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=fresh,text=True).strip(),'source':'local Git clone; no public push authorized','version':'0.3.0','published_package':False,'runtime':(original/'03-pristine.log').read_text().split('SS_RUNTIME=')[1].splitlines()[0],'no_application_source_mounts':True,'pristine_namespace_verified_before_install':True,'empty_before_first_activation':True,'initial_activation_failure':'Docker default address pools exhausted','resumed_same_installed_container':True,'explicit_network':net,'full_native_suite_passed':True,'replays':replays,'fresh_inference':False}
(output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
