# -*- coding: utf-8 -*-
"""Tools for programmatic generation of a YANG Abstract Syntax Tree."""
from six import StringIO

from pyang import statements as st
from pyang.error import Position
from pyang.translators import yang

from pyangext import __version__  # noqa
from pyangext.definitions import PREFIX_SEPARATOR
from pyangext.utils import compare_prefixed, create_context

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def select(statements, keyword=None, arg=None, ignore_prefix=False):
    """Given a list of statements filter by keyword, or argument or both.

    Arguments:
        statements (list of pyang.statements.Statement):
            list of statements to be filtered.
        keyword (str): if specified the statements should have this keyword
        arg (str): if specified the statements should have this argument

    ``keyword`` and ``arg`` can be also used as keyword arguments.

    Returns:
        list: nodes that matches the conditions
    """
    response = []
    for item in statements:
        if isinstance(item, StatementWrapper):
            item = item._statement

        if (keyword and keyword != item.keyword and
                not compare_prefixed(
                    keyword, item.raw_keyword, ignore_prefix=ignore_prefix)):
            continue

        if (arg and arg != item.arg and
                not compare_prefixed(
                    arg, item.arg, ignore_prefix=ignore_prefix)):
            continue

        response.append(item)

    return response


def find(parent, keyword=None, arg=None, ignore_prefix=False):
    """Select all sub-statements by keyword, or argument or both.

    See :func:`select`
    """
    if isinstance(parent, StatementWrapper):
        parent = parent._statement

    return select(parent, keyword, arg, ignore_prefix)


def dump(node, file_obj=None, prev_indent='', indent_string='  ', ctx=None):
    """Generate a string representation of an abstract syntax tree.

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

    if isinstance(node, StatementWrapper):
        node = node._statement

    # process AST
    yang.emit_stmt(
        ctx or create_context(), node, _file_obj, 1, None,
        prev_indent, indent_string)

    # oneliners <3: if no file_obj get buffer content and close it!
    return file_obj or (_file_obj.getvalue(), _file_obj.close())[0]


class YangBuilder(object):
    """YANG Statement generator factory.

    YANG Builder provides an easy way of generating and printing
    Abstract Syntax Trees.

    If an undefined method is called from builder, the name of the
    method is used as keyword for the statement. Underscore are replaced
    by dashes and duble underscores denote separation of a prefix::

        >>> from pyangext.syntax_tree import YangBuilder
        >>> Y = YangBuilder('desired-module-name')
        >>> Y.leaf_list('allow-user', [
                Y.type('string'), Y.description('username')
            ]).dump()
        # => 'leaf-list allow-user {
        #       type string;
        #       description "username";
        #     }'
        >>> Y.ext__c_define(
                'INTERFACES', Y.if_feature('local-storage')).dump()
        # => 'ext:c-define "INTERFACES" {
        #       if-feature local-storage;
        #     }'

    When the builder itself is called, the first argument is used as
    keyword for the statement and the second is used as its argument.
    Optional children and parent nodes can be passed::

        >>> Y('ext:c-define', 'INTERFACES',
                     Y.if_feature('local-storage')).dump()
        # => 'ext:c-define "INTERFACES" {
        #       if-feature local-storage;
        #     }'

    Note that Builder is stateful, it means it cannot be shared among
    threads or even used to build multiple trees simultaneously.

    The prefered way of building ASTs is by passing children as argument,
    but is also possible to delay the children creation::

        >>> tl = Y.leaf_list('text-lines')
        >>> tl.type('string')
        >>> tl.description('lines of a text')
        >>> tl.dump()
        # => 'leaf-list text-lines {
        #       type string;
        #       description "lines of a text";
        #     }'

    """
    def __init__(self, name='builder-generated', top=None, keyword='module'):
        """Initialize builder.

        Arguments:
            name (str): desired name for a hypothetical output module.
            top (pyang.statements.Statement): outer-most statement
                (useful for sub-trees)
        """
        self._pos = (top and top.pos) or Position(name)

        # Creates a dummy outermost module statement to simplify
        # traversing tree logic
        self._top = top or st.Statement(None, None, self._pos, 'module', name)

        if not self._pos.top:
            self._pos.top = self._top

    def __call__(self, keyword, arg=None, children=None, parent=None):
        """Magic method to generate YANG statements.

        Arguments:
            keyword (str): string to be used as keyword for the statement
            arg (str): argument of the statement

        Keyword Arguments:
            children: optional statement or list to be inserted as substatement
            parent (pyang.statements.Statement): optional parent statement

        Returns:
            StatementWrapper: wrapper around ``pyang.statements.Statement``.
                call ``unwrap`` if direct access is necessary.
        """
        children = children or []

        if isinstance(arg, (list, tuple, st.Statement, StatementWrapper)):
            children = arg
            arg = None

        if not isinstance(children, (list, tuple)):
            children = [children]

        if keyword in ('module', 'submodule'):
            node = self._top
            node.keyword = keyword
            node.arg = arg
            node.i_module = node
        else:
            parent_node = (
                parent._statement
                if isinstance(parent, StatementWrapper)
                else parent
            )

            node = st.Statement(
                self._top, parent_node, self._top.pos, keyword, arg)
            node.i_module = self._top

        unwraped_children = []
        for child in children:
            if isinstance(child, StatementWrapper):
                unwraped = child._statement
            else:
                unwraped = child
            unwraped.parent = node
            unwraped_children.append(unwraped)

        node.substmts = unwraped_children

        return StatementWrapper(node, self)

    def __getattr__(self, keyword):
        """Magic method to generate YANG statements."""
        keyword = keyword.replace('__', ':').replace('_', '-')
        build = self.__call__

        def _factory(arg=None, children=None, prefix=None, **kwargs):
            node_type = keyword
            if prefix is not None:
                node_type = PREFIX_SEPARATOR.join([prefix, keyword])

            return build(node_type, arg, children, **kwargs)

        return _factory

    def blankline(self):
        """Insert a empty line."""
        return self.__call__('_comment', '')

    def comment(self, text):
        """Generate a comment node.

        Arguments:
            text (str): content of the comment
        """
        lines = text.strip().splitlines()
        if len(lines) == 1:
            text = '// ' + lines[0]
        else:
            text = (
                '/*\n' +
                '\n'.join(['* ' + line for line in lines]) +
                '\n*/'
            )

        return self.__call__('_comment', text)

    def from_tuple(self, texp, parent=None):
        """Generates a YANG statement form a tuple-expression

        Here the tuple-expression is considered a tuple (nested or not)
        in the form::

            (<keyword>, <arg>, <children>)

        Consider the following YANG statement::

            container error {
              leaf code { type int32; }
              leaf message { type string; }
            }

        The equivalent tuple-expression is::

            ('container', 'error', [
                ('leaf', 'code', [('type', 'int32')]),
                ('leaf', 'message', [('type', 'string')]),
            ])

        For comments use ``_comment``.
        Note that children should be a list

        Arguments:
            texp (tuple): tuple-expression representation of statement
            parent (pyang.statements.Statement): optional parent statement

        Example:
            The statement `leaf counter { type int32; }` can be generated by::

                builder.from_tuple(('leaf', 'counter', [('type', 'int32')]))

        See :meth:`YangBuilder.__call__`.
        """
        if isinstance(texp, st.Statement):
            return StatementWrapper(texp, self)

        if isinstance(texp, StatementWrapper):
            return texp

        if not isinstance(texp, tuple):
            raise ValueError(
                'argument should be tuple, %d given', type(texp))

        last = texp[-1]
        if isinstance(last, list):
            node = self(*texp[:-1], parent=parent)
            for child in last:
                node.append(self.from_tuple(child, parent=node))

            return node

        return self(*texp, parent=parent)


class ValidationError(RuntimeError):
    """Validation not alowed"""
    pass


class StatementWrapper(object):
    def __init__(self, statement, builder):
        """Create a builder wrapper around ``pyang.statements.Statement``.

        This wrapper can be used to generate substatements, or dump the
        syntax tree as a YANG string representation.

        Example:
        ::
            >>> from pyangext.syntax_tree import YangBuilder
            >>> Y = YangBuilder('desired-module-name')
            >>> wrapper = Y.leaf_list('allow-user')
            >>> wrapper.type('string')
            >>> wrapper.dump()
            # => 'leaf-list allow-user {
            #       type string;
            #     }'
        """
        self._statement = statement
        self._builder = builder

    def __call__(self, *args, **kwargs):
        """Call ``__call__`` from builder, adding result as substatement.

        See :meth:`YangBuilder.__call__`.
        """
        kwargs.setdefault('parent', self._statement)
        other_wrapper = self._builder.__call__(*args, **kwargs)
        self._statement.substmts.append(other_wrapper._statement)

        return other_wrapper

    def __getattr__(self, name):
        """Call ``__getattr__`` from builder, adding result as substatement.

        See :meth:`YangBuilder.__getattr__`.
        """
        method = self._builder.__getattr__(name)
        parent = self._statement

        def _call(*args, **kwargs):
            kwargs.setdefault('parent', self._statement)
            other_wrapper = method(*args, **kwargs)
            parent.substmts.append(other_wrapper._statement)

            return other_wrapper

        return _call

    def dump(self, *args, **kwargs):
        """Returns the string representation of the YANG module.

        See :func:`dump`.
        """
        return dump(self._statement, *args, **kwargs)

    def find(self, *args, **kwargs):
        """Find by a substatement by keyword, or argument or both.

        See :func:`select`.
        """
        children = select(self._statement.substmts, *args, **kwargs)
        return [type(self)(child, self._builder) for child in children]

    def unwrap(self):
        """Retrieve the inner ``pyang.statements.Statement`` object"""
        return self._statement

    def append(self, *children, **kwargs):
        """
        Add children statements

        Arguments:
            *children (pyang.statements.Statements): substatements to be added

        Keyword Arguments:
            copy (boolean): If true, the node will be copied and not modified
                in place

        Returns:
            StatementWrapper: wrapper itself
        """
        statement = self._statement
        substatements = statement.substmts
        copy = kwargs.get('copy')

        for child in children:
            sub = (
                child._statement if isinstance(child, StatementWrapper)
                else child
            )
            if copy:
                sub = sub.copy(statement)
            else:
                sub.parent = statement
            substatements.append(sub)

        return self

    def validate(self, ctx=None):
        """Validates the syntax tree.

        Should be called just from ``module``, ``submodule`` statements.

        Arguments:
            ctx (pyang.Context): object generated from pyang parsing
        """
        node = self._statement
        if node.keyword not in ('module', 'submodule'):
            raise ValidationError(
                'Cannot validate `%d`, only top-level statements '
                '(module, submodule)', node.keyword)

        st.validate_module(ctx or create_context(), node)

        return node.i_is_validated

    def __repr__(self):
        """Unique representation for debugging purposes."""
        node = self._statement
        return '<{}.{}({} "{}") at {}>'.format(
            self.__module__, type(self).__name__,
            node.keyword, node.arg, hex(id(self)))
