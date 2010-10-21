# -*- coding: utf-8 -*-
# $Id: __init__.py 146677 2010-10-21 15:24:51Z glenfant $
"""collective.monkeypatcherpanel"""
from App.version_txt import getZopeVersion
version = getZopeVersion()
if version > (2, 12):
    from App.ImageFile import ImageFile
else:
    from Globals import ImageFile

from controlpanel import ControlPanel
from config import CONTROLPANEL_ID

def initialize(context):
    """Zope 2 registration"""
    # FIXME: somehow dirty way to get the control panel. Something cleaner available around?
    zcp = context._ProductContext__app.Control_Panel
    cp_id = ControlPanel.id
    if (version <= (2, 12)) and (CONTROLPANEL_ID not in zcp.objectIds()):
        control_panel = ControlPanel()
        zcp._setObject(cp_id, control_panel)

    return
