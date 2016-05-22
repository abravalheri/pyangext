#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for pyangext.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
from __future__ import absolute_import, division, print_function

import sys
from textwrap import dedent

import pkg_resources

import pytest
from mock import MagicMock


@pytest.fixture(scope='session')
def example_module(tmpdir_factory):
    """Creates a sample YANG file"""
    location = tmpdir_factory.mktemp("examples")
    example = location.join("example-module.yang")
    example.write(dedent("""\
        module example-module {
          namespace "urn:yang:example:module";
          prefix em;
        }"""))

    return str(example.realpath())


@pytest.fixture(scope='session')
def dummy_plugin_content():
    """Dummy pyang content that dumps the contents of a parameter"""
    return dedent("""\
        import optparse
        from pyang import plugin

        def pyang_plugin_init():
            plugin.register_plugin(FakeFixturePlugin())

        class FakeFixturePlugin(plugin.PyangPlugin):
            def add_opts(self, optparser):
                g = optparser.add_option_group("FakeFixture Plugin Options")
                g.add_options([
                    optparse.make_option(
                        "--fake-fixture-option", default="Hello World!")
                ])

            def add_output_format(self, fmts):
                    self.multiple_modules = True
                    fmts['fake-fixture'] = self

            def emit(self, ctx, modules, fd):
                fd.write(ctx.opts.fake_fixture_option)""")


@pytest.fixture(scope='session')
def dummy_plugin_dir(tmpdir_factory, dummy_plugin_content):
    """Creates a temp directory with a dummy plugin inside"""
    location = tmpdir_factory.mktemp("plugins")
    location.join("fake_fixture_plugin.py").write(dummy_plugin_content)

    return str(location.realpath())


@pytest.fixture
def register_dummy_plugin(dummy_plugin_dir, monkeypatch):
    """Make entry point always include the dummy plugin"""
    # pylint: disable=import-error
    sys.path.append(dummy_plugin_dir)
    from fake_fixture_plugin import pyang_plugin_init

    def _mock():
        monkeypatch.setattr(
            pkg_resources,
            'iter_entry_points',
            MagicMock(return_value=[
                MagicMock(load=MagicMock(return_value=pyang_plugin_init))
            ])
        )

    return _mock
