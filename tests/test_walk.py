#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""tests for AST traversal"""

import pytest

from pyang.statements import validate_module

from pyangext.utils import create_context, parse, walk

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


@pytest.fixture
def ctx():
    """Pyang Context for validating modules"""
    return create_context()


@pytest.fixture
def module(ctx):
    """YANG modules without errors or warning"""
    module = parse(
        """
        module test {
            namespace urn:yang:test;
            prefix test;

            revision 2008-01-02 { description "first update"; }

            typedef code {
                type string {
                    length "0..8";
                    pattern "[0-9a-fA-F]*";
                }
            }

            grouping identification {
                leaf part-number { type code; }
                leaf serial-number { type code; }
            }

            leaf name { type string; }
            container id { uses identification; }
        }
        """,
        ctx
    )

    validate_module(ctx, module)

    return module


def test_walk(module):
    """
    should count 3 leaves
    with key=substmts should count 1 uses statement
    with key=i_children should count 0 uses statement (uses are expanded)
    """
    def is_leaf(node):
        """check if node is leaf"""
        return node.keyword == 'leaf'

    assert len(walk(module, is_leaf, key='substmts')) == 3
    assert len(walk(module, is_leaf, key='i_children')) == 3

    def is_uses(node):
        """check if node is uses"""
        return node.keyword == 'uses'

    assert len(walk(module, is_uses, key='substmts')) == 1
    assert len(walk(module, is_uses, key='i_children')) == 0
