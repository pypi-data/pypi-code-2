# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from djangode import global_objects
from djangode.utils.qt import QtCore, QtGui, QtWebKit

class BrowserTab(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.vlayout = QtGui.QVBoxLayout()

        self.url_bar = QtGui.QLineEdit(self)
        self.vlayout.addWidget(self.url_bar)

        self.browser = BrowserWindow(self)
        self.vlayout.addWidget(self.browser)

        self.setLayout(self.vlayout)

        self.browser.urlChanged.connect(self.url_changed)
        self.url_bar.returnPressed.connect(self.browse_to_url)

    def reload(self):
        self.browser.reload()

    def url_changed(self, url):
        self.url_bar.setText(url if isinstance(url, basestring) else url.toString())

    def browse_to_url(self):
        url = self.url_bar.text()

        if url.startsWith("/") and global_objects.project is not None:
            self.browser.load(QtCore.QUrl("%s%s" % (global_objects.project.runner.host(), url)))
        else:
            self.browser.load(QtCore.QUrl(url))

class BrowserWindow(QtWebKit.QWebView):
    def __init__(self, parent, url = None):
        QtWebKit.QWebView.__init__(self, parent)

        self.loadProgress.connect(loadProgress)

        if url is not None:
            self.load(QtCore.QUrl("%s%s" % (global_objects.project.runner.host() if not url.startsWith("http://") else "", url)))
        elif global_objects.project is not None:
            self.load(QtCore.QUrl(global_objects.project.runner.host()))
        else:
            self.load(QtCore.QUrl("http://www.djangoproject.com/"))

def loadProgress(i):
    pass
