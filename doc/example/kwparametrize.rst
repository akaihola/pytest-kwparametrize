
.. _kwparamexamples:

Parametrizing tests with ``kwparametrize``
=================================================

:func:`pytest_kwparametrize.plugin.kwparametrize`

.. currentmodule:: pytest_kwparametrize.plugin

``pytest-kwparametrize`` allows to easily parametrize test functions
with an alternative syntax compared to
:ref:`@pytest.mark.parametrize <pytest:@pytest.mark.parametrize>`.
For basic ``kwparametrize`` docs, see :ref:`kwparametrize-basics`,
and for plain :ref:`@pytest.mark.parametrize <pytest:@pytest.mark.parametrize>` docs,
see :ref:`parametrize-basics`.

In the following we provide some examples using
the mechanisms provided by ``pytest-kwparametrize``.

Different options for test IDs
------------------------------------

pytest builds a test ID string for each case in a parametrized test.
See :ref:`paramexamples` for more information.

These examples are the ``pytest-kwparametrize`` versions
of the examples in :ref:`paramexamples`:

.. literalinclude:: test_time.py
   :language: python


.. code-block:: pytest

    $ pytest test_time.py --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collected 8 items

    <Module test_time.py>
      <Function test_timedistance_v0[a0-b0-expected0]>
      <Function test_timedistance_v0[a1-b1-expected1]>
      <Function test_timedistance_v1[forward]>
      <Function test_timedistance_v1[backward]>
      <Function test_timedistance_v2[20011212-20011211-expected0]>
      <Function test_timedistance_v2[20011211-20011212-expected1]>
      <Function test_timedistance_v3[forward]>
      <Function test_timedistance_v3[backward]>

    ======================== 8 tests collected in 0.12s ========================

In ``test_timedistance_v3``, we used ``pytest.param`` to specify the test IDs
together with the actual data, instead of listing them separately.

A quick port of "testscenarios"
------------------------------------

.. _`test scenarios`: https://pypi.org/project/testscenarios/

Here is a quick port to run tests configured with `test scenarios`_,
an add-on from Robert Collins for the standard unittest framework. We
only have to work a bit to construct the correct arguments for pytest-kwparametrize's
:py:func:`kwparametrize`:

.. literalinclude:: test_scenarios.py
   :language: python

this is a fully self-contained example which you can run with:

.. code-block:: pytest

    $ pytest test_scenarios.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collected 4 items

    test_scenarios.py ....                                               [100%]

    ============================ 4 passed in 0.12s =============================

If you just collect tests you'll also nicely see 'advanced' and 'basic' as variants for the test function:

.. code-block:: pytest

    $ pytest --collect-only test_scenarios.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collected 4 items

    <Module test_scenarios.py>
      <Class TestSampleWithScenarios>
          <Function test_demo1[basic]>
          <Function test_demo2[basic]>
          <Function test_demo1[advanced]>
          <Function test_demo2[advanced]>

    ======================== 4 tests collected in 0.12s ========================

Note that we told ``kwparametrize()`` that your scenario values
should be considered class-scoped.  With pytest-2.3 this leads to a
resource-based ordering.

Deferring the setup of parametrized resources
---------------------------------------------------

The parametrization of test functions happens at collection
time.  It is a good idea to setup expensive resources like DB
connections or subprocess only when the actual test is run.
Here is a simple example how you can achieve that. This test
requires a ``db`` object fixture:

.. literalinclude:: defer_setup/test_backends.py
   :language: python

We can now add a test configuration that generates two invocations of
the ``test_db_initialized`` function and also implements a factory that
creates a database object for the actual test invocations:

.. literalinclude:: defer_setup/conftest.py
   :language: python

Let's first see how it looks like at collection time:

.. code-block:: pytest

    $ pytest test_backends.py --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collected 2 items

    <Module test_backends.py>
      <Function test_db_initialized[d1]>
      <Function test_db_initialized[d2]>

    ======================== 2 tests collected in 0.12s ========================

And then when we run the test:

.. code-block:: pytest

    $ pytest -v test_backends.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y -- $PYTHON_PREFIX/bin/python
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collecting ... collected 2 items

    test_backends.py::test_db_initialized[d1] XPASS
    test_backends.py::test_db_initialized[d2] XFAIL

    ======================= 2 passed, 1 xfailed in 0.04s =======================

The first invocation with ``db == "DB1"`` passed while the second with ``db == "DB2"`` failed.  Our ``db`` fixture function has instantiated each of the DB values during the setup phase while the ``pytest_generate_tests`` generated two according calls to the ``test_db_initialized`` during the collection phase.

Indirect parametrization
---------------------------------------------------

Using the ``indirect=True`` parameter when parametrizing a test allows to
parametrize a test with a fixture receiving the values before passing them to a
test:

.. literalinclude:: test_indirect.py
   :language: python

This can be used, for example, to do more expensive setup at test run time in
the fixture, rather than having to run those setup steps at collection time.

Apply indirect on particular arguments
---------------------------------------------------

Very often parametrization uses more than one argument name. There is opportunity to apply ``indirect``
parameter on particular arguments. It can be done by passing list or tuple of
arguments' names to ``indirect``. In the example below there is a function ``test_indirect`` which uses
two fixtures: ``x`` and ``y``. Here we give to indirect the list, which contains the name of the
fixture ``x``. The indirect parameter will be applied to this argument only, and the value ``a``
will be passed to respective fixture function:

.. literalinclude:: test_indirect_list.py
   :language: python

The result of this test will be successful:

.. code-block:: pytest

    $ pytest -v test_indirect_list.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y -- $PYTHON_PREFIX/bin/python
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collecting ... collected 1 item

    test_indirect_list.py::test_indirect[a-b] PASSED                     [100%]

    ============================ 1 passed in 0.12s =============================

Parametrizing test methods through per-class configuration
--------------------------------------------------------------

.. _`unittest parametrizer`: https://github.com/testing-cabal/unittest-ext/blob/master/params.py

Here is an example ``pytest_generate_tests`` function implementing a
parametrization scheme similar to Michael Foord's `unittest
parametrizer`_ but in a lot less code:

.. literalinclude:: test_parametrize.py
   :language: python

There's are class-level definitions which specify which argument sets to use
for each test function.  But instead of looking it up automatically, as is done in
stock ``@pytest.mark.parametrize``'s :ref:`paramexamples` examples,
we simply point to it in the ``@kwparametrize`` decorator.  Let's run it:

.. code-block:: pytest

    $ pytest -v
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y -- $PYTHON_PREFIX/bin/python
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collecting ... collected 3 items

    test_parametrize.py::TestClass::test_equals[1-2] XFAIL
    test_parametrize.py::TestClass::test_equals[3-3] PASSED
    test_parametrize.py::TestClass::test_zerodivision[1-0] PASSED

    ======================= 2 passed, 1 xfailed in 0.04s =======================

Set marks or test ID for individual parametrized test
--------------------------------------------------------------------

With ``@kwparametrize``, you don't use ``pytest.param``
to apply marks or set test IDs to individual parametrized tests.
Instead, just add ``marks=[...]`` or ``id=...`` as extra keys
in the test case dictionary.
For example:

.. literalinclude:: test_pytest_param_example.py
   :language: python

In this example, we have 4 parametrized tests. Except for the first test,
we mark the rest three parametrized tests with the custom marker ``basic``,
and for the fourth test we also use the built-in mark ``xfail`` to indicate this
test is expected to fail. For explicitness, we set test ids for some tests.

Then run ``pytest`` with verbose mode and with only the ``basic`` marker:

.. code-block:: pytest

    $ pytest -v -m basic
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-0.x.y -- $PYTHON_PREFIX/bin/python
    rootdir: pytest-kwparametrize
    plugins: kwparametrize-x.y.z
    collecting ... collected 4 items / 1 deselected / 3 selected

    test_pytest_param_example.py::test_eval[1+7-8] PASSED                [ 33%]
    test_pytest_param_example.py::test_eval[basic_2+4] PASSED            [ 66%]
    test_pytest_param_example.py::test_eval[basic_6*9] XFAIL             [100%]

    =============== 2 passed, 11 deselected, 1 xfailed in 0.12s ================

As the result:

- Four tests were collected
- One test was deselected because it doesn't have the ``basic`` mark.
- Three tests with the ``basic`` mark was selected.
- The test ``test_eval[1+7-8]`` passed, but the name is autogenerated and confusing.
- The test ``test_eval[basic_2+4]`` passed.
- The test ``test_eval[basic_6*9]`` was expected to fail and did fail.

.. _`kwparametrizing_conditional_raising`:

Parametrizing conditional raising
--------------------------------------------------------------------

Use :func:`pytest.raises` with the
:ref:`pytest.mark.kwparametrize ref` decorator to write parametrized tests
in which some tests raise exceptions and others do not.

It is helpful to define a no-op context manager ``does_not_raise`` to serve
as a complement to ``raises``. For example:

.. literalinclude:: test_conditional_raising.py
   :language: python

In the example above, the first three test cases should run unexceptionally,
while the fourth should raise ``ZeroDivisionError``.
