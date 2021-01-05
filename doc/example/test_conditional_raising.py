# content of test_conditional_raising.py
try:
    from contextlib import nullcontext as does_not_raise
except ImportError:
    # Python <3.7
    from contextlib import suppress as does_not_raise

import pytest


@pytest.mark.kwparametrize(
    dict(example_input=3),
    dict(example_input=2),
    dict(example_input=1),
    dict(example_input=0, expectation=lambda: pytest.raises(ZeroDivisionError)),
    defaults=dict(expectation=does_not_raise),
)
def test_division(example_input, expectation):
    """Test how much I know division."""
    with expectation():
        assert (6 / example_input) is not None
