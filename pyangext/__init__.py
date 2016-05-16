# -*- coding: utf-8 -*-
"""Critical missing features for ``pyang`` plugin users and authors

    ``pyangext`` is an abbreviation for **pyang** + sensible **ext**ensions


Plugin Auto-Registering
=======================
No need for coping and pasting ``.py`` files inside
``pyang`` instalation dir or manually setting ``PYANG_PLUGINPATH``
environment variable. By using the ``pyangext`` command line tool all the
plugins registered using ``setuptools`` entry-points are auto-detected.

See :mod:`pyangext.__main__`.


YANG module expansion
=====================
Expand all ``uses`` statement by embedding ``grouping`` definitions.
"""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:  # pylint: disable=bare-except
    __version__ = 'unknown'
