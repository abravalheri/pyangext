#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # pylint: disable=redefined-outer-name
"""
tests for pyangext cmd
"""
import os
import sys
from collections import Counter
from textwrap import dedent

import pkg_resources
from six.moves import shlex_quote

import pytest
from mock import MagicMock

import pyangext
from pyangext import __main__ as cmd

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


class CliExecutionAbort(RuntimeError):
    """Custom exception to abort cli without sys.exit"""
    pass


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


@pytest.fixture
def run_command(tmpdir_factory, monkeypatch):
    """Fixture to run CLI command with arguments traping stdout and stderr"""

    def _run(command, *args):
        """Run CLI command with arguments traping stdout and stderr

        Arguments:
            args (list): command line options and arguments

        Returns:
            tuple: (captured stdout, captured stdin)
        """
        # prepare command options and arguments
        monkeypatch.setattr(sys, 'argv', ['pyangext'] + list(args))

        io_dir = tmpdir_factory.mktemp("io")
        stdout_file = str(io_dir.join("stdout.txt").realpath())
        stderr_file = str(io_dir.join("stderr.txt").realpath())

        # Trap IO
        with open(stdout_file, 'w') as trap_stdout, \
                open(stderr_file, 'w') as trap_stderr:

            # Trap sys.exit
            exit_func = sys.exit
            monkeypatch.setattr(
                sys, 'exit', MagicMock(side_effect=CliExecutionAbort))

            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = trap_stdout, trap_stderr

            try:
                command()
            except CliExecutionAbort:
                pass

            # Untrap IO
            sys.stdout, sys.stderr = old_stdout, old_stderr

            # Untrap sys.exit
            monkeypatch.setattr(sys, 'exit', exit_func)

        with open(stdout_file, 'r') as trap_stdout, \
                open(stderr_file, 'r') as trap_stderr:
            response = trap_stdout.read(), trap_stderr.read()

        return response

    return _run


def test_plugin_paths(dummy_plugin_dir, register_dummy_plugin):
    """
    plugin_paths should include the directory of a plugin
        registered as entry_point
    """
    register_dummy_plugin()
    locations = cmd.plugin_paths()
    assert dummy_plugin_dir in locations


def test_expanded_path(dummy_plugin_dir, register_dummy_plugin):
    """
    expanded_path should contain PYANG_PLUGINPATH
    expanded_path should keep order with PYANG_PLUGINPATH in the begining
    expanded_path should not contain duplicated values
    """
    register_dummy_plugin()
    os.environ['PYANG_PLUGINPATH'] = '/abc'
    locations = cmd.expanded_path()
    assert dummy_plugin_dir in locations
    assert '/abc' in locations

    os.environ['PYANG_PLUGINPATH'] = '/abc:/def'
    locations = cmd.expanded_path()
    assert locations[0] == '/abc'
    assert locations[1] == '/def'
    assert locations[2] == dummy_plugin_dir

    os.environ['PYANG_PLUGINPATH'] = '/abc:/abc'
    locations = cmd.expanded_path()
    location_counter = Counter(locations)
    assert location_counter['/abc'] == 1


def test_print_path(dummy_plugin_dir, register_dummy_plugin, run_command):
    """
    print_path should produce the composed plugin path
    """
    register_dummy_plugin()
    os.environ['PYANG_PLUGINPATH'] = '/abc:/def'

    stdout, stderr = run_command(cmd.cli, '--path')

    expectation = shlex_quote('/abc:/def:{}'.format(dummy_plugin_dir))

    assert expectation in stdout
    assert not stderr


def test_export_path(dummy_plugin_dir, register_dummy_plugin, run_command):
    """
    export_path should produce an export statement with composed plugin path
    """
    register_dummy_plugin()
    os.environ['PYANG_PLUGINPATH'] = '/abc:/def'

    stdout, stderr = run_command(cmd.cli, '--export-path')

    expectation = (
        'export PYANG_PLUGINPATH=' +
        shlex_quote('/abc:/def:{}'.format(dummy_plugin_dir))
    )

    assert expectation in stdout
    assert not stderr


def test_run(register_dummy_plugin, example_module, run_command):
    """
    run command should forward arguments to pyang
    pyang help should display plugin options
    plugin format should be know by pyang
    plugin options should work
    """
    register_dummy_plugin()
    stdout, stderr = run_command(cmd.cli, 'run', '-v')
    assert not stderr
    assert 'pyangext' not in stdout
    assert pyangext.__version__ not in stdout
    assert 'pyang' in stdout

    stdout, stderr = run_command(cmd.cli, 'run', '-h')
    assert not stderr
    assert 'FakeFixture Plugin Options' in stdout
    assert '--fake-fixture' in stdout

    stdout, stderr = run_command(
        cmd.cli, 'run', '-f', 'fake-fixture', example_module)
    assert not stderr
    assert 'Hello World!' in stdout

    stdout, stderr = run_command(
        cmd.cli, 'run', '-f', 'fake-fixture',
        '--fake-fixture-option', '!dlroW olleH', example_module)
    assert not stderr
    assert '!dlroW olleH' in stdout
