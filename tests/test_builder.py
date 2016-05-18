#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
tests for YANG builder
"""
import pytest

from pyang.statements import Statement

from pyangext.syntax_tree import ValidationError, YangBuilder

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


@pytest.fixture
def builder():
    """Default YANG AST builder"""
    return YangBuilder()


def test_dump(builder):
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


def test_call(builder):
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


def test_getattr(builder):
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


def test_comment(builder):
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


def test_blankline(builder):
    """
    blank lines should be empty
    """
    blankline = builder.blankline()
    assert builder.dump(blankline).strip() == ''


def test_wrapper_dump(builder):
    """
    dump should correctly print wrapper
    wrapper should dump itself
    """
    module = builder.module('test', [
        builder.prefix('test'),
        builder.namespace('urn:yang:test')
    ])

    assert builder.dump(module).strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )

    assert module.dump().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_wrapper_attribute(builder):
    """
    wrapper should allow direct attribute
    """
    module = builder.module('test')
    module.prefix('test')
    module.namespace('urn:yang:test')

    assert module.dump().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_wrapper_call(builder):
    """
    wrapper should allow direct call
    """
    module = builder('module', 'test')
    module('prefix', 'test')
    module('namespace', 'urn:yang:test')

    assert module.dump().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_mix_builder(builder):
    """
    builder should mix with pyang standard
    """
    module = builder(
        'module', 'test',
        Statement(None, None, None, 'namespace', 'urn:yang:test')
    )
    module('prefix', 'test')

    assert module.dump().strip() == (
        'module test {\n'
        '  namespace "urn:yang:test";\n'
        '  prefix test;\n'
        '}'
    )


def test_statement_without_arg(builder):
    """
    builder should allow bypassing ``arg``  as positional argument,
        in other words, pass ``children`` after ``keyword``
    """
    module = builder('module', 'test', [
        builder.namespace('urn:yang:test'),
        builder.prefix('test'),
        builder.rpc('perform', builder.input(
            builder.leaf('name', builder.type('string'))
        )),
        builder.rpc('eval', builder(
            'input',
            builder.leaf('name', builder.type('string'))
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


def test_builder_unwrap(builder):
    """
    unwrap should return pyang.statements.Statement
    """
    module = builder('module', 'test')
    assert isinstance(module.unwrap(), Statement)


def test_wrapper_validate(builder):
    """
    validate should not allow non top-level statements
    """
    leaf = builder.leaf('name', builder.type('string'))

    with pytest.raises(ValidationError):
        leaf.validate()
