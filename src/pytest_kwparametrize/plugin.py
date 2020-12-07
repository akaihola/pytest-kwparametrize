from inspect import Parameter, signature
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from _pytest.python import Metafunc
from pytest import fail

# Keyword argument names accepted by @pytest.mark.parametrize().
# All other keywords can be used as parameter names for parametrized test cases.
# Fish these from Pytest internals to hope for better forward compatibility.
_pytest_mark_parametrize_params = signature(Metafunc.parametrize).parameters
_pytest_mark_parametrize_kw_params = [
    param_name
    for param_name, param in _pytest_mark_parametrize_params.items()
    if param.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
]
PARAMETRIZE_KEYWORDS = _pytest_mark_parametrize_kw_params[3:]
# In Pytest 6.1.2: ["indirect", "ids", "scope", "_param_mark"]


def _get_param(
    name: str, params: Dict[str, Any], defaults: Dict[str, Any], metafunc: Metafunc
):
    if name in params:
        return params[name]
    if defaults[name] is ...:
        fail(
            f"In {metafunc.function.__name__}: The '{name}' parameter was omitted in a "
            f"@kwparametrize test case but marked as required",
            pytrace=False,
        )
    return defaults[name]


def _has_one_iterable(marker_args: List[Any]):
    return (
        len(marker_args) == 1
        and isinstance(marker_args[0], Iterable)
        and not isinstance(marker_args, Mapping)
    )


def _parse_marker_args(marker_args: List[Any]) -> Tuple[List[Any], List[Any]]:
    if _has_one_iterable(marker_args):
        # called like:
        # @pytest.mark.kwparametrize([dict(<case1>), dict(<case2>), ...])
        testcase_dicts, *parametrize_args = marker_args
        return testcase_dicts, parametrize_args
    # called like:
    # @pytest.mark.kwparametrize(dict(<case1>), dict(<case2>), ...)
    return marker_args, []


def _parse_marker_kwargs(kwargs: Dict[str, Any]):
    parametrize_kwargs = {k: v for k, v in kwargs.items() if k in PARAMETRIZE_KEYWORDS}
    defaults = {k: v for k, v in kwargs.items() if k not in PARAMETRIZE_KEYWORDS}
    if set(defaults) == {"defaults"}:
        # called like:
        # @pytest.mark.kwaparametrize(..., defaults=dict(param1=, param2=, ...))
        return parametrize_kwargs, defaults["defaults"]
    # called like:
    # @pytest.mark.kwaparametrize(..., param1=, param2=, ...)
    return parametrize_kwargs, defaults


def _fail_if_unknown_params(
    params: Dict[str, Any], defaults: Dict[str, Any], metafunc: Metafunc
) -> None:
    unknown_params = set(params).difference(defaults)
    if unknown_params:
        fail(
            f"In {metafunc.function.__name__}: Unknown parameter(s) {unknown_params}",
            pytrace=False,
        )


def _param_dicts_to_tuples(
    testcase_dicts: List[Dict[str, Any]], defaults: Dict[str, Any], metafunc: Metafunc
) -> List[Tuple[Any]]:
    argvalues = []
    for params in testcase_dicts:
        _fail_if_unknown_params(params, defaults, metafunc)
        param_values = (
            _get_param(name, params, defaults, metafunc) for name in defaults
        )
        argvalues.append(tuple(param_values))
    return argvalues


def pytest_generate_tests(metafunc: Metafunc) -> None:
    for marker in metafunc.definition.iter_markers(name="kwparametrize"):
        testcase_dicts, parametrize_args = _parse_marker_args(marker.args)
        parametrize_kwargs, defaults = _parse_marker_kwargs(marker.kwargs)
        testcase_tuples = _param_dicts_to_tuples(testcase_dicts, defaults, metafunc)
        metafunc.parametrize(
            list(defaults),
            testcase_tuples,
            *parametrize_args,
            **parametrize_kwargs,
            _param_mark=marker,
        )
