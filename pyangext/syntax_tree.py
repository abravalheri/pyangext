# -*- coding: utf-8 -*-
"""TODO: doc
"""
from collections import namedtuple

from six import StringIO

from pyang.statements import Statement
from pyang.translators import yang

from pyangext import __version__  # noqa
from pyangext.definitions import PREFIX_SEPARATOR

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"

_YangOptions = namedtuple(  # pylint: disable=invalid-name
    '_YangOptions', ('yang_remove_unused_imports', 'yang_canonical'))
_SimpleContext = namedtuple(  # pylint: disable=invalid-name
    '_SimpleContext', ('opts',))
_ctx = _SimpleContext(  # pylint: disable=invalid-name
    _YangOptions(False, True))


class YangBuilder(object):
    # pylint: disable=no-self-use

    def __call__(self, keyword, arg=None, children=None, parent=None):
        children = children or []

        if hasattr(arg, '__iter__') or isinstance(arg, Statement):
            children = arg
            arg = None

        if not hasattr(children, '__iter__'):
            children = [children]

        node = Statement(None, parent, None, keyword, arg)
        node.substmts = children

        return node

    def __getattr__(self, keyword):
        keyword = keyword.replace('__', ':').replace('_', '-')

        def factory(arg=None, children=None, prefix=None, **kwargs):
            node_type = keyword
            if prefix is not None:
                node_type = PREFIX_SEPARATOR.join([prefix, keyword])

            return self.__call__(node_type, arg, children, **kwargs)

        return factory

    def blankline(self):
        return Statement(
            None, None, None, '_comment', '')

    def comment(self, text):
        lines = text.strip().splitlines()
        if len(lines) == 1:
            return Statement(
                None, None, None, '_comment', '// ' + lines[0])

        lines = '\n'.join(['* ' + line for line in lines])
        return Statement(
            None, None, None, '_comment', '/*\n' + lines + '\n*/')

    def dump(self, node, file_obj=None,
             prev_indent='', indent_string='  ', ctx=_ctx):
        """
        """
        _file_obj = file_obj or StringIO()
        yang.emit_stmt(
            ctx, node, _file_obj, 1, None, prev_indent, indent_string)
        return file_obj or (
            _file_obj.getvalue(), _file_obj.close())[0]

builder = YangBuilder()  # pylint: disable=invalid-name
