# content of test_pytest_param_example.py
import pytest


@pytest.mark.kwparametrize(
    dict(test_input="3+5", expected=8),
    dict(test_input="1+7", expected=8, marks=pytest.mark.basic),
    dict(test_input="2+4", expected=6, marks=pytest.mark.basic, id="basic_2+4"),
    dict(
        test_input="6*9",
        expected=42,
        marks=[pytest.mark.basic, pytest.mark.xfail],
        id="basic_6*9",
    ),
)
def test_eval(test_input, expected):
    assert eval(test_input) == expected
