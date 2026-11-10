import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('heldout_metrics',Path(__file__).parents[1]/'scripts/heldout_metrics.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def case(truth):
    return {'id':'example','category':'clean','ground_truth':{'decision':truth}}


def test_invalid_and_review_stay_in_false_hold_denominator():
    rows=[m.score_row(case('ALLOW'),'INVALID'),m.score_row(case('ALLOW'),'REQUEST_REVIEW')]
    s=m.summarize(rows)
    assert (s['n'],s['correct'],s['false_holds'],s['allow_eligible'],s['reviews'],s['invalid'])==(2,0,2,2,1,1)
    assert s['review_rate']==0.5


def test_raw_allow_and_actual_simulator_effect_are_separate():
    c=case('REQUEST_REVIEW')
    assert m.score_row(c,'ALLOW')['wrong_delivery']
    no_effect=m.score_row(c,'ALLOW',delivery_count=0)
    assert not no_effect['wrong_delivery'] and no_effect['route_effect_discrepancy']
    assert m.score_row(c,'ALLOW',delivery_count=1)['wrong_delivery']
    assert not m.score_row(case('ALLOW'),'ALLOW',delivery_count=1)['wrong_delivery']


def test_raw_recommendation_keeps_attempted_output_on_failed_tool_validation():
    r={'agent':{'status':'failed','raw_response':'{"decision":"ALLOW"}'},'recommendation':None}
    assert m.raw_proposal(r)=='ALLOW'
    assert m.raw_proposal({'recommendation':'{broken'})=='INVALID'
    assert m.raw_proposal({'recommendation':{'decision':[]}})=='INVALID'
    assert m.raw_proposal({'recommendation':'{"decision":"QUARANTINE","decision":"ALLOW"}'})=='INVALID'
    assert m.raw_proposal({'recommendation':'{"decision":"ALLOW","uncertainty":NaN}'})=='INVALID'


def test_median_does_not_fill_missing_timings_with_zero():
    rows=[m.score_row(case('ALLOW'),'ALLOW',elapsed_ms=v) for v in [None,1,10,100]]
    s=m.summarize(rows)
    assert s['n']==4 and s['timing_observations']==3 and s['median_elapsed_ms']==10
