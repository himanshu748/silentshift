"""Pure approval/timer checks; these do not establish an EC2 installation."""
import datetime
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.bootstrap_demo_host import validate_trial

START=datetime.datetime(2026,11,9,13,tzinfo=datetime.timezone.utc).timestamp()


def config(hours):
    return {'created_at':'2026-11-09T13:00:00+00:00','approved_hours':hours,'expires_at':START+hours*3600}


@pytest.mark.parametrize('hours',[4,8])
def test_exactly_approved_window_and_matching_absolute_timer(hours):
    value=config(hours)
    assert validate_trial(value,START+60,value['expires_at'])==value['expires_at']


@pytest.mark.parametrize('hours',[0,6,9,24])
def test_other_durations_cannot_be_inferred_from_an_active_timer(hours):
    value=config(hours)
    with pytest.raises(ValueError):validate_trial(value,START+1,value['expires_at'])


def test_longer_expiry_and_later_or_earlier_timer_are_refused():
    value=config(8)
    with pytest.raises(ValueError):validate_trial({**value,'expires_at':value['expires_at']+1},START+1,value['expires_at']+1)
    for delta in [-60,60]:
        with pytest.raises(ValueError):validate_trial(value,START+1,value['expires_at']+delta)


def test_expired_future_start_naive_time_and_nonfinite_expiry_are_refused():
    value=config(8)
    for now in [START-1,value['expires_at'],value['expires_at']+1]:
        with pytest.raises(ValueError):validate_trial(value,now,value['expires_at'])
    with pytest.raises(ValueError):validate_trial({**value,'created_at':'2026-11-09T13:00:00'},START+1,value['expires_at'])
    for expiry in [float('nan'),float('inf')]:
        with pytest.raises(ValueError):validate_trial({**value,'expires_at':expiry},START+1,expiry)
