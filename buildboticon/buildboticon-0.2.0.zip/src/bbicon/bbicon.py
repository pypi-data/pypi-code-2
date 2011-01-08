#!/bin/env python

# BuildBotIcon - a system tray monitoring tool for BuildBot

# Copyright: 2010-2011 Marcus Lindblom
# License: GPL 3.0
# Website: https://bitbucket.org/marcusl/buildboticon/

import PyQt4.Qt
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from PyQt4.QtNetwork import * #@UnusedWildImport

import sys, re, textwrap, logging
import yaml
import bbicon_qrc #@UnusedImport

# ordered in severity
states = ['success', 'warn', 'fail', 'exception', 'offline', 'error']

class Build(QObject):
    log = logging.getLogger('Build')

    def __init__(self, id, url):
        QObject.__init__(self)

        assert url.isValid(), "Build %s has invalid url '%s'" % (id, url)

        self.id = id
        self.url = url
        self.prev_state = None
        self.state = None

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
            text = 'Build %(id)s at %(url)s has completed sucessfully.'
            icon_type = QSystemTrayIcon.Information
        elif new_state == 'warn':
            title = 'Build has warnings!'
            text = 'A build %(id)s at %(url)s has completed with warnings.'
            icon_type = QSystemTrayIcon.Warning
        elif new_state == 'fail':
            title = 'Build failed!'
            text = 'A build %(id)s at %(url)s has failed.'
            icon_type = QSystemTrayIcon.Warning
        elif new_state == 'exception':
            title = 'Build failed with exception!'
            text = 'A build %(id)s at %(url)s has failed with an exception.'
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
            text = 'Build %(id)s at %(url)s has unknown build state ' + str(new_state)
            icon_type = QSystemTrayIcon.Critical
            new_state = 'error'

        if new_state != self.state:
            text = text % { 'url': self.url.toString(), 'id': self.id }

            if new_state != error:
                self.log.info('Builder %s went from %s to %s: %s' % (self.id, self.state, new_state, text))
            else:
                self.log.warning('Builder %s went from %s to %s: %s' % (self.id, self.state, new_state, text))

            if 'offline' not in [self.state, new_state]:
                self.tray.showMessage(title, text, icon_type)

            icon = QIcon(':/buildbot-%s.%s' % (new_state, 'png' if new_state == 'error' else 'gif'))

            self.tray.setIcon(icon)
            self.tray.setToolTip(text)
            self.prev_state = self.state
            self.state = new_state

class BuildBotIcon(QObject):
    regex = re.compile('(success|warn|fail|exception)')
    log = logging.getLogger('BuildBotIcon')

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

        self.sounds = settings.sounds

        self.builds = dict((id, self._setup_build(id, url))
                           for id, url in settings.builds.items())
        self.outstanding_requests = 0

        self.offline_errors = [
            QNetworkReply.ConnectionRefusedError,
            QNetworkReply.HostNotFoundError,
            QNetworkReply.TimeoutError]

        # TemporaryNetworkFailureError is only available from Qt 4.7+
        if hasattr(QNetworkReply, 'TemporaryNetworkFailureError'):
            self.offline_errors.append(QNetworkReply.TemporaryNetworkFailureError)

        QMetaObject.connectSlotsByName(self)

    def start(self):
        self.timer.start()
        self.on_timer_timeout()

    def _setup_build(self, id, url):
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
        self.log.debug("Checking builds' statuses...")

        self.outstanding_requests = 0

        for b in self.builds.values():
            req = QNetworkRequest(b.url)
            req.setOriginatingObject(b)
            self.network.get(req)
            self.outstanding_requests += 1

    def on_network_finished(self, reply):
        self.log.debug("Request to %s finished" % reply.request().url().toString())

        b = reply.request().originatingObject()
        error = None
        state = None

        # determine build state
        if reply.error() in self.offline_errors:
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

        # if all requests have been replied to, play sound if state changed
        if not self.outstanding_requests:
            self._maybePlaySound()

    def _maybePlaySound(self):
        new_states = set(b.state for b in self.builds.values()
                         if b.state != b.prev_state
                         and b.prev_state not in ['offline', None])

        # self.log.warn(self.builds)
        # self.log.warn(new_states)

        # check all states, from worst to best, play "worst" sound
        for state in reversed(states):
            if state in new_states:
                sound = self.sounds.get(state)
                if sound:
                    sound.play()
                    return
class SettingsError(Exception):
    pass

class Settings(object):
    '''Settings for BuildbotIcon
    
       interval - integer of seconds between polls
       builds - list of tuples (id, url) for builds to check
       sounds - dict of state -> QSound for playing sounds 
    '''

    def __init__(self, file=None):
        self.interval = 30
        self.builds = {}
        self.sounds = {}

    def load(self, file):
        '''load settings from yaml file
        
            @param file: a file-like object providing a yaml document
        
            @throws: YAMLError on syntax error in file
            @throws: SettingsError on bad configuration
        '''

        settings = yaml.safe_load(file)

        # coerce types to make sure structure is correct
        for i in settings:
            if 'builds' == i:
                for id, url in settings['builds'].items():
                    # need to create QUrl separately as it doesn't store invalid urls
                    qurl = QUrl(url)
                    if not qurl.isValid():
                        raise SettingsError("Invalid url '%s' for build '%s'" % (url, id))
                    self.builds[id] = qurl
                continue

            if 'interval' == i:
                self.interval = int(settings['interval'])
                continue

            if 'sounds' == i:
                self.sounds = dict((s, QSound(f)) for s, f in settings['sounds'].items())
                for state in (s for s, _ in self.sounds.items() if not s in states):
                    raise SettingsError("Invalid state '%s' in sounds", state)
                continue

            raise SettingsError('Unknown settings item: %s' % i)

#############################################################################################

def main():
    a = QApplication(sys.argv)
    a.setQuitOnLastWindowClosed(False)

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    settings = Settings()
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as file:
                settings.load(file)
        except Exception, e:
            QMessageBox.warning(None, "Error loading config file",
                                str(e), buttons=QMessageBox.Close)
    else:
        QMessageBox.information(None, "No config file specified",
                                "Usage: bbicon.py <path-to-settings.yaml>",
                                buttons=QMessageBox.Close)
        settings.interval = 5
        settings.builds = [('buildbot', 'http://localhost:8000/builder.html')]

    bbi = BuildBotIcon(settings)
    bbi.start()
    sys.exit(a.exec_())

if __name__ == '__main__':
    main()
