# -*- coding: utf-8 -*-
"""Utility belt for working with ``pyang`` and ``pyangext``."""
from six import StringIO

from pyang import Context, FileRepository
from pyang.translators import yang

from .definitions import PREFIX_SEPARATOR

__all__ = ['create_context', 'compare_prefixed', 'select', 'find', 'dump']

DEFAULT_OPTIONS = {
    'format': 'yang',
    'verbose': True,
    'list_errors': True,
    'print_error_code': True,
    'yang_remove_unused_imports': True,
    'yang_canonical': True,
    'trim_yin': False,
    'keep_comments': True,
    'features': [],
    'deviations': [],
    'path': [],
}
"""Default options for pyang command line"""

DEFAULT_ATTRIBUTES = {
    'trim_yin': False,
}
"""Default parameters for pyang context"""


class objectify(object):  # pylint: disable=invalid-name
    """Utility for providing object access syntax (.attr) to dicts"""

    def __init__(self, *args, **kwargs):
        for entry in args:
            self.__dict__.update(entry)

        self.__dict__.update(kwargs)

    def __getattr__(self, _):
        return None

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value


def create_context(path='.', *options, **kwargs):
    """Generates a pyang context

    Arguments:
        path (str): location of YANG modules.
        *options: list of dicts, with options to be passed to context.
        **kwargs: similar to ``options`` but have a higher precedence.

    Returns:
        pyang.Context: Context object for ``pyang`` usage
    """

    opts = objectify(DEFAULT_OPTIONS, *options, **kwargs)
    repo = FileRepository(path, no_path_recurse=opts.no_path_recurse)
    ctx = Context(repo)
    ctx.opts = opts

    for attr, value in DEFAULT_ATTRIBUTES.items():
        setattr(ctx, attr, value)

    return ctx


def compare_prefixed(arg1, arg2,
                     prefix_sep=PREFIX_SEPARATOR, ignore_prefix=False):
    """Compare 2 arguments : prefixed strings or tuple ``(prefix, string)``

    Arguments:
        arg1 (str or tuple): first argument
        arg2 (str or tuple): first argument
        prefix_sep (str): prefix string separator (default: ``':'``)

    Returns:
        boolean
    """
    cmp1 = arg1 if isinstance(arg1, tuple) else tuple(arg1.split(prefix_sep))
    cmp2 = arg2 if isinstance(arg2, tuple) else tuple(arg2.split(prefix_sep))

    if ignore_prefix:
        return cmp1[-1:] == cmp2[-1:]

    return cmp1 == cmp2


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
    return select(parent.substmts, keyword, arg, ignore_prefix)


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

    # process AST
    yang.emit_stmt(
        ctx or create_context(), node, _file_obj, 1, None,
        prev_indent, indent_string)

    # oneliners <3: if no file_obj get buffer content and close it!
    return file_obj or (_file_obj.getvalue(), _file_obj.close())[0]
