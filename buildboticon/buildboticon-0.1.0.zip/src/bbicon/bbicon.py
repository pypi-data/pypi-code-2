#!/bin/env python

# BuildBotIcon - a system tray monitoring tool for BuildBot

# Copyright: 2010-2011 Marcus Lindblom
# License: GPL 3.0
# Website: https://bitbucket.org/marcusl/buildboticon/

import PyQt4.Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import sys, re, os, textwrap

import bbicon_qrc

states = ['success', 'warn', 'fail', 'exception', 'error', 'offline']

class Build(QObject):
    def __init__(self, id, url):
        QObject.__init__(self)

        self.id = id
        self.url = QUrl(url)
        self.prev_state = None
        self.state = None

        assert self.url.isValid(), "Build %s has invalid url '%s'" % (id, url)

        self.tray = QSystemTrayIcon()
        self.set_status('offline')
        self.tray.setVisible(True)

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.id

    def __repr__(self):
        return '<%s instance %s %s>' % (type(self), self.id, self.url)

    def set_status(self, new_state, error=None):
        if new_state == 'success':
            title = 'Build ok.'
            text = 'Build at %(url)s has completed sucessfully.'
            icon_type = QSystemTrayIcon.Information
        elif new_state == 'warn':
            title = 'Build has warnings!'
            text = 'A build at %(url)s has completed with warnings.'
            icon_type = QSystemTrayIcon.Warning
        elif new_state == 'fail':
            title = 'Build failed!'
            text = 'A build at %(url)s has failed.'
            icon_type = QSystemTrayIcon.Warning
        elif new_state == 'exception':
            title = 'Build failed with exception!'
            text = 'A build at %(url)s has failed with an exception.'
            icon_type = QSystemTrayIcon.Warning
        elif new_state == 'offline':
            title = 'BuildBot is offline'
            text = 'Unable to reach the BuildBot at %(url)s.'
            icon_type = QSystemTrayIcon.Warning
        elif error:
            new_state = 'error'
            title = 'Error checking %s' % self.id
            text = error
            icon_type = QSystemTrayIcon.Critical
        else:
            title = 'Internal error'
            text = 'Unknown build state %s' % new_state
            icon_type = QSystemTrayIcon.Critical
            new_state = 'error'

        if new_state != self.state:
            text = text % { 'url': self.url.toString() }

            print 'Builder %s went from %s to %s: %s' % (self.id, self.state, new_state, text)

            if 'offline' not in [self.state, new_state]:
                self.tray.showMessage(title, text, icon_type)

            icon = QIcon(':/buildbot-%s.%s' % (new_state, 'png' if new_state == 'error' else 'gif'))

            self.tray.setIcon(icon)
            self.tray.setToolTip(text)
            self.prev_state = self.state
            self.state = new_state

class BuildBotIcon(QObject):
    regex = re.compile('(success|warn|fail|exception)')

    def __init__(self, settings):
        QObject.__init__(self)

        self.cxt_menu = QMenu()
        self.cxt_menu.addAction("About...", self.on_about)
        self.cxt_menu.addAction("About Qt...", lambda: QMessageBox.aboutQt(None))
        self.cxt_menu.addAction("Quit", qApp.quit)

        self.timer = QTimer(self)
        self.timer.setObjectName('timer')
        self.timer.setInterval(settings.interval * 1000)

        self.network = QNetworkAccessManager(self)
        self.network.setObjectName('network')

        self.sounds = dict((state, QSound(file)) for state, file in settings.sounds)

        QMetaObject.connectSlotsByName(self)

        self.builds = map(lambda (id, url): self.setup_build(id, url), settings.builds)
        self.outstanding_requests = {}

        self.timer.start()
        self.on_timer_timeout()

    def setup_build(self, id, url):
        b = Build(id, url)
        b.tray.activated.connect(self.on_activated)
        b.tray.setContextMenu(self.cxt_menu)
        return b

    def on_activated(self, reason):
        actions = {
            QSystemTrayIcon.Context: lambda: self.cxt_menu.show(),
            QSystemTrayIcon.Trigger: lambda: self.cxt_menu.show()
            }

        actions.get(reason, lambda: None)()


    def on_about(self):
        text = textwrap.dedent('''\
            BuildBotIcon - a BuildBot monitoring utility

            http://bitbucket.org/marcusl/buildboticon

            Copyright 2010-2011 Marcus Lindblom
            Licensed under GPLv3

            Using Qt %s, PyQt %s and
            Python %s''' %
            (PyQt4.Qt.QT_VERSION_STR, PyQt4.Qt.PYQT_VERSION_STR,
            sys.version))

        self.about = QMessageBox()
        self.about.setWindowTitle("About BuildBotIcon...")
        self.about.setText(text)
        self.about.setIconPixmap(QPixmap(':/buildbot-bignut.png'))
        self.about.show()

    def on_timer_timeout(self):
        print "checking..."

        self.outstanding_requests = 0

        for b in self.builds:
            req = QNetworkRequest(b.url)
            req.setOriginatingObject(b)
            self.network.get(req)
            self.outstanding_requests += 1

    def on_network_finished(self, reply):
        print "Request to %s finished" % reply.request().url().toString()

        b = reply.request().originatingObject()

        error = None
        state = None

        offline_errors = [
            QNetworkReply.ConnectionRefusedError,
            QNetworkReply.HostNotFoundError,
            QNetworkReply.TimeoutError]

        if hasattr(QNetworkReply, 'TemporaryNetworkFailureError'):
            offline_errors.append(QNetworkReply.TemporaryNetworkFailureError)

        if reply.error() in offline_errors:
            state = 'offline'
        elif reply.error():
            error = 'Network error %i reading %s: %s' % \
                (reply.error(), b.url.toString(), reply.errorString())
        else:
            # assume utf-8 in reply, but doesn't really matter as we regex for 7-bit ascii
            match = self.regex.search(QString.fromUtf8(reply.readAll()))
            if not match:
                error = 'Reply did not match any expected content'
            else:
                state = match.group(0)

        # update icon
        b.set_status(state, error)

        self.outstanding_requests -= 1

        # all requests have been replied to, play sound if state changed
        if self.outstanding_requests == 0:
            new_states = [b.state for b in self.builds if b.state != b.prev_state]

            # check all states, from worst to best, play "worst" sound
            for state in reversed(states[:-1]): # skip offline state
                if state in new_states:
                    sound = self.sounds.get(state)
                    if sound:
                        sound.play()
                        break


class Settings(object):
     def __init__(self, file=None):
        self.interval = 30
        self.builds = []
        self.sounds = {} # state str -> sound file name

#############################################################################################

def main():
    a = QApplication(sys.argv)
    a.setQuitOnLastWindowClosed(False)

    settings = Settings(sys.argv[1] if len(sys.argv) > 1 else None)
    settings.interval = 5
    settings.builds = [('buildbot', 'http://localhost:8000/builder.html')]

    bbi = BuildBotIcon(settings)
    sys.exit(a.exec_())

if __name__ == '__main__':
    main()
