#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command line tools for pyang + sensible extensions.

This module includes tools for augmenting ``PYANG_PLUGINPATH`` with
the location of auto-discovered pyang plugins.

Pyang do not use the ``setuptools`` to register plugins. Instead it requires
that the paths of all directories containing plugins to be present in the
``PYANG_PLUGINPATH`` environment variable.

``pyangext`` reads all entry points under ``yang.plugins``, detect the path
to the file that contains the function registered, and builds a list with
the containing directories.

In this sense, ``pyangext run`` command can be used as a bridge to
the ``pyang`` command, but using the auto-discovery feature.

.. note:: Including non pyang-plugin python files alongside pyang-plugins
    python files (in the same directory) will result in a pyang CLI crash.

    It is recommended that the function registered as entry-point follows
    the proprietary pyang plugin convention, or in other words:

    - it should be named ``pyang_plugin_init``
    - it should call ``pyang.plugin.register_plugin`` with an instance of
      ``pyang.plugin.PyangPlugin`` as argument.

.. seealso::
    https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins


Command Line Interface
======================

  Usage:
    ``pyangext [OPTIONS] COMMAND [ARGS]``

  Options:
    -h, --help             Show this message and exit.

    -v, --version          Show the version and exit.

    --path                 Prints the auto discovered plugin path.
                           Python packages that register an entry-point
                           inside ``yang.plugins`` will be auto-detected.

    --init, --export-path  Prints an export shell statement with the auto
                           discovered plugin path.

                           This may be used by shell script to configure
                           ``PYANG_PLUGINPATH`` environment variable.

                           Example: |example|

    --help                 Show this message and exit.

  Commands:
    :``call``: invoke pyang script with plugin path adjusted using
        auto-discovery.

.. |example| raw:: html

   <code><pre>eval $(pyangext --export-path)</pre></code>
"""
import sys
from os import environ
from os.path import pathsep
from subprocess import Popen
from textwrap import dedent

from six.moves import shlex_quote

import click

from . import __version__  # noqa
from .paths import expanded

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


def _fixdoc(func):
    """Fix the text wrapping in a function's docstring"""
    docstring = dedent(func.__doc__)
    lines = (' '.join(line.split()) for line in docstring.split('\n\n'))

    new_docstring = "\n".join(lines)
    func.__doc__ = new_docstring

    return new_docstring


# click option callback
def print_path(ctx, _, value):
    """\
    Prints the auto discovered plugin path.

    Packages that register an ``yang.plugins``
    entry-point will be auto-detected.
    """
    if not value or ctx.resilient_parsing:
        return

    click.echo(pathsep.join(expanded()))
    ctx.exit()


# click option callback
def export_path(ctx, _, value):
    """\
    Prints an export shell statement with the auto discovered plugin path.

    This may be used by shell script to configure ``PYANG_PLUGINPATH``
    environment variable.

    Example:
        eval $(pyangext --export-path)
    """
    if not value or ctx.resilient_parsing:
        return

    click.echo(
        'export PYANG_PLUGINPATH=' +
        shlex_quote(pathsep.join(expanded())))
    ctx.exit()


@click.group()
@click.help_option('-h', '--help')
@click.version_option(__version__, '-v', '--version')
@click.option(
    '--path', help=_fixdoc(print_path),
    is_flag=True, expose_value=False, callback=print_path)
@click.option(
    '--init', '--export-path', help=_fixdoc(export_path),
    is_flag=True, expose_value=False, callback=export_path)
def call():
    """\
    pyang + sensible extensions

    Includes self-registered pyang plugin auto-discovery
    """
    pass

_fixdoc(call)


@call.command(
    'run', context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def call_pyang(args):
    """\
    invoke pyang script with plugin path adjusted using auto-discovery
    """

    environ['PYANG_PLUGINPATH'] = pathsep.join(expanded())
    proc = Popen(['pyang'] + list(args), stdout=sys.stdout, stderr=sys.stderr)
    proc.wait()
    return proc.returncode

_fixdoc(call_pyang)
