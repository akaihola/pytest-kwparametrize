======================
 pytest-kwparametrize
======================

Alternate syntax for ``@pytest.mark.parametrize`` with test cases as dictionaries
and default value fallbacks.

The problem
===========

Tests parametrized using ``@pytest.mark.parametrize`` can easily become hard to read
when the number of parameters grows large. For example::

    @pytest.mark.parametrize(
        "a, b, c, d, e, f, expect",
        [
            (3, "one", 4.0, 0x01, 0o5, 9e0, 0b10,),
            (6, "five", 3.0, 0x05, 0o10, 9e0, 0b111,),
        ],
    )
    def test_my_func(a, b, c, d, e, f, expect):
        assert my_func(a, b, c, d, e, f) == expect

The solution
============

``pytest-kwparametrize`` uses dictionaries instead of tuples for test cases.
This way every parameter is always labeled and more easily identified by the reader.
Also, test function parameters aren't declared separately
as with ``@pytest.mark.parametrize``,
and test cases don't need to be enclosed in a list::

    @pytest.mark.kwparametrize(
        dict(a=3, b="one", c=4.0, d=0x01, e=0o5, f=9e0, expect=0b10,),
        dict(a=6, b="five", c=3.0, d=0x05, e=0o10, f=9e0, expect=0b111,),
    )
    def test_my_func(a, b, c, d, e, f, expect):
        assert my_func(a, b, c, d, e, f) == expect

See examples below for additional features.


Examples
========

Basic syntax with no default values::

    @pytest.mark.kwparametrize(
        dict(a=0, b=0, expect=0),
        dict(a=1, b=0, expect=1),
    )
    def test_my_func(a, b, expect):
        assert my_func(a, b) == expect

Defining a default value for a parameter so it can be omitted from test cases::

    @pytest.mark.kwparametrize(
        dict(a=0, expect=0),
        dict(a=1, expect=1),
        dict(a=0, b=1, expect=0),
        dict(a=1, b=1, expect=2),
        b=0,
    )
    def test_my_func(a, b, expect):
        assert my_func(a, b) == expect

You can also provide the test cases as an iterable (e.g. list, tuple, generator)
just as with ``@pytest.mark.parametrize``::

    @pytest.mark.kwparametrize(
        [
            dict(a=0, b=0, expect=0),
            dict(a=1, b=0, expect=1),
        ]
    )
    def test_my_func(a, b, expect):
        assert my_func(a, b) == expect

Default values can also be paassed as a dictionary
using the ``defaults=`` keyword argument
(here all parameters have a default)::

    @pytest.mark.kwparametrize(
        dict(),
        dict(a=1, expect=1),
        dict(b=1),
        dict(a=1, b=1, expect=2),
        defaults=dict(a=0, b=0, expect=0),
    )
    def test_my_func(a, b, expect):
        assert my_func(a, b) == expect

The marker works with fixtures and Pytest's built-in keyword arguments::

    @pytest.mark.kwparametrize(
        # test cases:
        dict(),
        dict(filename="special.txt", expect=1),
        dict(content="special content"),

        # default parameter values:
        filename="dummy.txt",
        content="dummy content",
        expect=42,

        # example of a Pytest built-in keyword argument:
        ids=["with defaults", "special filename", "speial content"],
    )
    def test_my_func(tmpdir, filename, content, expect):
        filepath = (tmpdir / filename)
        filepath.write(content)
        assert my_func(filepath) == expect


Contributors ✨
===============

Thanks goes to these people (`emoji key`_):

.. raw:: html

   <!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
   <table>
       <tr>
           <td align="center">
               <a href="https://github.com/akaihola">
                   <img src="https://avatars.githubusercontent.com/u/13725?v=3" width="100px;" alt="@akaihola"/>
                   <br />
                   <sub><b>Antti Kaihola</b></sub>
               </a>
               <br />
               <a href="#question-akaihola" title="Answering Questions">💬</a>
               <a href="https://github.com/akaihola/pytest-kwparametrize/commits?author=akaihola"
                  title="Code">💻</a>
               <a href="https://github.com/akaihola/pytest-kwparametrize/commits?author=akaihola"
                  title="Documentation">📖</a>
               <a href="https://github.com/akaihola/pytest-kwparametrize/pulls?q=is%3Apr+reviewed-by%3Aakaihola"
                  title="Reviewed Pull Requests">👀</a>
               <a href="#maintenance-akaihola" title="Maintenance">🚧</a>
           </td>
       </tr>
   </table>
   <!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the all-contributors_ specification.
Contributions of any kind are welcome!

.. _README.rst: https://github.com/akaihola/pytest-kwparametrize/README.rst
.. _emoji key: https://allcontributors.org/docs/en/emoji-key
.. _all-contributors: https://allcontributors.org
