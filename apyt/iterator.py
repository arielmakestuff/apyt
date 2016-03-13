# -*- coding: utf-8 -*-
# apyt/iterator.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Iterator utility functions"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
from collections.abc import Iterable

# Third-party imports

# Local imports


# ============================================================================
# pipe
# ============================================================================


def pipe(func, *other):
    """Create a generator callable from one or more generator function"""
    funclist = [func]
    funclist.extend(other)

    def pipefunc(iterator):
        """Pipe generator function"""
        if not isinstance(iterator, Iterable):
            raise TypeError('{} object is not iterable'.
                            format(type(iterator).__name__))
        curiter = iterator
        for func in funclist:
            curiter = func(curiter)

        for el in curiter:
            yield el

    return pipefunc


def ipipe(iterator, *func):
    """Create generator from an iterator and generator functions"""
    iterfunc = pipe(*func)
    for el in iterfunc(iterator):
        yield el


# ============================================================================
#
# ============================================================================
