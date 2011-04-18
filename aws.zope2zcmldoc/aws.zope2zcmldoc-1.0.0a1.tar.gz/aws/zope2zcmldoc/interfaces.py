# -*- coding: utf-8 -*-
# $Id: interfaces.py 237778 2011-04-18 10:40:52Z glenfant $
"""Public interfaces"""

from zope.interface import Interface

class IControlPanel(Interface):
    """ZCML documentation Control Panel
    """
    def namespaces():
        """Ordered list of dicts with keys
        * namespace: URI of namespace
        * view_url: URL to the details
        *
        """