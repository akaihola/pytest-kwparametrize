# content of test_backends.py
import pytest


@pytest.mark.xfail
def test_db_initialized(db):
    # a dummy test
    if db.__class__.__name__ == "DB2":
        pytest.fail("deliberately failing for demo purposes")
