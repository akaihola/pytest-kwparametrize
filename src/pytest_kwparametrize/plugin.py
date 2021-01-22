"""Implementation of the ``kwparametrize`` Pytest plugin"""

import sys
from collections import abc
from inspect import Parameter, signature
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple, Union, cast

import pytest
from _pytest.mark import ParameterSet
from _pytest.python import Metafunc
from pytest import fail

if sys.version_info >= (3, 8):
    # pylint: disable=no-name-in-module
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


def _get_keyword_parameters(function: Callable[..., Any]) -> List[str]:
    return [
        param_name
        for param_name, param in signature(function).parameters.items()
        if param.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]
    ]


# Keyword argument names accepted by @pytest.mark.parametrize().
# These keywords can't be used as parameter names for parametrized test cases.
# Fish these from Pytest internals to hope for better forward compatibility.
# In Pytest 6.1.2: ["indirect", "ids", "scope", "_param_mark"]
PARAMETRIZE_KEYWORDS = set(_get_keyword_parameters(Metafunc.parametrize)[3:])

# Keyword argument names accepted by `pytest.param(...)`
# These keywords can't be used as parameter names for parametrized test cases.
# Fish these from Pytest internals to hope for better forward compatibility.
# In Pytest 6.1.2: ["marks", "id"]
PYTEST_PARAM_KEYWORDS = set(_get_keyword_parameters(pytest.param))


DictOfAny = Dict[str, Any]
TestCase = Mapping[str, Any]
TestCases = Sequence[TestCase]


def _get_param(
    name: str, params: DictOfAny, defaults: DictOfAny, metafunc: Metafunc
) -> Any:
    if name in params:
        return params[name]
    if defaults[name] is ...:
        fail(
            f"In {metafunc.function.__name__}: The '{name}' parameter was omitted in a "
            f"@kwparametrize test case but marked as required",
            pytrace=False,
        )
    return defaults[name]


def _has_one_iterable(marker_args: List[Union[TestCases, TestCase]]) -> bool:
    return (
        len(marker_args) == 1
        and isinstance(marker_args[0], abc.Sequence)
        and not isinstance(marker_args[0], abc.Mapping)
    )


def _parse_marker_args(marker_args: List[Union[TestCases, TestCase]]) -> List[TestCase]:
    if _has_one_iterable(marker_args):
        # called like:
        # @pytest.mark.kwparametrize([dict(<case1>), dict(<case2>), ...])
        testcase_dicts = cast(TestCases, marker_args[0])
    else:
        # called like:
        # @pytest.mark.kwparametrize(dict(<case1>), dict(<case2>), ...)
        testcase_dicts = cast(TestCases, marker_args)
    return list(testcase_dicts)


TestParams = Dict[str, Any]


class ParametrizeKwArgs(TypedDict):
    """Types for kwparametrize() keyword arguments"""

    ...


class MarkerKwArgs(TypedDict):
    """Types for @pytest.mark.kwparametrize() keyword arguments"""

    defaults: TestParams


def _parse_marker_kwargs(kwargs: DictOfAny) -> Tuple[TestParams, ParametrizeKwArgs]:
    parametrize_kwargs = {k: v for k, v in kwargs.items() if k in PARAMETRIZE_KEYWORDS}
    defaults = {k: v for k, v in kwargs.items() if k not in PARAMETRIZE_KEYWORDS}
    if set(defaults) == {"defaults"}:
        # called like:
        # @pytest.mark.kwaparametrize(..., defaults=dict(param1=, param2=, ...))
        default_params = cast(TestParams, defaults["defaults"])
    else:
        # called like:
        # @pytest.mark.kwaparametrize(..., param1=, param2=, ...)
        default_params = defaults
    return default_params, cast(ParametrizeKwArgs, parametrize_kwargs)


ParametrizeArgValues = List[ParameterSet]


def _param_dicts_to_tuples(
    testcase_dicts: List[TestCase], defaults: TestParams, metafunc: Metafunc
) -> ParametrizeArgValues:
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
    *args: Union[List[DictOfAny], DictOfAny],
    **kwargs: Any,
) -> None:
    """Add new invocations to the underlying test function using the list
    of argvalues for the test function arguments.  Parametrization is performed
    during the collection phase.  If you need to setup expensive resources
    see about setting indirect to do it rather at test setup time.

    :param metafunc:
        A :py:class:`pytest.Metafunc` object representing the test function.
        **Note:** The :ref:`pytest.mark.kwparametrize ref` decorator accepts all the
        same arguments as this function except for ``metafunc`` which must be omitted.

    :param args:
        The list of test arguments determines how often a test is invoked with
        different argument values.

        If only one list value was specified as a positional argument,
        it must contain test parameters as dictionaries.
        If N positional arguments were specified, each of them must be a dictionary,
        where each item specifies a value for the test function's respective parameter.

    :param indirect:
        A list of arguments' names (subset of argnames) or a boolean.
        If True the list contains all names from the argnames. Each
        argvalue corresponding to an argname in this list will
        be passed as request.param to its respective argname fixture
        function so that it can perform more expensive setups during the
        setup phase of a test rather than at collection time.

    :param ids:
        Sequence of (or generator for) ids for ``argvalues``,
        or a callable to return part of the id for each argvalue.

        With sequences (and generators like :func:`itertools.count`) the
        returned ids should be of type ``str``, ``int``, ``float``,
        ``bool``, or ``None``.
        They are mapped to the corresponding index in ``args``.
        ``None`` means to use the auto-generated id.

        If it is a callable it will be called for each entry in
        ``args``, and the return value is used as part of the
        auto-generated id for the whole set (where parts are joined with
        dashes ("-")).
        This is useful to provide more specific ids for certain items, e.g.
        dates.  Returning ``None`` will use an auto-generated id.

        If no ids are provided they will be generated automatically from
        the args.

    :param scope:
        If specified it denotes the scope of the parameters.
        The scope is used for grouping tests by parameter instances.
        It will also override any fixture-function defined scope, allowing
        to set a dynamic scope using test context or configuration.

    """
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
    """In Pytest's test generation hook, handle ``@pytest.mark.kwparametrize``"""
    for marker in metafunc.definition.iter_markers(name="kwparametrize"):
        kwparametrize(metafunc, *marker.args, _param_mark=marker, **marker.kwargs)


def pytest_configure(config):
    """Configure Pytest to know about the ``@pytest.mark.kwparametrize`` marker """
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
