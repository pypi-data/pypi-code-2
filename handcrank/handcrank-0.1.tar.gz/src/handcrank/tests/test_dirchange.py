import time
import shutil
from os import unlink, mkdir
from os.path import join

from handcrank.tests.testcase import TestCase
from handcrank.dirchange import Monitor


class DirectoryChangeTest(TestCase):
    def test_handles_bad_directory(self):
        with self.assertRaises(IOError):
            monitor = Monitor('/somethingthatdoesnotexist')

    def assertChanged(self, monitor):
        # First time should be yep
        self.assertTrue(monitor.has_changed())
        # Calling it again (because nothing has changed) should be nope
        self.assertFalse(monitor.has_changed())

    def assertNotChanged(self, monitor):
        self.assertFalse(monitor.has_changed())

    def test_will_detect_new_file(self):
        shutil.copytree(join(self.fixtures, 'site_normal'), self.working)
        monitor = Monitor(self.working)

        self.assertNotChanged(monitor)

        open(join(self.working, 'knights_ni.rst'), 'w').close()

        self.assertChanged(monitor)

    def test_will_detect_file_deleted(self):
        shutil.copytree(join(self.fixtures, 'site_normal'), self.working)
        monitor = Monitor(self.working)

        open(join(self.working, 'knights_ni.rst'), 'w').close()
        open(join(self.working, 'the_french.rst'), 'w').close()
        open(join(self.working, 'three_headed_knight.rst'), 'w').close()
        open(join(self.working, 'template', 'index.html'), 'w').close()

        self.assertNotChanged(monitor)

        unlink(join(self.working, 'knights_ni.rst'))

        self.assertChanged(monitor)

        unlink(join(self.working, 'template', 'index.html'))

        self.assertChanged(monitor)

    def test_will_detect_file_modified(self):
        shutil.copytree(join(self.fixtures, 'site_normal'), self.working)
        monitor = Monitor(self.working)

        self.assertNotChanged(monitor)

        time.sleep(1.0)
        with open(join(self.working, 'the_quest.rst'), 'w') as fh:
            fh.write('Clippity cloppity clippity cloppity coconut')

        self.assertChanged(monitor)

        time.sleep(1.0)
        with open(join(self.working, 'template', 'index.html'), 'w') as fh:
            fh.write('<htNI!l><htNI!l>')

        self.assertChanged(monitor)

    def test_will_ignore_directories(self):
        shutil.copytree(join(self.fixtures, 'site_normal'), self.working)
        mkdir(join(self.working, 'output'))

        with open(join(self.working, 'output', 'the_quest.html'), 'w') as fh:
            fh.write('<html>Clippity cloppity coconut</html>')

        monitor = Monitor(self.working)

        self.assertNotChanged(monitor)

        time.sleep(1.0)
        open(join(self.working, 'output', 'the_quest.html'), 'w').close()

        self.assertChanged(monitor)

        # Now we ignore the output directory
        monitor = Monitor(self.working,
            ignore_directory=join(self.working, 'output'))

        self.assertNotChanged(monitor)

        time.sleep(1.0)
        open(join(self.working, 'output', 'the_quest.html'), 'w').close()

        self.assertNotChanged(monitor)
