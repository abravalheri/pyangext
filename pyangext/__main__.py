#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Enables pyangext cli to run as script with ``python -m``"""
from pyangext import __version__  # noqa
from pyangext import cli

__author__ = "Anderson Bravalheri"
__copyright__ = "Copyright (C) 2016 Anderson Bravalheri"
__license__ = "mozilla"


if __name__ == "__main__":
    cli.call()
