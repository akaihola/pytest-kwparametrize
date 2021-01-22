# content of test_time.py
from datetime import datetime, timedelta

import pytest

testdata = [
    dict(a=datetime(2001, 12, 12), b=datetime(2001, 12, 11), expected=timedelta(1)),
    dict(a=datetime(2001, 12, 11), b=datetime(2001, 12, 12), expected=timedelta(-1)),
]


@pytest.mark.kwparametrize(testdata)
def test_timedistance_v0(a, b, expected):
    diff = a - b
    assert diff == expected


@pytest.mark.kwparametrize(testdata, ids=["forward", "backward"])
def test_timedistance_v1(a, b, expected):
    diff = a - b
    assert diff == expected


def idfn(val):
    if isinstance(val, (datetime,)):
        # note this wouldn't show any hours/minutes/seconds
        return val.strftime("%Y%m%d")


@pytest.mark.kwparametrize(testdata, ids=idfn)
def test_timedistance_v2(a, b, expected):
    diff = a - b
    assert diff == expected


@pytest.mark.kwparametrize(
    dict(
        a=datetime(2001, 12, 12),
        b=datetime(2001, 12, 11),
        expected=timedelta(1),
        id="forward",
    ),
    dict(
        a=datetime(2001, 12, 11),
        b=datetime(2001, 12, 12),
        expected=timedelta(-1),
        id="backward",
    ),
)
def test_timedistance_v3(a, b, expected):
    diff = a - b
    assert diff == expected
