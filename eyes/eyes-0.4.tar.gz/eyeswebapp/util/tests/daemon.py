from django.test import TestCase
from util.daemon import Daemon
import os
class DaemonTests(TestCase):
    # def setUp(self):
    #     pass        
    def test_daemon_defaults(self):
        """testing Daemon default values"""
        new_daemon = Daemon("/tmp/nothing.pid")
        self.assertTrue(new_daemon)
        self.assertEquals(new_daemon.stdin, '/dev/null')
        self.assertEquals(new_daemon.stdout, '/dev/null')
        self.assertEquals(new_daemon.stderr, '/dev/null')
        self.assertEquals(new_daemon.pidfile, "/tmp/nothing.pid")
    #
    # def test_functional_daemon_start_stop(self):
    #     """testing Daemon default values"""
    #     new_daemon = Daemon("/tmp/nothing.pid")
    #     self.assertTrue(new_daemon)
    #     new_daemon.start()
    #     self.assertTrue(os.path.exists(new_daemon.pidfile))
    #     new_daemon.stop()
    #     self.assertFalse(os.path.exists(new_daemon.pidfile))
    #
