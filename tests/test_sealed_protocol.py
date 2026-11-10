"""Protocol guards without reading sealed case contents."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_sealed


def test_sealed_plan_never_opens_cases(monkeypatch,capsys,tmp_path):
    monkeypatch.setattr(sys,'argv',['run_sealed','--dataset','sealed','--source-commit','HEAD','--output',str(tmp_path)])
    def forbidden(*args):raise AssertionError('Sealed inputs must remain unopened')
    monkeypatch.setattr(run_sealed,'source_identity',forbidden)
    monkeypatch.setattr(run_sealed,'frozen',forbidden)
    assert run_sealed.main()==0
    assert 'No case file opened' in capsys.readouterr().out


def test_execute_without_explicit_sealed_open_does_not_open(monkeypatch,tmp_path):
    monkeypatch.setattr(sys,'argv',['run_sealed','--dataset','sealed','--execute','--source-commit','HEAD','--output',str(tmp_path)])
    monkeypatch.setattr(run_sealed,'frozen',lambda *_: (_ for _ in ()).throw(AssertionError('Unexpected read')))
    assert run_sealed.main()==0


def test_production_override_changes_only_outcome_indexing():
    text=(ROOT/'tests/iris/HeldoutPrecedents.cls').read_text()
    assert 'request.Action = "index_precedent"' in text
    assert 'Return ##super(request,.response)' in text
    assert 'SilentShift.Test.HeldoutPrecedents' not in (ROOT/'src/SilentShift/Production.cls').read_text()
    assert 'Heldout' not in (ROOT/'module.xml').read_text()


def test_label_commits_remain_distinct_from_model_execution_source():
    assert run_sealed.DATASETS['sealed'][1]=='9c8d9376f08024eb7f5ff05771a5b02a854d6b4f'
    assert run_sealed.DATASETS['sealed'][3]==36
    assert run_sealed.DATASETS['dev'][3]==48


def test_resume_retains_completed_attempts_and_frozen_identity():
    import copy
    original={'status':'paused-infrastructure','completed':24,'planned':108,'run_id':'original-run',
              'source_inventory':{'engine':'unchanged'},'dataset_sha256':'unchanged-input',
              'reason':'host below unchanged disk floor'}
    value=copy.deepcopy(original)
    assert run_sealed.resume_checkpoint(value,'recorded-resume-time') is value
    assert value['status']=='running'
    for key in ('completed','planned','run_id','source_inventory','dataset_sha256'):
        assert value[key]==original[key]
    assert value['infrastructure_resumes']==[{'resumed_at':'recorded-resume-time','completed_retained':24,
                                             'pause_reason':'host below unchanged disk floor'}]
    run_sealed.resume_checkpoint(value,'another-check')
    assert len(value['infrastructure_resumes'])==1
