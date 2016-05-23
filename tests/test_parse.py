#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
tests for YANG content to AST conversion
"""
from __future__ import print_function

import warnings

import pytest

from pyang.statements import Statement

from pyangext.utils import create_context, find, parse

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


@pytest.fixture
def ctx():
    """creates a context with custom configuration to print error code."""
    return create_context(max_line_len=140, print_error_code=True)


WITH_WARN = pytest.mark.parametrize('warning_type, text', [
    ('LONG_LINE',
     'module a {'
     'leaf aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
     'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
     'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
     'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa;'
     '}'),
    # YANG parser does not produce several warnings...
])


@WITH_WARN
def test_warn_invalid_string(ctx, warning_type, text):
    """
    parse should warn when something went wrong
    """
    with pytest.warns(SyntaxWarning) as info:
        parse(text, ctx)

    assert warning_type in '\n'.join(str(record.message) for record in info)


@WITH_WARN
def test_raise_invalid_string_if_warning_option(ctx, warning_type, text):
    """
    warns should be transformed in error if warnings option contains 'error'
    """
    ctx.opts.warnings = ['error']
    with pytest.raises(SyntaxError) as info:
        parse(text, ctx)

    assert warning_type in str(info.value)


@WITH_WARN
def test_not_warn_invalid_string_if_none_option(ctx, warning_type, text):
    """
    warns should ignore if warnings option contains 'none'
    """
    ctx.opts.warnings = ['none']
    assert parse(text, ctx)
    print(warning_type)


WITH_ERRORS = pytest.mark.parametrize('error_type, text', [
    ('EXPECTED_ARGUMENT', 'module a { keyword }'),
    ('INCOMPLETE_STATEMENT', 'module a { leaf a { leaf type }'),
    ('EOF_ERROR', '/* unterminated comment'),
    #  this do not need to be exhaustive,
    #  just ensure exceptions are raised
])


@WITH_ERRORS
def test_raise_invalid_string(ctx, error_type, text):
    """
    parse should raise SyntaxErrors
    """
    with pytest.raises(SyntaxError) as info:
        parse(text, ctx)
    assert error_type in str(info.value)


@WITH_ERRORS
def test_not_raise_invalid_string_if_ignore_option(ctx, error_type, text):
    """
    No exception should be raised if ignore_errors option is true
    But no tree is generated
    """
    ctx.opts.ignore_errors = True
    assert parse(text, ctx) is None
    print(error_type)


@WITH_ERRORS
def test_not_raise_invalid_string_if_ignore_tag(ctx, error_type, text):
    """
    No exception should be raised if ignore_errors_tags contain error type
    But no tree is generated
    """
    ctx.opts.ignore_error_tags = [error_type]
    assert parse(text, ctx) is None


@pytest.mark.parametrize('text', [
    'leaf id { type int32; }',
    'container user { leaf name { type string; } }',
    'description "BEST DESCRIPTION EVER!!";',
    '// this is a single line comment\nleaf name { type string; }',
    '/* this is a\nmulti-line\ncomment */leaf name { type string; }',
    # this do not need to be exhaustive,
    # just parser produce Statement
])
def test_parse_valid_string(text):
    """
    should parse valid YANG string into Statement
    """
    assert isinstance(parse(text), Statement)


@pytest.fixture
def ok_yang():
    """YANG modules without errors or warning"""
    return """
        module test {
            namespace urn:yang:test;
            prefix test;

            revision 2008-01-02 {
                description "first update";
            }

            leaf name {
                type string {
                    length "0..8";
                    pattern "[0-9a-fA-F]*";
                }
            }
        }
    """


def test_parse_nested(ok_yang):
    """
    should parse all nested statements
    """
    with warnings.catch_warnings(record=True) as info:
        module = parse(ok_yang)
        assert find(module, 'namespace', 'urn:yang:test')
        assert find(module, 'prefix', 'test')
        revision = find(module, 'revision', '2008-01-02')[0]
        assert find(revision, 'description', 'first update')
        leaf = find(module, 'leaf', 'name')[0]
        leaf_type = find(leaf, 'type', 'string')[0]
        assert find(leaf_type, 'length', '0..8')
        assert find(leaf_type, 'pattern', '[0-9a-fA-F]*')

    assert not info


def test_parse_from_file(tmpdir, ok_yang):
    """
    should parse content from file if first argument is file
    """
    yang_file = tmpdir.join('test')
    yang_file.write(ok_yang)
    test_parse_nested(str(yang_file))
