# -*- coding: utf-8 -*-
# test/unit/pyfile/test_unit_pyfile_astnode.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Unit tests for class ASTNode"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import ast

# Third-party imports
import pytest

# Local imports
from apyt.pyfile import ASTNode


# ============================================================================
# Init tests
# ============================================================================


@pytest.mark.parametrize('val', [
    None, 1, 1.1, 'hello'
])
def test_init_arg_node_ast_type(val):
    """node arg can only be an ast.AST object"""
    expected = 'node arg expected {}, got {} instead'
    expected = (expected.format(ast.AST.__name__, val.__class__.__name__), )
    with pytest.raises(TypeError) as err:
        ASTNode(val)
    assert err.value.args == expected


def test_init_attr_node():
    """node attribute is set to the value of the node arg"""
    src = 'a = 1'
    root = ast.parse(src)
    node = ASTNode(root)
    assert getattr(node, 'node', None) == root


@pytest.mark.parametrize('val', [
    42, 4.2, 'hello',
    ast.parse('b = 2')
])
def test_init_arg_parent_wrongtype(val):
    """parent arg can only be None or an ast.AST instance"""
    expected = 'parent arg expected {} or {}, got {} instead'
    expected = (expected.format(ASTNode.__name__,
                                type(None).__name__,
                                val.__class__.__name__), )
    src = 'a = 1'
    root = ast.parse(src)
    with pytest.raises(TypeError) as err:
        ASTNode(root, parent=val)
    assert err.value.args == expected


@pytest.mark.parametrize('parent', [
    ASTNode(ast.parse('a = 1')),
    None
])
def test_init_attr_parent(parent):
    """_parent attr is set to the value of the parent arg"""
    root = ast.parse('b = 2')
    node = ASTNode(root, parent=parent)
    nparent = node._parent
    assert nparent is parent


# ============================================================================
# __iter__ tests
# ============================================================================


def test_iter_no_body():
    """If the wrapped node has no child nodes, don't yield anything"""
    src = '1'
    root = ast.parse(src)

    # The tree is Module -> Expr -> Number
    # root = Module; root.body[0] = Expr
    node = ASTNode(root.body[0].value)
    assert list(node) == []


def test_iter_empty_body():
    """Don't yield anything if wrapped node has an empty body attr"""
    root = ast.parse('')
    node = ASTNode(root)
    assert list(node) == []


def test_iter_body():
    """Yield elements of wrapped node's body attr"""
    root = ast.parse('a = 1')
    node = ASTNode(root)
    assert [n.node for n in node] == root.body


def test_iter_yield_astnode():
    """All yielded elements are of type ASTNode"""
    src = """
def a():
    return 42
def b():
    return 4242
    """.strip()
    root = ast.parse(src)
    node = ASTNode(root)
    assert all(isinstance(n, ASTNode) for n in node)


def test_iter_yield_subclass():
    """All yielded elements are a subclass of ASTNode"""
    class SubASTNode(ASTNode):
        """SubASTNode"""

    src = """
def a():
    return 42
def b():
    return 4242
    """.strip()
    root = ast.parse(src)
    node = SubASTNode(root)
    assert all(isinstance(n, ASTNode) and isinstance(n, SubASTNode)
               for n in node)


# ============================================================================
# __getattr__ tests
# ============================================================================


def test_getattr_noattr():
    """Raise error if node object does not contain attr name"""
    src = 'a = 42'
    root = ast.parse(src)
    node = ASTNode(root)
    name = 'what'
    expected = ("'{}' object has no attribute '{}'".
                format(root.__class__.__name__, name))
    with pytest.raises(AttributeError) as err:
        node.__getattr__(name)

    assert err.value.args == (expected, )


def test_getattr_hasattr():
    """Retrieve node attr"""
    src = """
def a():
    return 42
def b():
    return 4242
    """.strip()
    root = ast.parse(src)
    node = ASTNode(root)
    assert node.body == root.body


# ============================================================================
# parent property test
# ============================================================================


def test_prop_parent_get():
    """Return value of _parent"""
    src = """
def a():
    return 42
def b():
    return 4242
    """.strip()
    root = ast.parse(src)
    node = ASTNode(root)
    assert node.parent is None
    node._parent = 42
    assert node.parent == 42


def test_prop_parent_noset():
    """parent property is read-only"""
    src = 'a = 42'
    root = ast.parse(src)
    node = ASTNode(root)
    expected = "can't set attribute"
    with pytest.raises(AttributeError) as err:
        node.parent = 42
    assert err.value.args == (expected, )


# ============================================================================
# children property test
# ============================================================================


def test_prop_children_fromiter():
    """Create list from __iter__ method"""
    class CustomIter(ASTNode):
        """Custom iter"""
        def __iter__(self):
            return (i for i in range(42))

    src = 'a = 42'
    root = ast.parse(src)
    node = CustomIter(root)
    expected = list(range(42))
    assert node.children == expected


# ============================================================================
#
# ============================================================================
