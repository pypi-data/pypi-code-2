# -*- coding: utf-8 -*-
# $Id: utils.py 237778 2011-04-18 10:40:52Z glenfant $
"""Misc utilities"""

from Products.Five import BrowserView
from config import CONTROLPANEL_ID
from controlpanel import ControlPanel

class Utils(BrowserView):

    def install(self):
        """Add the control panel
        """
        zcp = self.context.Control_Panel
        if CONTROLPANEL_ID not in zcp.objectIds():
            mpcp = ControlPanel()
            zcp._setObject(CONTROLPANEL_ID, mpcp)
        return u"ZCML doc panel added. Click the \"Back\" button of your browser."

    def uninstall(self):
        """Removes the control panel
        """
        zcp = self.context.Control_Panel
        if CONTROLPANEL_ID in zcp.objectIds():
            zcp._delObject(CONTROLPANEL_ID)
        return u"ZCML doc panel removed. Click the \"Back\" button of your browser."

