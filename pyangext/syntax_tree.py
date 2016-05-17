# -*- coding: utf-8 -*-
"""Tools for programmatic generation of a YANG Abstract Syntax Tree."""
from collections import namedtuple

from six import StringIO

from pyang.statements import Statement
from pyang.translators import yang

from pyangext import __version__  # noqa
from pyangext.definitions import PREFIX_SEPARATOR

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"

# Mock context and CLI options objects to allow `emit_yang`usage
_YangOptions = namedtuple(  # pylint: disable=invalid-name
    '_YangOptions', ('yang_remove_unused_imports', 'yang_canonical'))
_SimpleContext = namedtuple(  # pylint: disable=invalid-name
    '_SimpleContext', ('opts',))
_ctx = _SimpleContext(  # pylint: disable=invalid-name
    _YangOptions(False, True))


class YangBuilder(object):
    """YANG Statement generator factory.

    YANG Builder provides an easy way of generating and printing
    Abstract Syntax Trees.

    If an undefined method is called from builder, the name of the
    method is used as keyword for the statement. Underscore are replaced
    by dashes and duble underscores denote separation of a prefix::

        >>> from pyangext.syntax_tree import builder as Y
        >>> Y.dump(Y.leaf_list('allow-user', [
                Y.type('string'), Y.description('username')
            ]))
        # => "leaf-list allow-user {
        #       type string;
        #       description "username";
        #     }"
        >>> Y.dump(Y.ext__c_define(
                'INTERFACES', Y.if_feature('local-storage')))
        # => "ext:c-define INTERFACES {
        #       if-feature local-storage;
        #     }"

    When the builder itself is called, the first argument is used as
    keyword for the statement and the second is used as its argument.
    Optional children and parent nodes can be passed::

        >>> Y.dump(Y('ext:c-define', 'INTERFACES',
                     Y.if_feature('local-storage')))
        # => "ext:c-define INTERFACES {
        #       if-feature local-storage;
        #     }"

    """
    # pylint: disable=no-self-use

    def __call__(self, keyword, arg=None, children=None, parent=None):
        """Magic method to generate YANG statements.

        Arguments:
            keyword (str): string to be used as keyword for the statement
            arg (str): argument of the statement

        Keyword Arguments:
            children (list[pyang.statements.Statement]): optional statement
                or list to be inserted as substatement
            parent (pyang.statements.Statement): optional parent statement

        Returns: pyang.statements.Statement
        """
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
        """Magic method to generate YANG statements."""
        keyword = keyword.replace('__', ':').replace('_', '-')

        def _factory(arg=None, children=None, prefix=None, **kwargs):
            node_type = keyword
            if prefix is not None:
                node_type = PREFIX_SEPARATOR.join([prefix, keyword])

            return self.__call__(node_type, arg, children, **kwargs)

        return _factory

    def blankline(self):
        """Insert a empty line."""
        return Statement(
            None, None, None, '_comment', '')

    def comment(self, text):
        """Generate a comment node.

        Arguments:
            text (str): content of the comment
        """
        lines = text.strip().splitlines()
        if len(lines) == 1:
            return Statement(
                None, None, None, '_comment', '// ' + lines[0])

        lines = '\n'.join(['* ' + line for line in lines])
        return Statement(
            None, None, None, '_comment', '/*\n' + lines + '\n*/')

    def dump(
            self, node, file_obj=None,
            prev_indent='', indent_string='  ', ctx=_ctx):
        """Generate a string representation of the abstract syntax tree.

        Arguments:
            node (pyang.statements.Statement): object to be represented
            file_obj (file): *file-like* object where the representation
                will be dumped. If nothing is passed, the method returns
                a string

        Keyword Arguments:
            prev_indent (str): string to be added to the produced identation
            indent_string (str): string to be used as identation
            ctx (pyang.Context): contex object used to generate string
                representation. If no context is passed, a dummy object
                is used with default configuration

        Returns:
            str: text content if ``file_obj`` is not specified
        """
        # create a buffer to allow string return if no file_obj given
        _file_obj = file_obj or StringIO()

        # process AST
        yang.emit_stmt(
            ctx, node, _file_obj, 1, None, prev_indent, indent_string)

        # oneliners <3: if no file_obj get buffer content and close it!
        return file_obj or (_file_obj.getvalue(), _file_obj.close())[0]

builder = YangBuilder()  # pylint: disable=invalid-name
"""Element factory object."""
