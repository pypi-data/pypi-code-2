'''Unit-tests various XML/CSV validation scenarios (called tests also) in 
selector.py.'''
from selector import *
import unittest, shutil, os, time
from threading import Thread

file_location = '/home/eric/Alexandria_Consulting/Suncoast/JFCS/input_xml/Example_HUD_HMIS_2_8_Instance.xml'
file_from_location = '/home/eric/Alexandria_Consulting/Suncoast/JFCS/Example_HUD_HMIS_2_8_Instance.xml'
file_to_dir_loc = '/home/eric/Alexandria_Consulting/Suncoast/JFCS/input_xml'
        
class CreateFile(Thread):
    def __init__(self):
       Thread.__init__(self)
       print '\nHi, thread initting, cleaning up first'
       if os.path.isfile(file_location) is True:
           print '\ndeleting old version in thread'
           os.remove(file_location)
       
    def run(self):
        print 'hi, thread running'
        selector_obj = Selector()
        file_handler = FileHandler()
        #this won't work unless you make a separate thread.
        new_file = file_handler.monitor()
        self.results = selector_obj.validate(new_file)
        return

class SelectorTestCase(unittest.TestCase):
    '''see if the return value is a file path'''
    if os.path.isfile(file_location) is True:
        print '\ndeleting old version in main thread'
        os.remove(file_location)
        
    def test_validation_valid(self):
        '''Tests if HMIS XML 2.8 test is validating properly.'''
        c = CreateFile()
        c.start()
        time.sleep(1)
        print "main part running"
        #from_file = open(file_from_location,'w')
        #to_dir = open(file_to_dir_loc, 'w')
        print 'copying file'
        shutil.copy(file_from_location, file_to_dir_loc)
        print '\nStopping the thread'
        c.join()
        print 'Thread stopped.'
        if os.path.isfile(file_location) is True:
            print 'deleting old version in main thread end'
            os.remove(file_location)
        self.assertEqual(c.results, [False, True, False])
        
if __name__ == '__main__':
    unittest.main()