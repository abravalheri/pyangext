# -*- coding: utf-8 -*-
"""Critical missing features for ``pyang`` plugin users and authors

    ``pyangext`` is an abbreviation for **pyang** + sensible **extensions**


Plugin Auto-Registering
=======================
No need for coping and pasting ``.py`` files inside
``pyang`` installation dir or manually setting ``PYANG_PLUGINPATH``
environment variable. By using the ``pyangext`` command line tool all the
plugins registered using ``setuptools`` entry-points are auto-detected.

.. seealso:: module :mod:`pyangext.paths`.


YANG module expansion
=====================
Expand all ``uses`` statement by embedding ``grouping`` definitions.
"""
from __future__ import absolute_import

import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:  # pylint: disable=bare-except
    __version__ = 'unknown'
