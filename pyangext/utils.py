# -*- coding: utf-8 -*-
"""Utility belt for working with ``pyang`` and ``pyangext``."""

from pyang import Context, FileRepository

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
