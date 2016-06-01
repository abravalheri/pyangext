# -*- coding: utf-8 -*-
"""Critical missing features for ``pyang`` plugin users and authors."""
from __future__ import absolute_import

import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:  # pylint: disable=bare-except
    __version__ = 'unknown'
