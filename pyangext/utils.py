# -*- coding: utf-8 -*-
"""TODO: doc
"""
from six.moves import reduce  # pylint: disable=redefined-builtin

import inflection

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def prefixify(name, separator='-'):
    return inflection.parameterize(
        name, separator
    ).replace(
        'http-', ''
    ).replace(
        'urn-', ''
    )


def merge_dicts(*dicts):
    return reduce(lambda acc, x: acc.update(x) or acc, dicts, {})


def merge_lists(*lists):
    return reduce(lambda acc, x: acc.extend(x) or acc, lists, [])
