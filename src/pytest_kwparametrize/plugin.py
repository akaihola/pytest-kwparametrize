"""kwparametrize plugin"""

from inspect import Parameter, signature
from typing import Any, Callable, Dict, Iterable, List, Mapping, Tuple, Union

import pytest
from _pytest.python import Metafunc
from pytest import fail


def get_keyword_parameters(function: Callable) -> List[str]:
    return [
        param_name
        for param_name, param in signature(function).parameters.items()
        if param.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
    ]


# Keyword argument names accepted by @pytest.mark.parametrize().
# These keywords can't be used as parameter names for parametrized test cases.
# Fish these from Pytest internals to hope for better forward compatibility.
# In Pytest 6.1.2: ["indirect", "ids", "scope", "_param_mark"]
PARAMETRIZE_KEYWORDS = set(get_keyword_parameters(Metafunc.parametrize)[3:])

# Keyword argument names accepted by `pytest.param(...)`
# These keywords can't be used as parameter names for parametrized test cases.
# Fish these from Pytest internals to hope for better forward compatibility.
# In Pytest 6.1.2: ["marks", "id"]
PYTEST_PARAM_KEYWORDS = set(get_keyword_parameters(pytest.param))


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
        and not isinstance(marker_args[0], Mapping)
    )


def _parse_marker_args(
    marker_args: Iterable[Union[List[Dict[str, Any]], Dict[str, Any]]]
) -> List[Any]:
    if _has_one_iterable(marker_args):
        # called like:
        # @pytest.mark.kwparametrize([dict(<case1>), dict(<case2>), ...])
        (testcase_dicts,) = marker_args
        return testcase_dicts
    # called like:
    # @pytest.mark.kwparametrize(dict(<case1>), dict(<case2>), ...)
    return marker_args


def _parse_marker_kwargs(kwargs: Dict[str, Any]):
    parametrize_kwargs = {k: v for k, v in kwargs.items() if k in PARAMETRIZE_KEYWORDS}
    defaults = {k: v for k, v in kwargs.items() if k not in PARAMETRIZE_KEYWORDS}
    if set(defaults) == {"defaults"}:
        # called like:
        # @pytest.mark.kwaparametrize(..., defaults=dict(param1=, param2=, ...))
        return defaults["defaults"], parametrize_kwargs
    # called like:
    # @pytest.mark.kwaparametrize(..., param1=, param2=, ...)
    return defaults, parametrize_kwargs


def _param_dicts_to_tuples(
    testcase_dicts: List[Dict[str, Any]], defaults: Dict[str, Any], metafunc: Metafunc
) -> List[Tuple[Any]]:
    argvalues = []
    for params in testcase_dicts:
        param_values = (
            _get_param(name, params, defaults, metafunc) for name in defaults
        )
        param_keywords = {
            keyword: value
            for keyword, value in params.items()
            if keyword in PYTEST_PARAM_KEYWORDS
        }
        argvalues.append(pytest.param(*param_values, **param_keywords))
    return argvalues


def kwparametrize(
    metafunc: Metafunc,
    *args: Union[List[Dict[str, Any]], Dict[str, Any]],
    **kwargs: Any,
) -> None:
    """foo"""
    testcase_dicts = _parse_marker_args(args)
    defaults, parametrize_kwargs = _parse_marker_kwargs(kwargs)
    for params in testcase_dicts:
        for name in params:
            if name not in PYTEST_PARAM_KEYWORDS:
                defaults.setdefault(name, ...)
    testcase_tuples = _param_dicts_to_tuples(testcase_dicts, defaults, metafunc)
    metafunc.parametrize(
        argnames=list(defaults),
        argvalues=testcase_tuples,
        **parametrize_kwargs,
    )


def pytest_generate_tests(metafunc: Metafunc) -> None:
    for marker in metafunc.definition.iter_markers(name="kwparametrize"):
        kwparametrize(metafunc, *marker.args, _param_mark=marker, **marker.kwargs)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "kwparametrize(*argvalues):"
        " call a test function multiple times passing in different arguments in turn."
        " argvalues items need to be dictionaries."
        " Example: @kwparametrize(dict(arg1=1), dict(arg1=2))"
        " would lead to two calls of the decorated test function,"
        " one with arg1=1 and another with arg1=2."
        " see https://github.com/akaihola/pytest-kwparametrize"
        " for more info and examples.",
    )
