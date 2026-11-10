#!/usr/bin/env python3
"""Explicit fresh-container registry/load install, native tests and replay or live checks.

Only uniquely named new local resources are created. Existing stacks and the
Docker default context are untouched. Credentials and command logs stay private.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from fetch_ipm import SHA256, SIZE
from package_ipm import ROOT, module_version, stage
from verify_ipm_clean import (
    RELEASE,
    activate,
    available_network_subnet,
    command,
    prepare_native,
    private_write,
    runtime_environment,
    space,
    validate_network_subnet,
)
from verify_ipm_native import literal


def verification_inputs(args):
    """Select test assertions separately from the backend being installed."""
    source = Path(getattr(args, 'verification_source', None) or ROOT).resolve()
    if source != ROOT.resolve() and (args.source != 'public-registry'
                                    or args.execution_mode != 'recorded-replay'):
        raise ValueError('Alternate --verification-source is only for public-registry recorded-replay; '
                         'source-load verification must use its own source tests')
    tests = source / 'tests/iris'
    trace = source / 'scripts/trace_example.py'
    if not tests.is_dir() or not trace.is_file():
        raise ValueError('--verification-source must contain tests/iris and scripts/trace_example.py')
    return {'source': source, 'tests': tests, 'trace': trace}


def execute(args):
    if args.execution_mode == 'live' and not args.allow_model_calls:
        raise ValueError('Live verification requires --allow-model-calls for local inference')
    if args.install_latest and args.source != 'public-registry':
        raise ValueError('--install-latest requires --source public-registry')
    validate_network_subnet(getattr(args, 'network_subnet', None))
    verification = verification_inputs(args)
    if not re.fullmatch(r'silentshift-bonus-(load|registry)-[a-z0-9-]{1,35}', args.container):
        raise ValueError('Use a new silentshift-bonus-load-* or silentshift-bonus-registry-* container')
    docker=['docker','--context',args.context]
    subnet = available_network_subnet(getattr(args, 'network_subnet', None), docker)
    def checked(argv, **kw): return command(argv, **kw)
    if checked([*docker,'container','inspect',args.container],check=False).returncode == 0:
        raise ValueError('Container exists; do not replace it')
    image=json.loads(checked([*docker,'image','inspect',args.image]).stdout)[0]
    if (image.get('Config',{}).get('Labels') or {}).get('com.intersystems.platform-version') != '2026.3.0AI.154.0com':
        raise ValueError('Use the verified official 2026.3.0AI.154.0 Community image')
    vendor=ROOT/'.local/ipm/vendor/zpm-0.10.10.xml'
    if vendor.stat().st_size != SIZE or hashlib.sha256(vendor.read_bytes()).hexdigest()!=SHA256:
        raise ValueError('Pinned official IPM 0.10.10 installer is missing/mismatched')
    before_space=space(args)
    runtime=runtime_environment(args)
    runtime['SILENTSHIFT_PROVIDER_MODE']=args.execution_mode
    plan={'container':args.container,'source':args.source,'version':args.version,
        'image_id':image['Id'],'source_mounts':0,'existing_runtime_modified':False,
        'execution_mode':args.execution_mode,'space':before_space,'executed':False,
        'verification_source':str(verification['source']),'network_subnet':subnet}
    if not args.execute: return plan
    output=ROOT/'.local/ipm/bonus-runs'/args.container
    output.mkdir(parents=True,mode=0o700)
    private_write(output/'plan.json',json.dumps(plan,indent=2)+'\n')
    private_write(output/'runtime.env',''.join(k+'='+v+'\n' for k,v in runtime.items()))
    def run(argv,label,**kw): return checked(argv,log=output/(label+'.log'),**kw).stdout
    def session(script,label,namespace='SILENTSHIFT',marker=None):
        text=run([*docker,'exec','-i',args.container,'iris','session','IRIS','-U',namespace],label,data=script+'\nhalt\n')
        if marker and marker not in text.splitlines():
            raise RuntimeError('Missing '+marker+'; inspect private '+label+'.log')
        return text
    def cli(text,label):
        return session('set sc=##class(%IPM.Main).Shell('+literal(text)+')\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\n'
            'write "SS_IPM_COMMAND_OK",!',label,marker='SS_IPM_COMMAND_OK')
    phase='create'
    try:
        print('Creating fresh '+args.source+' verification container...',flush=True)
        run([*docker,'run','-d','--pull','never','--init','--name',args.container,
            '--hostname',args.container,'--label','silentshift.scope=bonus-release-verification',
            '--network','none','--memory','3g','--cpus','2','--shm-size','256m',
            '--env-file',str(output/'runtime.env'),'--log-opt','max-size=10m',image['Id']],'01-create')
        for attempt in range(60):
            ready=checked([*docker,'exec','-i',args.container,'iris','session','IRIS','-U','%SYS'],
                data='write "SS_READY",!\nhalt\n',check=False,timeout=20)
            if ready.returncode==0 and 'SS_READY' in ready.stdout.splitlines():break
            time.sleep(1)
        else:raise RuntimeError('Fresh IRIS did not start')
        mounts=json.loads(run([*docker,'inspect','--format','{{json .Mounts}}',args.container],'02-mounts'))
        if mounts:raise ValueError('Fresh application container must have no mounts')
        phase='pristine namespace'
        pristine=session('write "SS_RUNTIME=",$zversion,!\n'
            'if ##class(Config.Namespaces).Exists("SILENTSHIFT") halt\n'
            'write "SS_PRISTINE_OK",!','03-pristine','%SYS','SS_PRISTINE_OK')
        base='/home/irisowner/silentshift-bonus'
        run([*docker,'exec',args.container,'mkdir','-p',base],'04-directory')
        private_write(output/'namespace.cpf','[Actions]\nCreateResource:Name=%DB_SILENTSHIFT,Description="Isolated SilentShift bonus verification"\n'
            'CreateDatabase:Name=SILENTSHIFT,Directory=/usr/irissys/mgr/SILENTSHIFT,Resource=%DB_SILENTSHIFT\n'
            'CreateNamespace:Name=SILENTSHIFT,Globals=SILENTSHIFT,Routines=SILENTSHIFT,Interop=1\n')
        run([*docker,'cp',str(output/'namespace.cpf'),args.container+':'+base+'/namespace.cpf'],'05-copy-namespace')
        run([*docker,'exec','--user','0',args.container,'chown','51773:51773',base+'/namespace.cpf'],'06-owner')
        run([*docker,'exec',args.container,'iris','merge','IRIS',base+'/namespace.cpf'],'07-namespace')
        session('set properties("Enabled")=1\nset sc=##class(Security.Services).Modify("%Service_CallIn",.properties)\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nwrite "SS_PYTHON_OK",!',
            '08-python','%SYS','SS_PYTHON_OK')
        run([*docker,'cp',str(vendor),args.container+':'+base+'/zpm.xml'],'09-copy-client')
        session('set sc=$system.OBJ.Load('+literal(base+'/zpm.xml')+',"ck")\n'
            'if $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nwrite "SS_CLIENT_OK",!',
            '10-client',marker='SS_CLIENT_OK')
        cli('config set analytics 0','11-no-analytics')
        phase=args.source
        if args.source=='load':
            source=output/'stage';stage(ROOT,source)
            run([*docker,'cp',str(source),args.container+':'+base+'/stage'],'12-copy-candidate')
            install_command='load '+base+'/stage'
        else:
            run([*docker,'network','disconnect','none',args.container],'12-disconnect-none')
            run([*docker,'network','connect','bridge',args.container],'13-registry-egress')
            cli('repo -r -n PublicCommunity -url https://pm.community.intersystems.com/ -user "" -pass "" -publish 0 -read-only 1','14-public-repo')
            install_command=('install silentshift' if args.install_latest else
                'install PublicCommunity/silentshift '+args.version+' -synchronous')
        print('IPM '+install_command,flush=True)
        cli(install_command,'15-install')
        session('set module=##class(%IPM.Storage.Module).NameOpen("silentshift")\n'
            'if \'$isobject(module) halt\nwrite "SS_MODULE_VERSION=",module.VersionString,!\n'
            'if module.VersionString\'='+literal(args.version)+' halt\nwrite "SS_VERSION_OK",!',
            '16-version',marker='SS_VERSION_OK')
        if args.source=='load':
            cli('package silentshift -path '+base+'/export/','17-package')
            run([*docker,'cp',args.container+':'+base+'/export.tgz',str(output/('silentshift-'+args.version+'.tgz'))],'18-export')
        run([*docker,'cp',str(verification['tests']),args.container+':'+base+'/tests'],'19-tests')
        print('Starting the installed native production ('+args.execution_mode+')...',flush=True)
        if args.source=='public-registry':
            run([*docker,'network','disconnect','bridge',args.container],'20-disconnect-egress')
            run([*docker,'network','connect','none',args.container],'21-isolate-before-activation')
        activate(args,output,runtime,docker,session,run)
        # Adapter iterator checks need a real, isolated inbox even when polling is disabled.
        run([*docker,'exec','--user','0',args.container,'mkdir','-p','/var/opt/silentshift/partner-inbox'],'23-test-inbox')
        run([*docker,'exec','--user','0',args.container,'chown','51773:51773','/var/opt/silentshift/partner-inbox'],'24-inbox-owner')
        run([*docker,'exec',args.container,'chmod','700','/var/opt/silentshift/partner-inbox'],'25-inbox-mode')
        phase='unit tests'
        print('Running the full native %UnitTest suite...',flush=True)
        unit=session('set ^UnitTestRoot='+literal(base+'/tests/')+'\n'
            'set manager=##class(%UnitTest.Manager).%New()\n'
            'set passed=manager.RunTest("","/nodelete")\n'
            'write "SS_UNIT_RESULT=",passed,!\n'
            'if \'passed halt\nwrite "SS_UNIT_OK",!','26-unit-tests',marker='SS_UNIT_OK')
        required_classes=('AdapterChecks','ProviderChecks','ReplayChecks','RuntimeChecks','TraceChecks')
        if ('**FAILED**' in unit or 'Some tests FAILED' in unit
                or not all('SilentShift.Test.'+name+' passed' in unit for name in required_classes)):
            raise RuntimeError('Native test assertions failed; runner status alone is not test success')
        child={**os.environ,**runtime}
        replay=None; native_five=None; preparation=None
        if args.execution_mode == 'recorded-replay':
            phase='recorded playback'
            print('Running the no-key synthetic playback example...',flush=True)
            run([os.sys.executable,str(verification['trace']),'--api',
                f'http://127.0.0.1:{args.api_port}/silentshift/api','--context',args.context,
                '--container',args.container,'--output',str(output/'replay.json')],
                '27-replay',env=child,timeout=300)
            replay=json.loads((output/'replay.json').read_text())
        else:
            phase='local embedding and SDK diagnostic'
            run([*docker,'exec',args.container,'mkdir','-p',RELEASE],'27-diagnostic-directory')
            preparation=prepare_native(output,args.container,docker,session,run)
            phase='five live local investigations'
            print('Running five real local Ollama investigations...',flush=True)
            run([os.sys.executable,str(ROOT/'scripts/verify_native.py'),'--api',
                f'http://127.0.0.1:{args.api_port}/silentshift/api','--allow-model-calls',
                '--output',str(output/'native-five.json')],'28-native-five',env=child,timeout=1500)
            native_five=json.loads((output/'native-five.json').read_text())
            if not native_five.get('passed') or not native_five.get('native_verified') or len(native_five.get('checks',[])) != 5:
                raise RuntimeError('Live native verification did not pass all five cases')
        receipt={**plan,'executed':True,'runtime':re.search(r'SS_RUNTIME=([^\r\n]+)',pristine).group(1),
            'install_command':install_command,'installed_version':args.version,
            'production_started':True,'full_native_unit_suite_passed':True,
            'unit_output':unit,'replay':replay,'native_five':native_five,'live_preparation':preparation,
            'registry_install_verified':args.source=='public-registry',
            'registry_published':args.source=='public-registry','retained_resources':True}
        private_write(output/'receipt.json',json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({'receipt':str(output/'receipt.json'),'source':args.source,
            'version':args.version,'unit_suite_passed':True,
            'replay_passed':replay['passed'] if replay else None,
            'native_five_passed':native_five['passed'] if native_five else None,
            'session_id':replay['session_id'] if replay else None,
            'visual_trace_url':replay['visual_trace_url'] if replay else None}),flush=True)
        return receipt
    except Exception:
        private_write(output/'failure.json',json.dumps({'phase':phase,'retained_resources':True,'existing_runtime_modified':False})+'\n')
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',choices=['load','public-registry'],required=True)
    p.add_argument('--container',required=True)
    p.add_argument('--version',help='Expected version; defaults to source manifest for load, published 0.2.0 for registry')
    p.add_argument('--install-latest',action='store_true',help='Use literal public zpm install silentshift; still require the expected installed version')
    p.add_argument('--execution-mode',choices=['recorded-replay','live'],default='recorded-replay')
    p.add_argument('--allow-model-calls',action='store_true',help='Permit only the configured local Ollama live verification')
    p.add_argument('--context',default='colima-silentshift')
    p.add_argument('--vm-profile',default='silentshift')
    p.add_argument('--network-subnet',help='Optional unused RFC1918 IPv4 /24../28 for the new test network')
    p.add_argument('--verification-source',type=Path,
        help='Registry recorded-replay only: explicit source of native tests and trace assertions; defaults to this checkout')
    p.add_argument('--image',default='silentshift-iris:2026.3.0AI.154.0')
    p.add_argument('--gateway-image',default='containers.intersystems.com/intersystems/webgateway:2026.1')
    p.add_argument('--api-port',type=int,default=52793)
    p.add_argument('--env-file',type=Path,default=ROOT/'.env')
    p.add_argument('--min-host-free-gib',type=float,default=1.8)
    p.add_argument('--min-vm-free-gib',type=float,default=3)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args();a.activate_runtime=True
    a.version = a.version or (module_version(ROOT) if a.source == 'load' else '0.2.0')
    try:result=execute(a)
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as e:p.exit(1,'Verification stopped: '+str(e)+'\n')
    if not a.execute:print(json.dumps(result,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
