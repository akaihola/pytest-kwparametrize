# content of test_parametrize.py
import pytest


class TestClass:
    params_equals = [dict(a=1, b=2, marks=[pytest.mark.xfail]), dict(a=3, b=3)]
    params_zerodivision = [dict(a=1, b=0)]

    @pytest.mark.kwparametrize(params_equals)
    def test_equals(self, a, b):
        assert a == b

    @pytest.mark.kwparametrize(params_zerodivision)
    def test_zerodivision(self, a, b):
        with pytest.raises(ZeroDivisionError):
            a / b
