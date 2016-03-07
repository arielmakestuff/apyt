# -*- coding: utf-8 -*-
# apyt/pyfile.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Functions to work with python files"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import ast
from fnmatch import fnmatch
import sys

# Third-party imports

# Local imports


# ============================================================================
# Globals
# ============================================================================


BLOCKTYPES = (ast.Try, ast.FunctionDef, ast.ClassDef, ast.If, ast.For,
              ast.With, ast.While)
if sys.version_info >= (3, 5):
    BLOCKTYPES += (ast.AsyncFor, ast.AsyncFunctionDef, ast.AsyncWith)


# ============================================================================
# ASTNode
# ============================================================================


class ASTNode:
    """AST Node Wrapper to provide children and parent info"""
    __slots__ = ('__weakref__', 'node', '_parent')

    def __init__(self, node, *, parent=None):
        if not isinstance(node, ast.AST):
            msg = 'node arg expected {}, got {} instead'
            raise TypeError(msg.format(ast.AST.__name__,
                                       node.__class__.__name__))
        elif not isinstance(parent, (type(None), ASTNode)):
            msg = 'parent arg expected {} or {}, got {} instead'
            raise TypeError(msg.format(ASTNode.__name__,
                                       type(None).__name__,
                                       parent.__class__.__name__))

        self.node = node
        self._parent = parent

    def __iter__(self):
        """Iterate over node's children"""
        wrapper = self.__class__
        for node in ast.iter_child_nodes(self.node):
            yield wrapper(node, parent=self)

    def __getattr__(self, name):
        """Return node attributes"""
        return getattr(self.node, name)

    @property
    def parent(self):
        """Return parent node"""
        return self._parent

    @property
    def children(self):
        """Return list of child nodes"""
        return list(self)


# ============================================================================
# walk function
# ============================================================================


def walk(node, *, replace=False):
    """Breadth-first walk based on ASTNode"""
    if not isinstance(node, ASTNode):
        node = ASTNode(node)
    curlist = [node]
    nextlist = []
    while True:
        for cur in curlist:
            isgood = yield cur
            if isgood or isgood is None:
                if replace:
                    nextlist = cur.children
                else:
                    nextlist.extend(cur)
        if not nextlist:
            break
        curlist = nextlist
        nextlist = []


# ============================================================================
# SelectASTNodes
# ============================================================================


class SelectASTNodes:
    """Define core behaviour to select nodes from the walk function"""

    def __init__(self, node, *, replace=False, selectall=False,
                 selectroot=False, initnode=True):
        self._node = node if isinstance(node, ASTNode) else ASTNode(node)
        self._replace = replace
        self._all = selectall
        self._selectroot = selectroot
        self._initnode = initnode

    def __call__(self):
        node = self._node
        root = node.node
        iterwalk = walk(node, replace=self._replace)

        # Dot optimizations
        send = iterwalk.send
        matchfunc = self.match
        process = self.process
        selectroot = self._selectroot
        initnode = self.initnode if self._initnode else None

        n = next(iterwalk)
        defaultmsg = self._all
        while True:
            if initnode:
                initnode(n)
            rawnode = n.node
            msg = defaultmsg
            if rawnode is root:
                msg = True
                if selectroot:
                    yield process(n)
            elif matchfunc(n):
                msg = True
                yield process(n)
            try:
                n = send(msg)
            except StopIteration:
                break

    def initnode(self, node):
        """Node Initialization

        Do any initialization tasks based on node

        """

    def match(self, node):
        """Determine if node and its children should be selected."""
        return True

    def process(self, node):
        """Do some processing of the node

        This method is meant to be overridden in subclasses.

        """
        return node


# ============================================================================
# NearestDef
# ============================================================================


class NearestTopBlock(SelectASTNodes):
    """Find the nearest top-level block"""

    def __init__(self, node, lineno):
        super().__init__(node, replace=True, selectall=False,
                         initnode=False)
        self.lineno = lineno
        self.col_offset = None

    def __call__(self):
        found = None
        for f in super().__call__():
            if found is None or f.lineno > found.lineno:
                found = f
        return found

    def match(self, node):
        """TODO: Docstring for match."""
        rawnode = node.node
        return (
            isinstance(rawnode, BLOCKTYPES) and
            rawnode.col_offset == 0 and rawnode.lineno <= self.lineno
        )


class NearestDef(SelectASTNodes):
    """Find the nearest function/class definition"""

    def __init__(self, node, lineno):
        findblock = NearestTopBlock(node, lineno)
        block = findblock()
        selectroot = True
        if not isinstance(block, (ast.FunctionDef, ast.ClassDef)):
            block = node
            selectroot = False
        super().__init__(block, replace=False, selectall=True,
                         selectroot=selectroot, initnode=True)
        self.lineno = lineno
        self.col_offset = None

    def __call__(self):
        if self._node is None:
            return None
        found = None
        allfound = list(super().__call__())
        col_offset = self.col_offset
        for f in allfound:
            if found is None or f.lineno > found.lineno:
                if col_offset is None or f.col_offset <= col_offset:
                    found = f
        if found is None:
            return None
        return self._goparent(found)

    def initnode(self, node):
        """TODO: Docstring for initnode."""
        rawnode = node.node
        if isinstance(rawnode, ast.stmt) and rawnode.lineno == self.lineno:
            self.col_offset = rawnode.col_offset

    def match(self, node):
        """TODO: Docstring for match."""
        rawnode = node.node
        return (
            isinstance(rawnode, (ast.FunctionDef, ast.ClassDef)) and
            rawnode.lineno <= self.lineno
        )

    def _goparent(self, node):
        """asdsad"""
        retnode = node
        cur = node
        parent = cur.parent
        while parent:
            if isinstance(parent.node, ast.FunctionDef):
                retnode = parent
            cur = parent
            parent = cur.parent
        return retnode


class NearestTestDef(NearestDef):
    """TODO: to be defined"""

    def __init__(self, node, lineno, *, defglob='test*',
                 clsglob='Test*'):
        super().__init__(node, lineno)
        self._defglob = defglob
        self._clsglob = clsglob

    def match(self, node):
        """TODO: Docstring for match."""
        rawnode = node.node
        match = super().match(node)
        if not match:
            return False
        glob = (self._defglob if isinstance(rawnode, ast.FunctionDef)
                else self._clsglob)
        return fnmatch(rawnode.name, glob)


# ============================================================================
#
# ============================================================================
