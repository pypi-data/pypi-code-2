from bbicon import Build, BuildBotIcon, Settings
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from PyQt4.QtNetwork import * #@UnusedWildImport

import bbicon
from StringIO import StringIO
try:
    import unittest2 as unittest
except ImportError:
    import unittest #@UnusedImport

import logging
import sys
from mock import patch, Mock

###################################################################

def setUpModule():
    global qApp
    if qApp.startingUp():
        qApp = QApplication(sys.argv)
        logging.basicConfig()
        logging.getLogger().setLevel(logging.WARNING)

###################################################################

class TestBuild(unittest.TestCase):

    def setUp(self):
        setUpModule()
        self.build = Build('test', QUrl('http://localhost:8000/test'))

    def testCreate(self):
        self.assertTrue(self.build)
        self.assertTrue(self.build.state, 'offline')

    def testSuccess(self):
        self.build.set_status('success')
        self.assertEquals(self.build.state, 'success')

    def testStorePrevious(self):
        self.build.set_status('success')
        self.assertEquals(self.build.state, 'success')
        self.assertEquals(self.build.prev_state, 'offline')
        self.build.set_status('warn')
        self.assertEquals(self.build.state, 'warn')
        self.assertEquals(self.build.prev_state, 'success')

    def testError(self):
        self.build.set_status(None, 'unit test says fail')
        self.assertEquals(self.build.state, 'error')

    def testInternalError(self):
        self.build.set_status(None, None)
        self.assertEquals(self.build.state, 'error')

    def testSetIcon(self):
        @patch.object(QSystemTrayIcon, 'setIcon')
        def test(mock):
            self.build.set_status('success')
            self.assertTrue(mock.called, "should set an icon on startup")

    def testSetToolTip(self):
        @patch.object(QSystemTrayIcon, 'settoolTip')
        def test(mock):
            self.build.set_status('success')
            self.assertTrue(mock.called, "should set a tooltip on startup")
            self.assertIn(self.b.url.toString(), mock.call_args[0], "Url not in tooltip")

    def testDontShowInitialMessage(self):
        @patch.object(QSystemTrayIcon, 'showMessage')
        def test(mock):
            self.build.set_status('success')
            self.assertFalse(mock.called, "shouldn't show message on startup")

    def testShowMessageOnChange(self):
        @patch.object(QSystemTrayIcon, 'showMessage')
        def test(mock):
            self.build.set_status('success')
            mock.reset_mock()
            self.build.set_status('warn')
            self.assertTrue(mock.called, "should show message after changed status")

    def testDontShowMessageOnNoChange(self):
        @patch.object(QSystemTrayIcon, 'showMessage')
        def test(mock):
            self.build.set_status('success')
            self.build.set_status('warn')
            mock.reset_mock()

            self.build.set_status('warn')
            self.assertFalse(mock.called, "should not show message on repeated status")

#####################################################################

class MockRequest(QNetworkRequest):
    def __init__(self):
        QNetworkRequest.__init__(self)
        self.originatingObject = Mock()

class MockReply(QNetworkReply):
    def __init__(self):
        QNetworkReply.__init__(self)

        self.error = Mock()
        self.error.return_value = QNetworkReply.NoError

        self.errorString = Mock()
        self.errorString.return_value = ''

        self.readAll = Mock()
        self.readAll.return_value = QByteArray('')

        self.mock_request = MockRequest()
        self.request = Mock()
        self.request.return_value = self.mock_request

#####################################################################

class TestBuildbotIcon(unittest.TestCase):

    def setUp(self):
        setUpModule()

        # avoid leaving icons in system tray after test
        QSystemTrayIcon.setVisible = Mock()

        self.settings = Settings()
        self.settings.builds = {'test': QUrl('http://localhost:8000/test'),
                                'test2': QUrl('http://localhost:8000/test2')}

        # mock each sound individually
        for s in bbicon.states:
            sound = QSound('')
            sound.play = Mock()
            self.settings.sounds[s] = sound

        self.bbi = BuildBotIcon(self.settings)


    def testCreate(self):
        self.assertTrue(self.bbi)
        self.assertTrue(QSystemTrayIcon.setVisible.called)

    def testActivateMenuContext(self):
        self.bbi.on_activated(QSystemTrayIcon.Context)
        self.assertTrue(self.bbi.cxt_menu.isVisible())

    def testActivateMenuTrigger(self):
        self.bbi.on_activated(QSystemTrayIcon.Trigger)
        self.assertTrue(self.bbi.cxt_menu.isVisible())

    def testAbout(self):
        self.bbi.on_about()
        self.assertTrue(self.bbi.about.isVisible())

    def testStatusGet(self):
        @apply
        @patch.object(QNetworkAccessManager, 'get')
        def test(mock):
            self.bbi.on_timer_timeout()

            self.assertEqual(2, mock.call_count)
            for n, url in enumerate(self.settings.builds.values()):
                self.assertEqual(mock.call_args_list[n][0][0].url(), url)

    def _testStatusResponse(self, status, result=None):
        @apply
        @patch.object(QNetworkAccessManager, 'get')
        def test(mock):
            self.bbi.on_timer_timeout() # make some requests

            reply = MockReply()
            reply.mock_request.originatingObject.return_value = self.bbi.builds['test']
            reply.readAll.return_value = QByteArray('<td>%s</td>' % status)

            self.bbi.on_network_finished(reply)

            self.assertTrue(reply.error.called)
            self.assertTrue(reply.readAll.called)
            self.assertEqual(result or status, self.bbi.builds['test'].state)

    def testStatusResponseSuccess(self):
        self._testStatusResponse('success')

    def testStatusResponseWarning(self):
        self._testStatusResponse('warn')

    def testStatusResponseFail(self):
        self._testStatusResponse('fail')

    def testStatusResponseException(self):
        self._testStatusResponse('exception')

    def _testStatusResponseError(self, error, expected_state):
        @apply
        @patch.object(QNetworkAccessManager, 'get')
        def test(mock):
            self.bbi.on_timer_timeout() # make some requests

            reply = MockReply()
            reply.mock_request.originatingObject.return_value = self.bbi.builds['test']
            reply.error.return_value = error

            self.bbi.on_network_finished(reply)

            self.assertFalse(reply.readAll.called, 'NetworkReply.readAll() should not be called on errors')
            self.assertEqual(self.bbi.builds['test'].state, expected_state)

    def testStatusResponseOffline(self):
        self._testStatusResponseError(QNetworkReply.TimeoutError, 'offline')

    def testStatusResponseError(self):
        self._testStatusResponseError(QNetworkReply.ProtocolFailure, 'error')

    def testStatusResponseUnknown(self):
        self._testStatusResponse('jibberish and greek', 'error')

    def testPlaySoundAfterAllRequests(self):
        @apply
        @patch.object(QNetworkAccessManager, 'get')
        def test(mock):
            self.bbi.on_timer_timeout() # make some requests
            self.bbi._maybePlaySound = Mock()

            reply = MockReply()

            reply.mock_request.originatingObject.return_value = self.bbi.builds['test']
            self.bbi.on_network_finished(reply)

            self.assertFalse(self.bbi._maybePlaySound.called, "Shouldn't compute sounds ")

            reply.mock_request.originatingObject.return_value = self.bbi.builds['test2']
            self.bbi.on_network_finished(reply)

            self.assertTrue(self.bbi._maybePlaySound.called)

    def _testPlaySound(self, build_states):
        for k, v in build_states.items():
            if k in self.bbi.builds:
                self.bbi.builds[k].state = v[0]
                self.bbi.builds[k].prev_state = v[1]

        self.bbi._maybePlaySound()

        return self.bbi.sounds

    def testPlaySoundOnChange(self):
        sounds = self._testPlaySound({'test': ('success', 'fail')})
        self.assertFalse(sounds['fail'].play.called)
        self.assertTrue(sounds['success'].play.called)

    def testDontPlaySoundOnSame(self):
        sounds = self._testPlaySound({'test': ('success', 'success')})
        self.assertFalse(sounds['success'].play.called)

    def testPlayWorstSound(self):
        sounds = self._testPlaySound({'test': ('warn', 'success'),
                                      'test2': ('fail', 'success')})
        self.assertFalse(sounds['success'].play.called)
        self.assertFalse(sounds['warn'].play.called)
        self.assertTrue(sounds['fail'].play.called)

    def tesPlaySoundOnGoingOffline(self):
        sounds = self._testPlaySound({'test': ('offline', 'success')})
        self.assertTrue(sounds['offline'].play.called)

    def testDontPlaySoundOnGoingOnline(self):
        sounds = self._testPlaySound({'test': ('success', 'offline')})
        for k, v in sounds.items():
            self.assertFalse(v.play.called, "sound %s was played" % k)


#######################################################################

class TestSettings(unittest.TestCase):
    def setUp(self):
        setUpModule()
        self.settings = Settings()

    def testDefaultSettingsOnBBI(self):
        bbi = BuildBotIcon(self.settings)
        self.assertTrue(bbi)

    def testLoadInterval(self):
        file = StringIO('interval: 42')
        self.settings.load(file)
        self.assertEqual(42, self.settings.interval)

    def testLoadSoundsUnix(self):
        success_file = '~/sounds/woohoo.wav'
        file = StringIO('''sounds:\n success: '%s' ''' % success_file)
        self.settings.load(file)
        self.assertIn('success' , self.settings.sounds)
        self.assertEqual(success_file,
                          self.settings.sounds['success'].fileName())

    def testLoadSoundsWindows(self):
        # we use single quotes to avoid yaml escaping \s and \w
        success_file = 'c:\\sounds\\woohoo.wav'
        file = StringIO('''sounds:\n success: '%s' ''' % success_file)
        self.settings.load(file)
        self.assertIn('success', self.settings.sounds)
        self.assertEqual(success_file,
                          self.settings.sounds['success'].fileName())

    def testRaiseErrorWhenLoadingSoundsForUnknownState(self):
        # we use single quotes to avoid yaml escaping \s and \w
        file = StringIO('''sounds:\n bork: '~/meh.wav' ''')
        with self.assertRaises(bbicon.SettingsError) as cm:
            self.settings.load(file)
        self.assertIn('bork', str(cm.exception))

    def testLoadBuild(self):
        id = 'b1'
        url = 'http://localhost:8010/b1'
        file = StringIO('''builds:\n %s: %s \n''' % (id, url))
        self.settings.load(file)
        self.assertIn(id, self.settings.builds)
        self.assertEqual(url, self.settings.builds[id].toString())

    def testRaiseErrorForInvalidBuildURL(self):
        fail_url = '//:\\bork!'
        file = StringIO('''builds:\n b1: '%s' ''' % fail_url)
        with self.assertRaises(bbicon.SettingsError) as cm:
            self.settings.load(file)
        self.assertIn(fail_url, str(cm.exception))

    def testRaiseErrorForUnknownSettingsItem(self):
        fail_item = 'bork'
        file = StringIO('%s: 47' % fail_item)
        with self.assertRaises(bbicon.SettingsError) as cm:
            self.settings.load(file)
        self.assertIn(fail_item, str(cm.exception))



#######################################################################

if __name__ == '__main__':
    unittest.main()
