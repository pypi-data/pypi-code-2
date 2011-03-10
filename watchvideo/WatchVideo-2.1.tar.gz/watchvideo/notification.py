#!/usr/bin/env python
# -*- coding: utf-8 -*- #
###
#
# WatchVideo is the legal property of Leonardo Gastón De Luca
# leo[at]kde.org.ar Copyright (c) 2009 Leonardo Gastón De Luca
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###

try:
    import pynotify
    HAS_PYNOTIFY = True
except ImportError:
    HAS_PYNOTIFY = False

from watchvideo.qt import QtGui
from watchvideo.qt.QtGui import QSystemTrayIcon
import watchvideo.constants as c


class Notification:
    """This class handles the display of visual notification bubbles."""
    
    def __init__(self, trayicon, settings, appname="WatchVideo"):
        """Initialize the class."""
        self.trayicon = trayicon
        self.notifications = [] # This list holds the instances of all notifications
        
        self.settings = settings #should settings be here?!
        if HAS_PYNOTIFY:
            pynotify.init(appname)
        
    def show(self, title, message, category='download-done', urgency=0, expires=15000, image=c.ICON_DOWNLOAD):
        """Displays a notification bubble."""
        
        if category == 'download-done' and not \
        self.settings.value('Notification/notifyDone'):
            return 0
        
        if category == 'download-error':
            if not self.settings.value('Notification/notifyError'):
                return 0
                
            image = c.ICON_ERROR

        if HAS_PYNOTIFY:
            #image = '/'.join(__file__.split('/')[0:-1]) + '/' + image
            
            bubble = pynotify.Notification(title, message, image)
            
            bubble.set_category(category)
            bubble.set_hint('desktop-entry', 'WatchVideo')
            # bubble.set_hint('x', '0')
            # bubble.set_hint('y', '0')
            
            if urgency == 0:
                bubble.set_urgency(pynotify.URGENCY_LOW)
            elif urgency == 2:
                bubble.set_urgency(pynotify.URGENCY_CRITICAL)
            
            if expires == 0:
                bubble.set_timeout(pynotify.EXPIRES_NEVER)
            else:
                bubble.set_timeout(expires)
            
            bubble.show()
            self.notifications.append(bubble)
        elif self.trayicon.supportsMessages(): #Uses the ballon tip from the tray icon
            self.trayicon.showMessage(title, message, QSystemTrayIcon.Information, expires)
        else:
            print "Apparently you don't have python-notify and neither tray icon \
            popup messages are supported on your system. \
            I recomend you to install python-notify" 
            
    def getNotifications(self):
        """Returns a list with the instances of all notifications."""
        
        return self.notifications
        
    def tr(self, txt):
        """Translate a string into a local language."""
        return QtGui.QApplication.instance().translate('', txt)
