.. _`reference`:

.. currentmodule:: pytest_kwparametrize.plugin

API Reference
=============

This page contains the full reference to pytest's API.

.. contents::
    :depth: 3
    :local:


Functions
---------

pytest_kwparametrize.plugin.kwparametrize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: pytest_kwparametrize.plugin.kwparametrize


Marks
-----

Marks can be used apply meta data to *test functions* (but not fixtures), which can then be accessed by
fixtures or plugins.

.. _`pytest.mark.kwparametrize ref`:

pytest.mark.kwparametrize
~~~~~~~~~~~~~~~~~~~~~~~~~

**Tutorial**: :doc:`kwparametrize`.

This mark has almost the same signature as :py:meth:`kwparametrize`; see there
but disregard the ``metafunc`` argument.
