from textwrap import dedent, indent

import pytest


@pytest.mark.parametrize(
    "pyfile, expect_passed",
    [
        (
            """
            @pytest.mark.kwparametrize(
                dict(myparam=1),
                myparam=...,
            )
            def test_one_case_one_param_with_default_required(myparam):
                assert myparam == 1
            """,
            1,
        ),
        (
            """
            @pytest.mark.kwparametrize(dict(myparam=1))
            def test_one_case_one_param_no_default(myparam):
                assert myparam == 1
            """,
            1,
        ),
        (
            """
            @pytest.mark.kwparametrize(
                dict(myparam=1),
                dict(myparam=2),
                myparam=...,
                yourparam=42,
            )
            def test_two_cases_two_params_default_and_required(myparam, yourparam):
                assert myparam in [1, 2]
                assert yourparam == 42
            """,
            2,
        ),
        (
            """
            @pytest.mark.kwparametrize(
                dict(myparam=1, yourparam=42),
                dict(myparam=2, yourparam=43),
            )
            def test_two_cases_two_params_no_defaults(myparam, yourparam):
                assert myparam in [1, 2]
                assert yourparam in [42, 43]
            """,
            2,
        ),
        (
            """
            @pytest.mark.kwparametrize(
                dict(myparam=1),
                dict(myparam=2),
                ids=["first case", "second case"],
            )
            def test_pytest_kwargs(myparam):
                assert myparam in [1, 2]
            """,
            2,
        ),
        (
            """
            from pytest import LogCaptureFixture

            @pytest.mark.kwparametrize(dict(myparam=1))
            def test_fixture(caplog, myparam):
                assert myparam == 1
                assert isinstance(caplog, LogCaptureFixture)
            """,
            1,
        ),
    ],
)
def test_mark_kwparametrize(testdir, pyfile, expect_passed):
    testdir.makepyfile(f"import pytest\n" f"{dedent(pyfile)}")
    result = testdir.runpytest()
    try:
        result.assert_outcomes(passed=expect_passed)
    except AssertionError:
        test_output = indent(result.stdout.str(), "> ", lambda _: True)
        print(f"\n\n{test_output}\n")  # for debugging the test
        raise
    result.assert_outcomes(passed=expect_passed)
