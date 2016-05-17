#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tests for YANG builder
"""
from pyang.statements import Statement

from pyangext.syntax_tree import builder

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def test_dump():
    """
    dump should correctly print headless pyang.statements.Statement
    dump should correctly print nested pyang.statements.Statement
    """
    prefix = Statement(None, None, None, 'prefix', 'test')
    assert builder.dump(prefix).strip() == 'prefix test;'
    namespace = Statement(None, None, None, 'namespace', 'urn:yang:test')
    module = Statement(None, None, None, 'module', 'test')
    module.substmts = [namespace, prefix]
    assert builder.dump(module).strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_call():
    """
    calling build should build statements
    calling build directly with children should build nested statements
    """
    prefix = builder('prefix', 'test')
    assert builder.dump(prefix).strip() == 'prefix test;'

    extension = builder('ext:c-define', 'INTERFACES')
    assert builder.dump(extension).strip() == 'ext:c-define "INTERFACES";'

    module = builder('module', 'test', [
        builder('namespace', 'urn:yang:test'),
        builder('prefix', 'test'),
    ])
    assert builder.dump(module).strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_getattr():
    """
    calling undefined method build should build statements
    double underscores should be transformed into prefix
    underscore should be transformed into dashes
    explicit prefix as named parameter should work
    """
    prefix = builder.prefix('test')
    assert builder.dump(prefix).strip() == 'prefix test;'

    extension = builder.ext__c_define('INTERFACES')
    assert builder.dump(extension).strip() == 'ext:c-define "INTERFACES";'

    extension = builder.c_define('INTERFACES', prefix='ext')
    assert builder.dump(extension).strip() == 'ext:c-define "INTERFACES";'


def test_comment():
    """
    single line comments should start with double slashs
    """
    comment = builder.comment('comment test')
    assert builder.dump(comment).strip() == '// comment test'

    comment = builder.comment('comment\ntest')
    assert builder.dump(comment).strip() == (
        '/*\n'
        ' * comment\n'
        ' * test\n'
        ' */'
    )


def test_blankline():
    """
    blank lines should be empty
    """
    blankline = builder.blankline()
    assert builder.dump(blankline).strip() == ''
