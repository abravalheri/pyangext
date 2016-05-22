#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
tests for YANG builder
"""
from pyang.statements import Statement

from pyangext.utils import dump

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def test_dump():
    """
    dump should correctly print headless pyang.statements.Statement
    dump should correctly print nested pyang.statements.Statement
    """
    prefix = Statement(None, None, None, 'prefix', 'test')
    assert dump(prefix).strip() == 'prefix test;'
    namespace = Statement(None, None, None, 'namespace', 'urn:yang:test')
    module = Statement(None, None, None, 'module', 'test')
    module.substmts = [namespace, prefix]
    assert dump(module).strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )
