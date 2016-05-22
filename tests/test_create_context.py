#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
tests for find/select
"""
import pytest

from pyang.statements import Statement

from pyangext.utils import create_context

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


@pytest.fixture
def ctx():
    """Creates a context with utility function"""
    return create_context()


@pytest.fixture
def module():
    """Sample container"""
    module = Statement(None, None, None, 'module', 'fixture-test')
    namespace = Statement(module, module, None, 'namespace', 'urn:yang:test')
    prefix = Statement(module, module, None, 'prefix', 'test')

    container = Statement(module, module, None, 'container', 'outer')
    id_ = Statement(module, container, None, 'leaf', 'id')
    type_ = Statement(module, id_, None, 'type', 'int32')
    id_.substmts = [type_]

    name = Statement(module, container, None, 'leaf', 'name')
    type_ = Statement(module, name, None, 'type', 'string')
    name.substmts = [type_]
    container.substmts = [id_, name]

    module.substmts = [namespace, prefix, container]

    return module


def test_created_contex_is_valid(ctx, module):
    """
    context should be created without errors
    after adding a parsed module should not have errors
    """
    ctx.validate()
    assert not ctx.errors
    ctx.add_parsed_module(module)
    assert not ctx.errors


def test_created_can_search(ctx, module):
    """
    context should be able to search added modules
    """
    ctx.add_parsed_module(module)
    assert not ctx.search_module(None, 'fixture-test') == module
