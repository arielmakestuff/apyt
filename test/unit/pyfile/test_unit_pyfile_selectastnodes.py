# -*- coding: utf-8 -*-
# /home/smokybobo/opt/repos/git/personal/apyt/test/unit/pyfile/test_unit_pyfile_selectastnodes.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Test SelectASTNodes"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import ast

# Third-party imports
import pytest

# Local imports
from apyt.pyfile import ASTNode, SelectASTNodes


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def funcsrc():
    """Return source of a simple function definition"""
    src = """
def a():
    return 42
    """.strip()
    return src


@pytest.fixture
def src(funcsrc):
    """Return multi-statement source"""
    src = """{}
def b():
    return 4.2
c = 4242
class FortyTwo:
    def d(self):
        return 424242
    """.format(funcsrc).strip()
    return src


# ============================================================================
# Tests
# ============================================================================


def test_call_nodetype_is_astnode(funcsrc):
    """Accepts an ASTNode root node"""
    node = ast.parse(funcsrc)
    root = ASTNode(node)
    selector = SelectASTNodes(root, selectall=True, selectroot=True)
    nodes = set(n.node for n in selector())
    expected = set(ast.walk(node))
    assert nodes == expected


def test_call_nodetype_is_ast(funcsrc):
    """Accepts an ast.AST root node"""
    node = ast.parse(funcsrc)
    selector = SelectASTNodes(node, selectall=True, selectroot=True)
    nodes = set(n.node for n in selector())
    expected = set(ast.walk(node))
    assert nodes == expected


@pytest.mark.parametrize('val', [None, 'hello', 42, 4.2])
def test_call_node_badtype(val):
    """Raise exception if root node type is not ASTNode or ast.AST"""
    expected = ('node arg expected AST, got {} instead'.
                format(type(val).__name__))
    with pytest.raises(TypeError) as err:
        SelectASTNodes(val)
    assert err.value.args == (expected, )


def test_call_initnode(funcsrc):
    """initnode() method called if initnode init arg is True"""
    vals = []

    class CallInitNode(SelectASTNodes):
        """Test initnode method"""

        def initnode(self, node):
            """initnode"""
            vals.append(type(node.node).__name__)

    node = ast.parse(funcsrc)
    selector = SelectASTNodes(node, selectall=True, selectroot=True)
    expected = [type(n.node).__name__ for n in selector()]
    test = CallInitNode(node, selectall=True, selectroot=True)
    list(test())
    assert vals
    assert vals == expected


def test_call_noinitnode(funcsrc):
    """initnode() method is not called if initnode init arg is False"""
    vals = []

    class CallInitNode(SelectASTNodes):
        """Test initnode method"""

        def initnode(self, node):
            """initnode"""
            vals.append(type(node.node).__name__)

    node = ast.parse(funcsrc)
    test = CallInitNode(node, selectall=True, selectroot=True, initnode=False)
    list(test())
    assert not vals


@pytest.mark.parametrize('replace,selectall,selectroot', [
    (r, sa, sr) for r in [True, False]
    for sa in [True, False]
    for sr in [True, False]
])
def test_call_rootnode_always_selected(funcsrc, replace, selectall,
                                       selectroot):
    """Root node is always selected"""
    nodes = []

    class StoreNodes(SelectASTNodes):
        """Test initnode method"""

        def initnode(self, node):
            """initnode"""
            nodes.append(node.node)

    node = ast.parse(funcsrc)
    selector = StoreNodes(node, replace=replace, selectall=selectall,
                          selectroot=selectroot, initnode=True)
    list(selector())
    assert nodes
    assert nodes[0] is node


@pytest.mark.parametrize('replace,selectall', [
    (r, sa) for r in [True, False]
    for sa in [True, False]
])
def test_call_yield_rootnode(funcsrc, replace, selectall):
    """Yield root node if selectroot init arg is True"""
    node = ast.parse(funcsrc)
    selector = SelectASTNodes(node, selectroot=True, initnode=True,
                              selectall=selectall, replace=replace)
    result = [n.node for n in selector()]
    assert result
    assert result[0] is node


@pytest.mark.parametrize('replace,selectall', [
    (r, sa) for r in [True, False]
    for sa in [True, False]
])
def test_call_norootnode(funcsrc, replace, selectall):
    """Don't yield root node if selectroot init arg is False"""
    node = ast.parse(funcsrc)
    selector = SelectASTNodes(node, selectroot=False, selectall=selectall,
                              replace=replace)
    result = [n.node for n in selector()]
    assert result
    assert result[0] is not node
    assert node not in result


def test_call_match(funcsrc):
    """Yield node if match() return value is True"""

    class OnlyFunctions(SelectASTNodes):
        """Select only functions"""

        def match(self, node):
            """Return True if node is a FunctionDef"""
            return isinstance(node.node, ast.FunctionDef)

    node = ast.parse(funcsrc)
    expected = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
    selector = OnlyFunctions(node, selectroot=False, selectall=True,
                             initnode=False)
    found = [n.node for n in selector()]
    assert found == expected
    assert len(found) == 1
    assert found[0] is expected[0]


def test_call_nomatch(funcsrc):
    """Don't yield node if match() return value is False"""

    class AnythingButFunctions(SelectASTNodes):
        """Select everything except functions"""

        def match(self, node):
            """Return False if node is a FunctionDef"""
            return not isinstance(node.node, ast.FunctionDef)

    node = ast.parse(funcsrc)
    expected = [n for n in ast.walk(node)
                if not isinstance(n, ast.FunctionDef)]
    selector = AnythingButFunctions(node, selectroot=True, selectall=True,
                                    initnode=False)
    found = [n.node for n in selector()]
    assert found == expected
    assert not any(isinstance(n, ast.FunctionDef) for n in found)


def test_walk_allnodes(funcsrc):
    """Walk through all nodes if selectall init arg is True"""
    node = ast.parse(funcsrc)
    expected = [n for n in ast.walk(node)]
    selector = SelectASTNodes(node, selectroot=True, selectall=True,
                              initnode=False)
    nodes = [n.node for n in selector()]
    assert nodes
    assert nodes == expected


def test_walk_selectednodes(src, funcsrc):
    """Walk through only selected nodes if selectall init arg is False"""

    class AFunction(SelectASTNodes):
        """Select only 'a' function"""

        def match(self, node):
            """Match 'a' function and children"""
            if getattr(node, 'col_offset', None) == 0:
                return (
                    isinstance(node.node, ast.FunctionDef) and
                    node.name == 'a'
                )
            return True

    # FunctionDef objects has a 'name' attr
    # Num objects have an 'n' attr
    expected = [(type(n).__name__, getattr(n, 'name', None),
                 getattr(n, 'n', None))
                for n in ast.walk(ast.parse(funcsrc))][1:]
    node = ast.parse(src)
    selector = AFunction(node, selectall=False, selectroot=False,
                         initnode=False)
    nodes = [(type(n.node).__name__, getattr(n, 'name', None),
              getattr(n, 'n', None))
             for n in selector()]
    assert nodes == expected


def test_yield_last_selectednodes(funcsrc):
    """Yield child nodes of last selected node"""
    src = """
def b():
    return 'b'
def c():
    return 'c'
def d():
    return 'd'
{}
    """.strip().format(funcsrc)

    class TopFunction(SelectASTNodes):
        """Select only top level functions"""

        def match(self, node):
            """Match top level function and children"""
            if getattr(node, 'col_offset', None) == 0:
                return isinstance(node.node, ast.FunctionDef)
            return True

    node = ast.parse(src)

    # Setup expected values
    expected = [(type(n).__name__, getattr(n, 'name', None),
                 getattr(n, 'n', None))
                for n in ast.walk(ast.parse(funcsrc))][1:]
    expected = [('FunctionDef', name, None) for name in 'bcd'] + expected

    # Get nodes from source
    selector = TopFunction(node, selectall=False, selectroot=False,
                           initnode=False, replace=True)
    nodes = [(type(n.node).__name__, getattr(n, 'name', None),
              getattr(n, 'n', None))
             for n in selector()]
    assert nodes == expected


def test_call_process_method(funcsrc):
    """Return value of process() method is yielded for every selected node"""

    class TestProcess(SelectASTNodes):
        """Test process method"""

        def process(self, node):
            """Return 42"""
            return 42

    node = ast.parse(funcsrc)
    expected = [42 for n in ast.walk(node)]
    selector = TestProcess(node, selectroot=True, selectall=True,
                           initnode=False, replace=False)
    values = list(selector())
    assert values == expected


# ============================================================================
#
# ============================================================================
