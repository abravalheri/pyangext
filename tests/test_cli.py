#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # pylint: disable=redefined-outer-name
"""
tests for pyangext cli.call
"""
import os
import sys

from six.moves import shlex_quote

import pytest
from mock import MagicMock

import pyangext
from pyangext import cli

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


class CliExecutionAbort(RuntimeError):
    """Custom exception to abort cli without sys.exit"""
    pass


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


def test_print_path(dummy_plugin_dir, register_dummy_plugin, run_command):
    """
    print_path should produce the composed plugin path
    """
    register_dummy_plugin()
    os.environ['PYANG_PLUGINPATH'] = '/abc:/def'

    stdout, stderr = run_command(cli.call, '--path')

    expectation = shlex_quote('/abc:/def:{}'.format(dummy_plugin_dir))

    assert expectation in stdout
    assert not stderr


def test_export_path(dummy_plugin_dir, register_dummy_plugin, run_command):
    """
    export_path should produce an export statement with composed plugin path
    """
    register_dummy_plugin()
    os.environ['PYANG_PLUGINPATH'] = '/abc:/def'

    stdout, stderr = run_command(cli.call, '--export-path')

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
    stdout, stderr = run_command(cli.call, 'run', '-v')
    assert not stderr
    assert 'pyangext' not in stdout
    assert pyangext.__version__ not in stdout
    assert 'pyang' in stdout

    stdout, stderr = run_command(cli.call, 'run', '-h')
    assert not stderr
    assert 'FakeFixture Plugin Options' in stdout
    assert '--fake-fixture' in stdout

    stdout, stderr = run_command(
        cli.call, 'run', '-f', 'fake-fixture', example_module)
    assert not stderr
    assert 'Hello World!' in stdout

    stdout, stderr = run_command(
        cli.call, 'run', '-f', 'fake-fixture',
        '--fake-fixture-option', '!dlroW olleH', example_module)
    assert not stderr
    assert '!dlroW olleH' in stdout
