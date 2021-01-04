# content of test_indirect.py
import pytest


@pytest.fixture
def fixt(request):
    return request.param * 3


@pytest.mark.kwparametrize([dict(fixt="a"), dict(fixt="b")], indirect=True)
def test_indirect(fixt):
    assert len(fixt) == 3
