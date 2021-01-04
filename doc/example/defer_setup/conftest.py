# content of conftest.py
import pytest

from pytest_kwparametrize.plugin import kwparametrize


def pytest_generate_tests(metafunc):
    if "db" in metafunc.fixturenames:
        kwparametrize(metafunc, [dict(db="d1"), dict(db="d2")], indirect=True)


class DB1:
    """one database object"""


class DB2:
    """alternative database object"""


@pytest.fixture
def db(request):
    if request.param == "d1":
        return DB1()
    elif request.param == "d2":
        return DB2()
    else:
        raise ValueError("invalid internal test config")
