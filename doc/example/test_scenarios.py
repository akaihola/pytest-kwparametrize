# content of test_scenarios.py
from pytest_kwparametrize.plugin import kwparametrize


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for id_, scenario in metafunc.cls.scenarios:
        idlist.append(id_)
        argvalues.append(scenario)
    kwparametrize(metafunc, *argvalues, ids=idlist, scope="class")


scenario1 = ("basic", {"attribute": "value"})
scenario2 = ("advanced", {"attribute": "value2"})


class TestSampleWithScenarios:
    scenarios = [scenario1, scenario2]

    def test_demo1(self, attribute):
        assert isinstance(attribute, str)

    def test_demo2(self, attribute):
        assert isinstance(attribute, str)
