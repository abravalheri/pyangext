#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # pylint: disable=redefined-outer-name
"""
tests for pyangext cli.call
"""
import os

from pyangext.paths import discover, expanded

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def test_discover(dummy_plugin_dir, register_dummy_plugin):
    """
    discover should include the directory of a plugin
        registered as entry_point
    """
    register_dummy_plugin()
    locations = discover()
    assert dummy_plugin_dir in locations


def test_expanded(dummy_plugin_dir, register_dummy_plugin):
    """
    expanded should contain PYANG_PLUGINPATH
    expanded should keep order with PYANG_PLUGINPATH in the begining
    expanded should not contain duplicated values
    """
    register_dummy_plugin()
    os.environ['PYANG_PLUGINPATH'] = '/abc'
    locations = expanded()
    assert dummy_plugin_dir in locations
    assert '/abc' in locations

    os.environ['PYANG_PLUGINPATH'] = '/abc:/def'
    locations = expanded()
    assert locations[0] == '/abc'
    assert locations[1] == '/def'
    assert locations[2] == dummy_plugin_dir

    os.environ['PYANG_PLUGINPATH'] = '/abc:/abc'
    locations = expanded()
    assert locations.count('/abc') == 1
