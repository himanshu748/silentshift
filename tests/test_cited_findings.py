"""Citation provenance grants containment only, never release authority."""
import ast
import copy
import inspect
import json
import subprocess
from pathlib import Path

import pytest
from silentshift.engine import assess, assess_json, policy_json, rule_only, validate_policy

ROOT = Path(__file__).resolve().parents[1]


def sample():
    c = copy.deepcopy(json.loads((ROOT/'fixtures/v1/scenarios.json').read_text())['scenarios'][0])
    c['message'].update(unit='EA', quantity='240')
    c['references'][0]['dispatch_terms'] = {'body': 'The signed dispatch authorization is withdrawn until further notice.'}
    return c


def proposal(c, decision='QUARANTINE'):
    a = assess(c['message'], c['references'], '2026-11-02T12:00:00Z')
    return a, {'decision': decision, 'evidence_ids': a['evidence_ids'], 'explanation': 'Current dispatch authorization is withdrawn.', 'uncertainty': .1,
               'cited_findings': [{'reference_id': c['references'][0]['id'], 'path': '/dispatch_terms/body',
                                  'quote': 'dispatch authorization is withdrawn until further notice.'}]}


def test_grounded_prose_concern_can_quarantine_a_structured_clear_order():
    c=sample(); a,r=proposal(c)
    assert rule_only(a)=='ALLOW'
    old={k:v for k,v in r.items() if k!='cited_findings'}
    assert validate_policy(a,old)['decision']=='REQUEST_REVIEW'
    result=validate_policy(a,r,evidence_context=c)
    assert result['decision']=='QUARANTINE' and not result['downstream_permitted']
    assert any('not a verified deterministic' in reason for reason in result['reasons'])


@pytest.mark.parametrize('change', ['altered_quote','unknown_id','wrong_contract','peer','metadata','bad_pointer','no_context','expired','nontext','missing_path'])
def test_unverifiable_citations_cannot_be_grounded(change):
    c=sample(); a,r=proposal(c); f=r['cited_findings'][0]
    if change=='altered_quote': f['quote']='This fabricated phrase does not occur.'
    if change=='unknown_id': f['reference_id']='foreign:reference'
    if change=='wrong_contract': c['references'][0]['contract_id']='ANOTHER-PO'
    if change=='peer': c['references'][0]['authority']='peer'
    if change=='metadata': f.update(path='/id',quote=c['references'][0]['id'])
    if change=='bad_pointer': f['path']='/dispatch_terms/~2body'
    if change=='expired': a['active_reference_ids']=[]
    if change=='nontext': c['references'][0]['dispatch_terms']['body']=123
    if change=='missing_path': f['path']='/not_present'
    context=None if change=='no_context' else c
    result=validate_policy(a,r,evidence_context=context)
    assert result['decision']=='REQUEST_REVIEW' and not result['downstream_permitted']


@pytest.mark.parametrize('findings',[None,{},[{}],[{'reference_id':'x','path':'/text','quote':'short'}],[]*0])
def test_missing_or_malformed_findings_never_grant_containment(findings):
    c=sample(); a,r=proposal(c);r['cited_findings']=findings
    assert validate_policy(a,r,evidence_context=c)['decision']=='REQUEST_REVIEW'


def test_citation_never_releases_a_rule_hold():
    c=sample();c['message']['quantity']='241';a,r=proposal(c,'ALLOW')
    assert rule_only(a)=='QUARANTINE'
    assert validate_policy(a,r,evidence_context=c)['decision']=='QUARANTINE'
    c['references']=[];a,r=proposal(sample(),'ALLOW');a=assess(c['message'],[],'2026-11-02T12:00:00Z')
    r['evidence_ids']=[]
    assert rule_only(a)=='REQUEST_REVIEW'
    assert not validate_policy(a,r,evidence_context=c)['downstream_permitted']


def test_allow_with_a_concern_and_high_uncertainty_remains_review():
    c=sample();a,r=proposal(c,'ALLOW')
    assert validate_policy(a,r,evidence_context=c)['decision']=='REQUEST_REVIEW'
    r['decision']='QUARANTINE';r['uncertainty']=.9
    assert validate_policy(a,r,evidence_context=c)['decision']=='REQUEST_REVIEW'


def test_bridge_json_and_legacy_replay_remain_compatible():
    c=sample();a,r=proposal(c)
    assert json.loads(policy_json(json.dumps(a),json.dumps(r),evidence_context_json=json.dumps(c)))['decision']=='QUARANTINE'
    r.pop('cited_findings');r['decision']='ALLOW'
    assert json.loads(policy_json(json.dumps(a),json.dumps(r)))['downstream_permitted']


def test_deterministic_baseline_source_has_not_changed():
    frozen=subprocess.check_output(['git','show','d1d752c:python/silentshift/engine.py'],cwd=ROOT,text=True)
    current=(ROOT/'python/silentshift/engine.py').read_text()
    def functions(text):
        return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    for name in ('assess','assess_json','rule_only'):
        assert functions(frozen)[name]==functions(current)[name]
