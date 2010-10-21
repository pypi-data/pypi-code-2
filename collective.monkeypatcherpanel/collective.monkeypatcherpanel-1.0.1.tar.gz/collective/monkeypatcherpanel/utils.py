# -*- coding: utf-8 -*-
# $Id: utils.py 146688 2010-10-21 16:06:59Z glenfant $
"""Misc utilities"""

from Products.Five import BrowserView
from config import CONTROLPANEL_ID
from controlpanel import ControlPanel

class Utils(BrowserView):

    def add(self):
        """Add the control panel
        """
        zcp = self.context.Control_Panel
        if CONTROLPANEL_ID not in zcp.objectIds():
            mpcp = ControlPanel()
            zcp._setObject(CONTROLPANEL_ID, mpcp)
        return u"Monkey pacher panel added. Click the \"Back\" button."

    def remove(self):
        """Removes the control panel
        """
        zcp = self.context.Control_Panel
        zcp._delObject(CONTROLPANEL_ID)
        return u"Monkey pacher panel removed. Click the \"Back\" button."