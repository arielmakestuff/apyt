# -*- coding: utf-8 -*-
# test/unit/iterator/test_pipe.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""pipe iterator function unit tests"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
from functools import partial
from itertools import filterfalse

# Third-party imports
import pytest

# Local imports
from apyt.iterator import pipe


# ============================================================================
# pipe() tests
# ============================================================================


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_bad_func(val):
    """Passing non-callable raises an error"""
    pipefunc = pipe(int)
    with pytest.raises(TypeError):
        list(pipefunc(range(10)))


@pytest.mark.parametrize('val', [42, 4.2, '42'])
def test_bad_otherfunc(val):
    """Passing non-callable via other arg raises an error"""
    pipefunc = pipe(int, val)
    with pytest.raises(TypeError):
        list(pipefunc(range(10)))


def test_single_func():
    """Passing a single func is the same as just using that func"""
    func = partial(filterfalse, lambda x: x % 2)
    pipefunc = pipe(func)
    vals = list(range(10))
    expected = list(func(vals))
    assert list(pipefunc(vals)) == expected


@pytest.mark.parametrize('num', list(range(1, 11)))
def test_multiple_func(num):
    """Combine multiple functions into single pipe function"""
    def plus1(iterator):
        """Add 1"""
        for i in iterator:
            yield i + 1

    def plusx(num, iterator):
        """Add x*10"""
        for i in iterator:
            yield i + (10 * num)

    args = [partial(plusx, i + 1) for i in range(num)]

    vals = list(range(10))
    iterfunc = plus1(vals)
    for f in args:
        iterfunc = f(iterfunc)
    expected = list(iterfunc)

    pipefunc = pipe(plus1, *args)
    assert list(pipefunc(vals)) == expected


@pytest.mark.parametrize('val', [42, int, 4.2])
def test_noniterable(val):
    """Passing a non-iterable to the pipe generator raises an error"""
    func = partial(filterfalse, lambda x: x % 2 == 0)
    pipefunc = pipe(func)

    expected = '{} object is not iterable'.format(type(val).__name__)
    with pytest.raises(TypeError) as err:
        list(pipefunc(val))
    assert err.value.args == (expected, )


# ============================================================================
#
# ============================================================================
