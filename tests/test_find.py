#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
tests for find/select
"""
import pytest

from pyang.statements import Statement
from pyangext.utils import find

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


@pytest.fixture
def container():
    """Sample container"""
    container = Statement(None, None, None, 'container', 'outer')
    id_ = Statement(None, container, None, 'leaf', 'id')
    type_ = Statement(None, id_, None, 'type', 'int32')
    id_.substmts = [type_]
    name = Statement(None, container, None, 'leaf', 'name')
    type_ = Statement(None, name, None, 'type', 'string')
    name.substmts = [type_]
    container.substmts = [id_, name]

    return container


def test_find(container):
    """
    should find direct substatements by keyword + arg
    should find direct substatements by keyword
    should find direct substatements by arg
    should return StatementWrapper
    should not ignore prefix if no ``ignore_prefix`` were passed
    should ignore prefix in keyword if ``ignore_prefix`` were passed
    should ignore prefix in arg if ``ignore_prefix`` were passed
    """
    assert find(container, 'leaf', 'name')

    assert len(find(container, 'leaf')) == 2

    name = find(container, arg='name')
    assert name

    container.substmts.append(
        Statement(None, container, None, 'ext:myext', 'ext:value'))
    assert not find(container, 'myext')
    assert not find(container, arg='value')
    assert find(container, 'myext', ignore_prefix=True)
    assert find(container, arg='value', ignore_prefix=True)
