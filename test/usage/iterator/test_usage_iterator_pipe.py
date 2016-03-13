# -*- coding: utf-8 -*-
# test/usage/iterator/test_usage_iterator_pipe.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Usage tests for pipe() and ipipe()"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports

# Third-party imports

# Local imports
from apyt.iterator import pipe, ipipe


# ============================================================================
# Helpers
# ============================================================================


def add1(iterator):
    """Add 1"""
    for i in iterator:
        yield i + 1


def mult10(iterator):
    """Multiply by 10"""
    for i in iterator:
        yield i * 10


def mult100(iterator):
    """Multiply by 100"""
    for i in iterator:
        yield i * 100


# ============================================================================
# pipe() usage tests
# ============================================================================


def test_pipe():
    """Create single pipe generator func from other generator functions"""
    values = list(range(10))
    expected = [(i + 1) * 1000 for i in values]

    pipefunc = pipe(add1, mult10, mult100)
    result = list(pipefunc(values))
    assert result == expected


def test_ipipe():
    """Combine generator functions into a single generator function"""
    values = list(range(10))
    expected = [(i + 1) * 1000 for i in values]

    result = list(ipipe(values, add1, mult10, mult100))
    assert result == expected


# ============================================================================
#
# ============================================================================
