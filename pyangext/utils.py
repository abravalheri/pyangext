# -*- coding: utf-8 -*-
"""Utility belt for working with ``pyang`` and ``pyangext``."""
import io
import logging
from os.path import isfile
from warnings import warn

from six import StringIO

from pyang import Context, FileRepository
from pyang.error import err_level, err_to_str, error_codes
from pyang.translators import yang
from pyang.yang_parser import YangParser

from .definitions import PREFIX_SEPARATOR

__all__ = [
    'create_context',
    'compare_prefixed',
    'select',
    'find',
    'dump',
    'check',
    'parse',
]

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)
LOGGER = logging.getLogger(__name__)

DEFAULT_OPTIONS = {
    'path': [],
    'deviations': [],
    'features': [],
    'format': 'yang',
    'keep_comments': True,
    'no_path_recurse': False,
    'trim_yin': False,
    'yang_canonical': False,
    'yang_remove_unused_imports': False,
    # -- errors
    'ignore_error_tags': [],
    'ignore_errors': [],
    'list_errors': True,
    'print_error_code': False,
    'errors': [],
    'warnings': [code for code, desc in error_codes.items() if desc[0] > 4],
    'verbose': True,
}
"""Default options for pyang command line"""

_COPY_OPTIONS = [
    'canonical',
    'max_line_len',
    'max_identifier_len',
    'trim_yin',
    'lax_xpath_checks',
    'strict',
]
"""copy options to pyang context options"""


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


def _parse_features_string(feature_str):
    if feature_str.find(':') == -1:
        return (feature_str, [])

    [module_name, rest] = feature_str.split(':', 1)
    if rest == '':
        return (module_name, [])

    features = rest.split(',')
    return (module_name, features)


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

    for attr in _COPY_OPTIONS:
        setattr(ctx, attr, getattr(opts, attr))

    # make a map of features to support, per module (taken from pyang bin)
    for feature_name in opts.features:
        (module_name, features) = _parse_features_string(feature_name)
        ctx.features[module_name] = features

    # apply deviations (taken from pyang bin)
    for file_name in opts.deviations:
        with io.open(file_name, "r", encoding="utf-8") as fd:
            module = ctx.add_module(file_name, fd.read())
            if module is not None:
                ctx.deviation_modules.append(module)

    return ctx


def qualify_str(arg, prefix_sep=PREFIX_SEPARATOR):
    """Transform prefixed strings in tuple ``(prefix, string)``"""
    response = arg if isinstance(arg, tuple) else tuple(arg.split(prefix_sep))
    if len(response) == 2:
        return response

    return ('', response[0])


def compare_prefixed(arg1, arg2,
                     prefix_sep=PREFIX_SEPARATOR, ignore_prefix=False):
    """Compare 2 arguments : prefixed strings or tuple ``(prefix, string)``

    Arguments:
        arg1 (str or tuple): first argument
        arg2 (str or tuple): first argument
        prefix_sep (str): prefix string separator (default: ``':'``)

    Returns:
        bool
    """
    cmp1 = qualify_str(arg1, prefix_sep=prefix_sep)
    cmp2 = qualify_str(arg2, prefix_sep=prefix_sep)

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

    .. seealso:: function :func:`select`
    """
    return select(parent.substmts, keyword, arg, ignore_prefix)


def walk(parent, select=lambda x: x, apply=lambda x: x, key='substmts'):
    # pylint: disable=redefined-builtin,redefined-outer-name
    """Recursivelly find nodes and/or apply a function to them.

    Arguments:
        parent (pyang.statements.Statement): root of the subtree were
            the search will take place.
        select: optional callable that receives a node and returns a bool
            (True if the node matches the criteria)
        apply: optional callable that are going to be applied to the node
            if it matches the criteria
        key (str): property where the children nodes are stored,
            default is ``substmts``

    Returns:
        list: results collected from the apply function
    """
    results = []
    if select(parent):
        results.append(apply(parent))

    if hasattr(parent, key):
        children = getattr(parent, key)
        for child in children:
            results.extend(walk(child, select, apply, key))

    return results


def dump(node, file_obj=None, prev_indent='', indent_string='  ', ctx=None):
    """Generate a string representation of an abstract syntax tree.

    Arguments:
        node (pyang.statements.Statement): object to be represented
        file_obj (file): *file-like* object where the representation
            will be dumped. If nothing is passed, the method returns
            a string

    Keyword Arguments:
        prev_indent (str): string to be added to the produced indentation
        indent_string (str): string to be used as indentation
        ctx (pyang.Context): context object used to generate string
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

    # one-liners <3: if no file_obj get buffer content and close it!
    return file_obj or (_file_obj.getvalue(), _file_obj.close())[0]


def check(ctx, rescue=False):
    """Check existence of errors or warnings in context.

    Code mostly borrowed from ``pyang`` script.

    Arguments:
        ctx (pyang.Context): pyang context to be checked.

    Keyword Arguments:
        rescue (bool): if ``True``, no exception/warning will be raised.

    Raises:
        SyntaxError: if errors detected

    Warnings:
        SyntaxWarning: if warnings detected

    Returns:
        tuple: (list of errors, list of warnings), if ``rescue`` is ``True``
    """
    errors = []
    warnings = []
    opts = ctx.opts

    if opts.ignore_errors:
        return (errors, warnings)

    for (epos, etag, eargs) in ctx.errors:
        if (hasattr(opts, 'ignore_error_tags') and
                etag in opts.ignore_error_tags):
            continue
        if not ctx.implicit_errors and hasattr(epos.top, 'i_modulename'):
            # this module was added implicitly (by import); skip this error
            # the code includes submodules
            continue
        elevel = err_level(etag)  # elevel 4 -> warning
        explain = err_to_str(etag, eargs)
        reason = etag if opts.print_error_code else explain
        if 'unexpected keyword "description"' in reason:
            # TODO: WTF pyang bug??
            elevel = 4
        message = '({}) {}'.format(str(epos), reason)
        if (elevel >= 4 or etag in opts.warnings) and etag not in opts.errors:
            if 'error' in opts.warnings and etag not in opts.warnings:
                pass
            elif 'none' in opts.warnings:
                continue
            else:
                warnings.append(message)
                continue

        errors.append(message)

    if rescue:
        return (errors, warnings)

    if warnings:
        for message in warnings:
            warn(message, SyntaxWarning)

    if errors:
        raise SyntaxError('\n'.join(errors))

    return (errors, warnings)


def parse(text, ctx=None):
    """Parse a YANG statement into an Abstract Syntax Tree

    Arguments:
        text (str): file name for a YANG module or text
        ctx (optional pyang.Context): context used to validate text

    Returns:
        pyang.statements.Statement
    """
    parser = YangParser()

    filename = 'parser-input'

    ctx_ = ctx or create_context()

    if isfile(text):
        filename = text
        with open(filename, 'r') as fp:
            text = fp.read()

    # ensure reported errors are just from parsing
    old_errors = ctx_.errors
    ctx_.errors = []

    ast = parser.parse(ctx_, filename, text)

    # look for errors and warnings
    check(ctx_)

    # restore other errors
    ctx_.errors = old_errors

    return ast
