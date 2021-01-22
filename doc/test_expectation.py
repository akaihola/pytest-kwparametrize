# content of test_expectation.py
import pytest


@pytest.mark.kwparametrize(
    dict(test_input="3+5", expected=8),
    dict(test_input="2+4", expected=6),
    dict(test_input="6*9", expected=42, marks=[pytest.mark.xfail]),
)
def test_eval(test_input, expected):
    assert eval(test_input) == expected
