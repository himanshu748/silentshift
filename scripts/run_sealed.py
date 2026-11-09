#!/usr/bin/env python3
"""Frozen synthetic dev/sealed trials. Opening sealed cases requires explicit execution.

No output repair, label edits, model retries, or main/publication mutations.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import urllib.request

from run_heldout import ROOT, Native, baseline_matches, write_json
from verify_ipm_native import literal

DATASETS = {
    'dev': ('fixtures/v2-heldout/scenarios.json', 'a50a551a92b5f52ba5212a91dca3de0d21f57da5',
            'e02747e587495dd2587a3813277a15451c7715638d9ff9962186a09e8986ef55', 48),
    'sealed': ('fixtures/v3-sealed/scenarios.json', '9c8d9376f08024eb7f5ff05771a5b02a854d6b4f',
               '415489ccebbe21b83ea870c862570eb6acc7bd1a59ea2394fa7f31cd27c962d6', 36),
}
MODEL = 'qwen3-silentshift:4b-instruct'
PROMPT = 'silentshift-investigator/1.4.2'


def frozen(name):
    path, commit, sha, n = DATASETS[name]
    raw = (ROOT/path).read_bytes()
    original = subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)
    if raw != original or hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('Frozen inputs/labels changed')
    data = json.loads(raw)
    if len(data['scenarios']) != n: raise ValueError('Dataset size mismatch')
    return data


def source_identity(commit):
    files = subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'src','python'],cwd=ROOT,text=True).splitlines()
    result={}
    for path in files:
        raw=(ROOT/path).read_bytes()
        if raw != subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT):
            raise ValueError('Runtime differs from pinned source: '+path)
        result[path]=hashlib.sha256(raw).hexdigest()
    return result


def isolate_precedents(native):
    """Operator-only production configuration; retrieval and routing stay real."""
    native.copy(ROOT/'tests/iris/HeldoutPrecedents.cls','/home/irisowner/silentshift-bonus/HeldoutPrecedents.cls')
    original=(ROOT/'src/SilentShift/Production.cls').read_text()
    old='ClassName="SilentShift.Operation.Precedents"'
    if original.count(old)!=1: raise ValueError('Unexpected production definition')
    modified=original.replace(old,'ClassName="SilentShift.Test.HeldoutPrecedents"')
    path=ROOT/'.local/heldout/HeldoutProduction.cls';path.write_text(modified)
    native.copy(path,'/home/irisowner/silentshift-bonus/HeldoutProduction.cls')
    result=native.shell('set sc=##class(Ens.Director).StopProduction()\n'
        'if $system.Status.IsError(sc) halt\n'
        'set sc=$system.OBJ.Load("/home/irisowner/silentshift-bonus/HeldoutPrecedents.cls","ck")\n'
        'if $system.Status.IsError(sc) halt\n'
        'set sc=$system.OBJ.Load("/home/irisowner/silentshift-bonus/HeldoutProduction.cls","ck")\n'
        'if $system.Status.IsError(sc) halt\n'
        'set sc=##class(Ens.Director).StartProduction("SilentShift.Production")\n'
        'if $system.Status.IsError(sc) halt\n'
        'write "HELDOUT=",{"isolated":true}.%ToJSON(),!')
    if not result['isolated']: raise ValueError('Evaluation isolation failed')
    return {'scope':'evaluation-only no-learning host substitution; native retrieval unchanged',
            'production_source_sha256':hashlib.sha256(original.encode()).hexdigest(),
            'evaluation_production_sha256':hashlib.sha256(modified.encode()).hexdigest(),
            'substitution':'Precedents host -> SilentShift.Test.HeldoutPrecedents; index_precedent returns skipped'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',choices=DATASETS,required=True)
    p.add_argument('--execute',action='store_true')
    p.add_argument('--open-sealed',action='store_true')
    p.add_argument('--source-commit',required=True)
    p.add_argument('--container',default='silentshift-bonus-load-prose-v3-nov9')
    p.add_argument('--context',default='colima-silentshift')
    p.add_argument('--env-file',type=Path,default=ROOT/'.env')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if not a.execute or (a.dataset=='sealed' and not a.open_sealed):
        print('No case file opened. Explicit execution/open-sealed required.'); return 0
    inventory=source_identity(a.source_commit)
    opened_at=datetime.now(timezone.utc).isoformat()
    dataset=frozen(a.dataset)
    path,label_commit,data_sha,n=DATASETS[a.dataset]
    out=a.output;out.mkdir(parents=True,exist_ok=True)
    (ROOT/'.local/heldout').mkdir(parents=True,exist_ok=True)
    native=Native(a)
    target='/home/irisowner/silentshift-bonus/HeldoutEval.cls'
    native.copy(ROOT/'tests/iris/HeldoutEval.cls',target)
    result=native.shell('set sc=$system.OBJ.Load('+literal(target)+',"ck")\nwrite "HELDOUT=",{"compiled":($system.Status.IsOK(sc))}.%ToJSON(),!')
    if not result['compiled']:raise RuntimeError('Evaluation helper did not compile')
    identity=native.call('Identity')
    with urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=10) as response:
        models=json.load(response)['models']
    digest=next((m['digest'] for m in models if m['name']==MODEL),None)
    if digest!='30edee6daf42d36a77e6bdd225b2be0098021122827523f13035751575a66d35':
        raise ValueError('Local release model digest changed')
    identity['ollama_model_digest']=digest
    if ('Build 154U' not in identity['runtime'] or 'ARM64' not in identity['runtime']
            or identity['execution_mode']!='live' or identity['model']!=MODEL
            or identity['prompt_version']!=PROMPT or identity['assets']['engine_sha256']!=inventory['python/silentshift/engine.py']):
        raise ValueError('Native runtime/model/source identity mismatch')
    manifest_path=out/'manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        if manifest['dataset_sha256']!=data_sha or manifest['identity']!=identity or manifest['source_inventory']!=inventory:
            raise ValueError('Cannot resume changed inputs/runtime/source')
    else:
        isolation=isolate_precedents(native)
        manifest={'created_at':datetime.now(timezone.utc).isoformat(),'run_id':str(uuid.uuid4()),
            'dataset':a.dataset,'case_file_opened_at':opened_at,'dataset_sha256':data_sha,'labels_commit':label_commit,
            'source_commit':a.source_commit,'source_inventory':inventory,'identity':identity,
            'planned':n*3,'completed':0,'status':'running','synthetic':True,
            'protocol':'3 baseline executions and 3 fresh native agent+policy investigations per case; no selective retries',
            'isolation':isolation,'delivery_target':'IRIS simulator only'}
        stripped={'clock':dataset['clock'],'dataset_version':dataset['dataset_version'],
            'scenarios':[{k:c[k] for k in ('id','message','references')} for c in dataset['scenarios']]}
        payload=ROOT/'.local/heldout'/('input-'+a.dataset+'.json');write_json(payload,stripped)
        native.copy(payload,'/home/irisowner/silentshift-bonus/eval-input.json')
        result=native.call('Initialize','/home/irisowner/silentshift-bonus/eval-input.json',manifest['run_id'])
        if result['cases']!=n:raise ValueError('Input count mismatch')
        manifest['native_input_sha256']=hashlib.sha256(payload.read_bytes()).hexdigest()
        write_json(manifest_path,manifest)
    run=manifest['run_id']
    for trial in range(1,4):
        rules_file=out/f'rules-trial-{trial}.json'
        if not rules_file.exists():
            rows=[native.call('Rules',run,c['id']) for c in dataset['scenarios']]
            write_json(rules_file,{'trial':trial,'run_id':run,'source_commit':a.source_commit,'dataset_sha256':data_sha,'cases':rows,'timing_scope':'assess + unchanged rule_only in IRIS Embedded Python, excludes terminal/session overhead'})
            print(f'{a.dataset} rules trial {trial}: {len(rows)} executions',flush=True)
    for trial in range(1,4):
        directory=out/f'trial-{trial}';directory.mkdir(exist_ok=True)
        for case in dataset['scenarios']:
            if shutil.disk_usage(ROOT).free<1.8*1024**3:
                manifest.update(status='paused-infrastructure',reason='host below unchanged disk floor')
                write_json(manifest_path,manifest);raise RuntimeError('Disk floor reached; retained checkpoint')
            dest=directory/(case['id']+'.json')
            if dest.exists():
                prior_result=json.loads(dest.read_text())
                if prior_result['run_id']!=run or prior_result['scenario_id']!=case['id'] or prior_result['trial']!=trial or prior_result['dataset_sha256']!=data_sha:
                    raise ValueError('Existing checkpoint belongs to another execution')
                continue
            source_identity(a.source_commit)
            began=time.monotonic();prior=native.call('Read',run,case['id'],trial)
            observed=prior if prior['exists'] else native.call('Run',run,case['id'],trial)
            if not observed.get('exists'):
                write_json(directory/(case['id']+'-incomplete.json'),observed)
                raise RuntimeError('No persisted case; no redispatch permitted')
            record=observed['record']
            for _ in range(60):
                if record['routing']!='PROCESSING':break
                time.sleep(1);observed=native.call('Read',run,case['id'],trial);record=observed['record']
            if record['routing']=='PROCESSING' or not baseline_matches(record,case):
                write_json(directory/(case['id']+'-incomplete.json'),observed)
                raise RuntimeError('Unresolved case or mismatched frozen inputs; checkpoint retained')
            export=native.shell('write "HELDOUT=",##class(SilentShift.Test.ProviderChecks).InspectCase('+literal(record['id'])+'),!')
            write_json(dest,{'scenario_id':case['id'],'trial':trial,'run_id':run,'dataset_sha256':data_sha,
                'case_id':record['id'],'trace_id':record['trace_id'],'service_elapsed_ms':observed.get('service_elapsed_ms'),
                'harness_elapsed_ms':round((time.monotonic()-began)*1000,3),'record':record,'provider_export':export,
                'semantic_inputs_match_frozen':True,'resumed_existing_case':prior['exists']})
            manifest['completed']=sum((out/f'trial-{t}'/(c['id']+'.json')).exists() for t in range(1,4) for c in dataset['scenarios'])
            write_json(manifest_path,manifest)
            print(f"{a.dataset} trial={trial} {case['id']} trace={record['trace_id']} route={record['routing']} status={(record.get('agent') or {}).get('status')} {manifest['completed']}/{n*3}",flush=True)
    audit=native.shell('set s=##class(%SQL.Statement).%New()\n'
        'set sc=s.%Prepare("SELECT COUNT(*) AS N FROM SilentShift_Data.Precedent WHERE SourceScope LIKE ?")\n'
        'if $system.Status.IsError(sc) halt\n'
        'set r=s.%Execute('+literal('heldout:'+run+':%')+')\n'
        'if r.%SQLCODE<0 halt\n'
        'if \'r.%Next() halt\n'
        'write "HELDOUT=",{"evaluated_outcomes_in_precedent_index":(r.%Get("N"))}.%ToJSON(),!')
    if audit['evaluated_outcomes_in_precedent_index']!=0:
        raise RuntimeError('Evaluation outcomes leaked into the precedent corpus')
    manifest['learning_audit']=audit
    manifest.update(status='completed',finished_at=datetime.now(timezone.utc).isoformat())
    write_json(manifest_path,manifest)
    return 0


if __name__=='__main__':raise SystemExit(main())
