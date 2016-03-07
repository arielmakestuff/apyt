# -*- coding: utf-8 -*-
# test/unit/pyfile/test_unit_pyfile_walk.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Tests for walk() function"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import ast

# Third-party imports

# Local imports
from apyt.pyfile import ASTNode, walk


# ============================================================================
# Tests
# ============================================================================


def test_walk_firstnode():
    """First node returned is always root"""
    root = ast.parse('')
    node = ASTNode(root)
    result = list(walk(node))
    assert len(result) == 1
    assert isinstance(result[0], ASTNode)
    assert result[0].node is root
    assert result[0].parent is None


def test_walk_allnodes():
    """Returns same set of nodes as ast.walk"""
    src = """
def a():
    return 42
def b():
    return 4242
def c():
    return 4242
class Hello:
    def __init__(self):
        self.msg = 'World'
    """.strip()
    root = ast.parse(src)
    node = ASTNode(root)
    astwalk = {'<{}> {}'.format(getattr(n, 'name', ''), type(n).__name__)
               for n in ast.walk(root)}
    new_walk = {'<{}> {}'.format(getattr(n, 'name', ''),
                                 type(n.node).__name__)
                for n in walk(node)}
    assert len(astwalk) == len(new_walk)


def test_walk_arg_replace():
    """Only returns def nodes + last statement"""
    src = """
def a():
    return 42
def b():
    return 4242
def c():
    return 4242
class Hello:
    def __init__(self):
        self.msg = 'World'
a = 42
    """.strip()
    root = ast.parse(src)
    node = ASTNode(root)
    expected = ['Module', 'FunctionDef', 'FunctionDef', 'FunctionDef',
                'ClassDef', 'Assign', 'Name', 'Num']
    result = [type(n.node).__name__ for n in walk(node, replace=True)]
    assert result == expected


def test_walk_select_node():
    """Select nodes to yield by sending boolean to generator"""
    src = """
def a():
    return 42
def b():
    return 4242
def c():
    return 4242
class Hello:
    def __init__(self):
        self.msg = 'World'
a = 42
    """.strip()
    root = ast.parse(src)
    node = ASTNode(root)
    result = []
    expected = ['<{}> FunctionDef'.format(s) for s in 'abc']

    gen = walk(node, replace=True)
    send = gen.send
    n = next(gen)
    assert n.node is root
    while True:
        rawnode = n.node
        try:
            if rawnode is root:
                n = send(True)
            elif isinstance(rawnode, ast.FunctionDef):
                result.append('<{}> {}'.format(getattr(n, 'name', ''),
                                               type(rawnode).__name__))
                n = send(True)
            else:
                n = send(False)
        except StopIteration:
            break
    assert result == expected


def test_walk_arg_node_ast():
    """Normal AST node gets automatically wrapped as ASTNode"""
    root = ast.parse('')
    nodes = list(walk(root))
    assert all(isinstance(n, ASTNode) for n in nodes)
    assert [n.node for n in nodes] == [root]


# ============================================================================
#
# ============================================================================
