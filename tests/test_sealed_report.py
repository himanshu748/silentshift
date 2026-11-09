"""Tiny fake receipts test accounting; these are not model evaluation results."""
import json
from pathlib import Path
import sys

import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import report_sealed
from run_sealed import DATASETS


def prepare(tmp_path,monkeypatch):
    cases=[{'id':'TOY-A','category':'clean','ground_truth':{'decision':'ALLOW'}},
           {'id':'TOY-B','category':'unstructured','ground_truth':{'decision':'QUARANTINE'}}]
    monkeypatch.setattr(report_sealed,'frozen',lambda _: {'scenarios':cases})
    monkeypatch.setattr(report_sealed,'ROOT',tmp_path)
    source=tmp_path/'evidence';source.mkdir()
    sha=DATASETS['dev'][2]
    manifest={'status':'completed','completed':6,'run_id':'toy','source_commit':'toy-source',
              'labels_commit':'toy-labels','identity':{'runtime':'TOY; not an IRIS run','model':'toy','prompt_version':'toy'}}
    (source/'manifest.json').write_text(json.dumps(manifest))
    for trial in range(1,4):
        (source/f'rules-trial-{trial}.json').write_text(json.dumps({'dataset_sha256':sha,'cases':[
            {'scenario_id':c['id'],'decision':'ALLOW','elapsed_ms':.1} for c in cases]}))
        directory=source/f'trial-{trial}';directory.mkdir()
        for c in cases:
            # Bad order is contained each time; clean order is falsely held in trial 3.
            delivered=c['id']=='TOY-A' and trial!=3
            route='DELIVERED' if delivered else 'QUARANTINED'
            proposal={'decision':'ALLOW' if delivered else 'QUARANTINE','evidence_ids':['r'],
                      'explanation':'Toy assertion only.','uncertainty':0,'cited_findings':[]}
            record={'id':c['id']+str(trial),'trace_id':str(trial),'routing':route,'delivery_count':int(delivered),
                    'assessment':{'evidence_ids':['r']},'policy':{'checks':[]},
                    'agent':{'status':'returned','elapsed_ms':100,'raw_response':json.dumps(proposal)}}
            (directory/(c['id']+'.json')).write_text(json.dumps({'scenario_id':c['id'],'trial':trial,
                'run_id':'toy','dataset_sha256':sha,'semantic_inputs_match_frozen':True,'record':record}))
    return source


def test_all_repetitions_and_false_holds_remain_in_denominators(tmp_path,monkeypatch):
    source=prepare(tmp_path,monkeypatch)
    result=report_sealed.report('dev',source,tmp_path/'report.md')
    assert result['arms']['rules-only']['pooled']['correct']==3
    assert result['arms']['rules-only']['pooled']['wrong_deliveries']==3
    assert result['arms']['agent+policy']['pooled']['correct']==5
    assert result['arms']['agent+policy']['pooled']['false_holds']==1
    text=(tmp_path/'report.md').read_text()
    assert 'TOY-A' in text and 'Rules win' in text
    assert len(result['arms']['agent+policy']['failures'])==1


def test_incomplete_execution_cannot_be_called_complete(tmp_path,monkeypatch):
    source=prepare(tmp_path,monkeypatch)
    path=source/'manifest.json';m=json.loads(path.read_text());m['completed']=5;path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='every preregistered'):report_sealed.report('dev',source,tmp_path/'report.md')


def test_wrong_run_checkpoint_is_rejected(tmp_path,monkeypatch):
    source=prepare(tmp_path,monkeypatch)
    p=source/'trial-2/TOY-A.json';r=json.loads(p.read_text());r['run_id']='another-run';p.write_text(json.dumps(r))
    with pytest.raises(ValueError,match='identity'):report_sealed.report('dev',source,tmp_path/'report.md')
