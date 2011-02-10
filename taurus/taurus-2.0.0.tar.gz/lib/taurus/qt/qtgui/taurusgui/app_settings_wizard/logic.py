#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
###########################################################################

"""
This file provide the logic for the application settings wizard
-creates the wizard
-adds pages
-run the application_
"""

import os, sys
from PyQt4 import QtGui, QtCore, Qt
from taurus.core.util import Enumeration

def newSettings():
    import appsettingswizard

    app = QtGui.QApplication([])
    #QtCore.QResource.registerResource(appsettingswizard.get_resources())
    
    Pages = Enumeration('Pages', ('IntroPage', 'GeneralSettings', 'CustomLogoPage','SynopticPage','InstrumentsPage', 'PanelsPage','ExternalAppPage','MonitorPage','OutroPage'))
    w = appsettingswizard.AppSettingsWizard()

    intro = appsettingswizard.IntroPage()
    w.setPage(Pages.IntroPage, intro)
    intro.setNextPageId(Pages.GeneralSettings)
    
    #intro.setNextPageId(Pages.PanelsPage)
    
    general_settings_page = appsettingswizard.GeneralSettings()
    w.setPage(Pages.GeneralSettings, general_settings_page)
    general_settings_page.setNextPageId(Pages.CustomLogoPage)
    
    custom_logo_page = appsettingswizard.CustomLogoPage()
    w.setPage(Pages.CustomLogoPage, custom_logo_page)
    custom_logo_page.setNextPageId(Pages.SynopticPage)
    
    synoptic_page = appsettingswizard.SynopticPage()
    w.setPage(Pages.SynopticPage, synoptic_page)
    synoptic_page.setNextPageId(Pages.InstrumentsPage)
    
    instruments_page = appsettingswizard.InstrumentsPage()
    w.setPage(Pages.InstrumentsPage, instruments_page)
    instruments_page.setNextPageId(Pages.PanelsPage)
    
    panels_page = appsettingswizard.PanelsPage()
    w.setPage(Pages.PanelsPage, panels_page)
    panels_page.setNextPageId(Pages.ExternalAppPage)
    
    external_app_page = appsettingswizard.ExternalAppPage()
    w.setPage(Pages.ExternalAppPage, external_app_page)
    external_app_page.setNextPageId(Pages.MonitorPage)
    
    monitor_page = appsettingswizard.MonitorPage()
    w.setPage(Pages.MonitorPage, monitor_page)
    monitor_page.setNextPageId(Pages.OutroPage)   
    
    outro_page = appsettingswizard.OutroPage()
    w.setPage(Pages.OutroPage, outro_page)    

    w.setOption (QtGui.QWizard.CancelButtonOnLeft , True)
    #w.setOption (QtGui.QWizard.DisabledBackButtonOnLastPage , True)    
    w.show()
    sys.exit(app.exec_())


def main():
    newSettings()
  
if __name__ == "__main__":
    main()