#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automatically discover pyang plugins by reading setuptools entry-points."""

import sys
from os import environ
from os.path import dirname, pathsep

import pkg_resources

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"

__all__ = ['discover', 'expanded']


def discover():
    """Discovers pyang plugins registered using setuptools entry points.

    Collects the path for all python modules that have functions
    registered as an entry point inside ``yang.plugins`` group.

    Ideally the function registered should be named ``pyang_plugin_init``.
    It is also important to not include non-pyang-plugin python modules
    in the same directory of this module.

    Returns:
        Array of paths that contains python modules with pyang plugins.

    Reference:
        https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
    """

    dirs = []
    for plugin in pkg_resources.iter_entry_points('pyang.plugins'):
        try:
            dirs.append(
                dirname(sys.modules[plugin.load().__module__].__file__))
        except (KeyError, AttributeError):
            pass

    return dirs


def expanded():
    """Combines the autodiscovered plugin paths with env ``PYANG_PLUGINPATH``.

    This function appends paths discovered using ``discover`` function
    to the list provided by ``PYANG_PLUGINPATH`` environment variable.
    It also removes duplicated entries from the resulting list.

    Returns:
        Array of paths that contains python modules with pyang plugins.
    """
    original = environ.get('PYANG_PLUGINPATH', '').split(pathsep)
    registered = discover()

    new = original + registered
    seen = set()
    seen_add = seen.add
    return [
        path
        for path in new
        if path and not (path in seen or seen_add(path))
    ]
