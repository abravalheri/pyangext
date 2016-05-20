#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
tests for YANG builder
"""
import pytest

from pyang.statements import Statement

from pyangext.syntax_tree import StatementWrapper, YangBuilder, dump

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


def test_call():
    """
    calling build should build statements
    calling build directly with children should build nested statements
    """
    Y = YangBuilder()

    prefix = Y('prefix', 'test')
    assert dump(prefix).strip() == 'prefix test;'

    extension = Y('ext:c-define', 'INTERFACES')
    assert dump(extension).strip() == 'ext:c-define "INTERFACES";'

    module = Y('module', 'test', [
        Y('namespace', 'urn:yang:test'),
        Y('prefix', 'test'),
    ])
    assert dump(module).strip() == (
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
    Y = YangBuilder()

    prefix = Y.prefix('test')
    assert dump(prefix).strip() == 'prefix test;'

    extension = Y.ext__c_define('INTERFACES')
    assert dump(extension).strip() == 'ext:c-define "INTERFACES";'

    extension = Y.c_define('INTERFACES', prefix='ext')
    assert dump(extension).strip() == 'ext:c-define "INTERFACES";'


def test_comment():
    """
    single line comments should start with double slashs
    """
    Y = YangBuilder()

    comment = Y.comment('comment test')
    assert dump(comment).strip() == '// comment test'

    comment = Y.comment('comment\ntest')
    assert dump(comment).strip() == (
        '/*\n'
        ' * comment\n'
        ' * test\n'
        ' */'
    )


def test_blankline():
    """
    blank lines should be empty
    """
    Y = YangBuilder()

    blankline = Y.blankline()
    assert dump(blankline).strip() == ''


def test_from_tuple():
    """
    should build entire (nested) (sub)trees
    should return argument if it is an StatementWrapper
    should always return StatementWrapper
    should raise ValueError ir argument is not tuple,
        StatementWrapper or Statement
    """
    Y = YangBuilder()

    module = Y.from_tuple(
        ('module', 'test', [
            ('namespace', 'urn:yang:test'),
            ('prefix', 'test'),
            ('leaf', 'data', [('type', 'anyxml')])
        ])
    )

    assert dump(module).strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '  leaf data {\n'
        '    type anyxml;\n'
        '  }\n'
        '}'
    )

    assert id(Y.from_tuple(module)) == id(module)
    assert isinstance(module, StatementWrapper)
    assert isinstance(Y.from_tuple(module.unwrap()), StatementWrapper)

    with pytest.raises(ValueError):
        Y.from_tuple('foobar')


def test_wrapper_dump():
    """
    dump should correctly print wrapper
    wrapper should dump itself
    """
    Y = YangBuilder()

    module = Y.module('test', [
        Y.prefix('test'),
        Y.namespace('urn:yang:test')
    ])

    assert dump(module).strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )

    assert module.dump().strip().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_wrapper_attribute():
    """
    wrapper should allow direct attribute
    """
    Y = YangBuilder()

    module = Y.module('test')
    module.prefix('test')
    module.namespace('urn:yang:test')

    assert module.dump().strip().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_wrapper_call():
    """
    wrapper should allow direct call
    """
    Y = YangBuilder()

    module = Y('module', 'test')
    module('prefix', 'test')
    module('namespace', 'urn:yang:test')

    assert module.dump().strip().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_mix_builder():
    """
    builder should mix with pyang standard
    """
    Y = YangBuilder()

    module = Y(
        'module', 'test',
        Statement(None, None, None, 'namespace', 'urn:yang:test')
    )
    module('prefix', 'test')
    module.append(Y.from_tuple(
        ('leaf', 'data', [('type', 'anyxml')])
    ))

    assert module.dump().strip().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '  leaf data {\n'
        '    type anyxml;\n'
        '  }\n'
        '}'
    )


def test_statement_without_arg():
    """
    Y should allow bypassing ``arg``  as positional argument,
        in other words, pass ``children`` after ``keyword``
    """
    Y = YangBuilder()

    module = Y('module', 'test', [
        Y.namespace('urn:yang:test'),
        Y.prefix('test'),
        Y.rpc('perform', Y.input(
            Y.leaf('name', Y.type('string'))
        )),
        Y.rpc('eval', Y(
            'input',
            Y.leaf('name', Y.type('string'))
        )),
    ])

    assert module.dump().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '  rpc perform {\n'
        '    input {\n'
        '      leaf name {\n'
        '        type string;\n'
        '      }\n'
        '    }\n'
        '  }\n'
        '  rpc eval {\n'
        '    input {\n'
        '      leaf name {\n'
        '        type string;\n'
        '      }\n'
        '    }\n'
        '  }\n'
        '}'
    )
