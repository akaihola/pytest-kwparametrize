# content of test_combinations.py
import pytest


@pytest.mark.kwparametrize(dict(x=0), dict(x=1))
@pytest.mark.kwparametrize(dict(y=2), dict(y=3))
def test_foo(x, y):
    pass
