#!/usr/bin/env python3
"""Operator-only installer for the explicitly approved, timed ARM demo host.

Run as root in a private /opt/silentshift-demo bundle after the termination timer
is active. Never publishes images or packages; never creates AWS resources.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import time
import urllib.request

IMAGE = 'sha256:8fa0ae85777d11ef113ec25a7ac2d1548edfa321a31bcbfa3e0a01ea7dbd8713'
OLLAMA_SHA = '47c82a67e59e060a735d1cb50a2acf020126a3a4be3f6847d5b58b7dd59620b6'


def write(path, value, mode=0o600):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value);path.chmod(mode)


def execute(root):
    if os.geteuid()!=0: raise ValueError('Root operator required')
    if subprocess.run(['systemctl','is-active','--quiet','silentshift-expiry.timer']).returncode:
        raise ValueError('Install and verify the four-hour termination timer first')
    os.chdir(root)
    config=json.loads(Path('deployment-private.json').read_text())
    expiry=float(config['expires_at'])
    if not time.time()<expiry<=time.time()+4*3600:raise ValueError('Trial expiry must be within four hours')
    def run(args, *, data=None, timeout=1200):
        r=subprocess.run(args,input=data,text=True,capture_output=True,timeout=timeout)
        log=Path('operator-install.log')
        with log.open('a') as f:f.write(r.stdout+r.stderr)
        log.chmod(0o600)
        if r.returncode:raise RuntimeError('Installation stage failed: '+args[0]+'; private log retained')
        return r.stdout
    def session(script,namespace='SILENTSHIFT',marker='SS_STAGE_OK'):
        result=run(['docker','exec','-i','silentshift-demo-native','iris','session','IRIS','-U',namespace],data=script+'\nhalt\n')
        if marker not in result.splitlines():raise RuntimeError('Native marker missing; private log retained')
        return result
    def cli(command):
        return session('set sc=##class(%IPM.Main).Shell('+json.dumps(command)+')\nif $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nwrite "SS_STAGE_OK",!')
    print('Installing official Ubuntu packages',flush=True)
    run(['apt-get','update'])
    run(['apt-get','install','-y','docker.io','caddy','zstd','curl'])
    run(['systemctl','enable','--now','docker'])
    # Keep HTTP closed until the native boundary passes. Caddy has no app config yet.
    run(['systemctl','stop','caddy'])
    bundles=json.loads(Path('bundles.json').read_text())
    for name, record in bundles.items():
        h=hashlib.sha256()
        with open(name,'rb') as f:
            while b:=f.read(8*1024*1024):h.update(b)
        if h.hexdigest()!=record['sha256']:raise ValueError('Transferred bundle hash differs')
    print('Loading retained official ARM image without a registry',flush=True)
    run(['docker','load','-i','iris154-arm64.tar.gz'])
    identity=json.loads(run(['docker','image','inspect',IMAGE]))[0]
    if identity['Architecture']!='arm64' or identity['Config']['Labels'].get('com.intersystems.platform-version')!='2026.3.0AI.154.0com':raise ValueError('Wrong runtime')
    print('Installing pinned official Ollama and exact local models',flush=True)
    binary=Path('ollama-linux-arm64.tar.zst')
    if not binary.exists():
        run(['curl','--fail','--location','--silent','--show-error','--output',str(binary),'https://github.com/ollama/ollama/releases/download/v0.31.1/ollama-linux-arm64.tar.zst'])
    h=hashlib.sha256()
    with binary.open('rb') as f:
        while b:=f.read(8*1024*1024):h.update(b)
    if h.hexdigest()!=OLLAMA_SHA:raise ValueError('Official Ollama asset digest differs')
    run(['tar','--use-compress-program=unzstd','-xf',str(binary),'-C','/usr'])
    run(['useradd','--system','--home-dir','/var/lib/ollama','--shell','/usr/sbin/nologin','ollama'])
    Path('/var/lib/ollama/models').mkdir(parents=True)
    run(['tar','-xzf','ollama-models.tar.gz','-C','/var/lib/ollama/models'])
    manifests=json.loads(Path('model-identity.json').read_text())['manifest_sha256']
    for name, digest in manifests.items():
        if hashlib.sha256((Path('/var/lib/ollama/models')/name).read_bytes()).hexdigest()!=digest:raise ValueError('Model manifest differs')
    run(['chown','-R','ollama:ollama','/var/lib/ollama'])
    write('/etc/systemd/system/ollama.service','''[Unit]
Description=SilentShift local model (private Docker interface)
After=docker.service
Requires=docker.service
[Service]
User=ollama
Group=ollama
Environment=OLLAMA_HOST=172.17.0.1:11434
Environment=OLLAMA_MODELS=/var/lib/ollama/models
Environment=OLLAMA_NUM_PARALLEL=1
Environment=OLLAMA_MAX_LOADED_MODELS=2
Environment=OLLAMA_KEEP_ALIVE=30m
ExecStart=/usr/bin/ollama serve
Restart=on-failure
[Install]
WantedBy=multi-user.target
''',0o644)
    run(['systemctl','daemon-reload']);run(['systemctl','enable','--now','ollama'])
    print('Installing current native source, no application source mounts',flush=True)
    stage=Path('stage');stage.mkdir()
    with tarfile.open('silentshift-0.3.0.tgz') as archive:archive.extractall(stage,filter='data')
    run(['docker','network','create','--label','project=silentshift','silentshift-demo'])
    run(['docker','run','-d','--init','--name','silentshift-demo-native','--hostname','silentshift-demo-native','--network','silentshift-demo','--network-alias','iris','--add-host','host.docker.internal:host-gateway','--memory','3g','--cpus','1.5','--shm-size','256m','--env-file',str(root/'runtime.env'),'--log-opt','max-size=10m','--log-opt','max-file=2',IMAGE])
    for _ in range(120):
        r=subprocess.run(['docker','exec','-i','silentshift-demo-native','iris','session','IRIS','-U','%SYS'],input='write "SS_READY",!\nhalt\n',text=True,capture_output=True)
        if r.returncode==0 and 'SS_READY' in r.stdout.splitlines():break
        time.sleep(1)
    else:raise RuntimeError('IRIS not ready')
    base='/home/irisowner/silentshift-demo'
    run(['docker','exec','silentshift-demo-native','mkdir','-p',base])
    for name in ['namespace.cpf','zpm.xml','stage']:
        run(['docker','cp',str(root/name),'silentshift-demo-native:'+base+'/'+name])
    run(['docker','exec','--user','0','silentshift-demo-native','chown','-R','51773:51773',base])
    run(['docker','exec','silentshift-demo-native','iris','merge','IRIS',base+'/namespace.cpf'])
    session('set properties("Enabled")=1\nset sc=##class(Security.Services).Modify("%Service_CallIn",.properties)\nif $system.Status.IsError(sc) halt\nwrite "SS_STAGE_OK",!','%SYS')
    session('set sc=$system.OBJ.Load("'+base+'/zpm.xml","ck")\nif $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nwrite "SS_STAGE_OK",!')
    cli('config set analytics 0');cli('load '+base+'/stage')
    session('set sc=##class(SilentShift.Setup).Install()\nif $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nwrite "SS_RUNTIME=",$zversion,!\nwrite "SS_STAGE_OK",!')
    run(['python3','scripts/configure_demo_reader.py','--container','silentshift-demo-native','--env-file','edge.env','--execute'])
    run(['docker','pull','containers.intersystems.com/intersystems/webgateway:2026.1'])
    run(['docker','run','-d','--init','--name','silentshift-demo-gateway','--network','silentshift-demo','--network-alias','gateway','--publish','127.0.0.1:52773:80','--env','ISC_CSP_CONF_FILE=/private/CSP.conf','--env','ISC_CSP_INI_FILE=/private/CSP.ini','--mount','type=bind,src='+str(root/'CSP.conf')+',dst=/private/CSP.conf,readonly','--mount','type=bind,src='+str(root/'CSP.ini')+',dst=/private/CSP.ini','--log-opt','max-size=10m','--log-opt','max-file=2','containers.intersystems.com/intersystems/webgateway:2026.1'])
    # Deliberately measure amendment embedding separately from the live case.
    session('set sc=##class(SilentShift.Precedents).IndexAmendments(.report)\nif $system.Status.IsError(sc) do $system.Status.DisplayError(sc) halt\nwrite "SS_INDEX=",report,!\nwrite "SS_STAGE_OK",!')
    run(['useradd','--system','--home-dir','/var/lib/silentshift-demo','--shell','/usr/sbin/nologin','silentshift-demo'])
    Path('/var/lib/silentshift-demo').mkdir(parents=True)
    run(['chown','silentshift-demo:silentshift-demo','/var/lib/silentshift-demo'])
    run(['chgrp','silentshift-demo','edge.env']);Path('edge.env').chmod(0o640)
    # Public code/static assets only; root-owned runtime/gateway secrets stay 0600.
    for directory in ['demo_gateway','web']:
        run(['chmod','-R','a+rX',directory])
    root.chmod(0o755)
    write('/etc/systemd/system/silentshift-demo.service','''[Unit]
Description=SilentShift bounded synthetic demo
After=docker.service ollama.service
Requires=ollama.service
[Service]
User=silentshift-demo
Group=silentshift-demo
WorkingDirectory=/opt/silentshift-demo
EnvironmentFile=/opt/silentshift-demo/edge.env
ExecStart=/usr/bin/python3 -m demo_gateway.server
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/silentshift-demo
[Install]
WantedBy=multi-user.target
''',0o644)
    run(['systemctl','daemon-reload']);run(['systemctl','enable','--now','silentshift-demo'])
    # Operator opens public ingress only after checking this loopback service.
    write('caddy-ready.txt',config['origin']+' {\n reverse_proxy 127.0.0.1:8090 {\n  header_up X-Forwarded-For {remote_host}\n }\n}\n',0o644)
    print(json.dumps({'installed':True,'runtime_image':identity['Id'],'architecture':'arm64','public_caddy_started':False,'expires_at':expiry}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--execute',action='store_true',help='Install only on the approved timed host; default prints a plan')
    args=parser.parse_args()
    if args.execute:
        execute(args.bundle.resolve())
    else:
        print(json.dumps({'execute':False,'bundle':str(args.bundle.resolve()),'requires':'Root on approved ARM host with active four-hour expiry timer','publishes_images_or_packages':False}))
