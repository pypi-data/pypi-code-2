from fileinputwatcher import FileInputWatcher
from time import sleep
import unittest, os, Queue
import testCase_settings

class FileInputTestCase(unittest.TestCase):
    '''test if the threaded callback is working when file created'''
    def test_file_add(self):
        self.queue = Queue.Queue(0)
        dir = testCase_settings.INPUTFILES_PATH
        testFile = testCase_settings.TEST_FILE
        file_input_watcher = FileInputWatcher(dir, self.queue)
        if os.path.isfile(os.path.join(dir, testFile)) is True:
            os.remove(os.path.join(dir, testFile))
        #Start a monitoring thread.  It ends on its own.
        file_input_watcher.monitor()
        #now make a file whilst pyinotify thread is running
        sleep(1)
        f = open(os.path.join(dir, testFile),'w')
        f.close()
        result = self.queue.get(block='true')
        #print 'result is', result
        if result is not None:
            #print 'self.queue.get() is ', result 
            file_input_watcher.stop_monitoring()
        #clean up file mess created
        if os.path.isfile(os.path.join(dir, testFile)) is True:
            os.remove(os.path.join(dir, testFile))
        self.assertEqual(result, os.path.join(dir, testFile))
        
if __name__ == '__main__':
    unittest.main()