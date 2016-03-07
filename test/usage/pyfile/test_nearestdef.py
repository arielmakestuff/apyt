# -*- coding: utf-8 -*-
# /home/smokybobo/opt/repos/git/personal/apyt/test/usage/pyfile/test_nearestdef.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Usage test for NearestDef"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import ast

# Third-party imports
import pytest

# Local imports
from apyt.pyfile import NearestDef


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def msource():
    """Return medium-complexity source code"""
    src = """
def a():
    return 42
def b():
    def z():
        return 'z'
    return 4242
def c():
    return 4242
class D:
    def da(self):
        class No:
            def noa(self):
                return 'noa'
        return 'da'
if True:
    def zz():
        return 'zz'
    """.strip()
    return src


# ============================================================================
#
# ============================================================================


def test_nearest_class(msource):
    """Find nearest top-level class"""
    root = ast.parse(msource)
    line = 15
    finder = NearestDef(root, line)
    node = finder()
    assert isinstance(node.node, ast.ClassDef)
    assert node.name == 'D'


# ============================================================================
#
# ============================================================================
