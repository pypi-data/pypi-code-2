'''Unit-tests various encryption/decryption scenarios (called tests also) in 
clssecurity.py.'''
from clssecurity import ClsSecurity
import unittest
import os
import testcase_settings
import postgresutils

class CryptTestCase(unittest.TestCase):
    '''see if the return value is a file path'''
    #def test_decrypt2Stream(self):
    #    '''
    #    '''
        
    def test_decrypt_valid(self):
        '''Tests to see if we can decrypt a known file and compare that with existing 'unencrypted' version of the file'''
        security = ClsSecurity()
        instance_filename = os.path.join("%s" % testcase_settings.INPUTFILES_PATH, testcase_settings.XML_ENCRYPTED_FILE)
        sourceFile = os.path.join("%s" % testcase_settings.INPUTFILES_PATH, testcase_settings.XML_FILE_VALID)
        dData = security.decryptFile(instance_filename)
        stream = open(sourceFile, 'r')
        uData = stream.read()
        self.assertEqual(uData, dData)
        stream.close()
        
    def test_encrypt_valid(self):
        '''Tests we can encrypt a file.  Encrypted file will be compared against a known "encrypted" file outside of framework'''
        
        security = ClsSecurity()
        #instance_filename = '/home/eric/workspace/reposHUD/trunk/Coastal_HSXML_converter/test_xml/coastal_sheila.xml'#IGNORE:C0301
        instance_filename = os.path.join("%s" % testcase_settings.INPUTFILES_PATH, testcase_settings.XML_DECRYPTED_FILE)
        outputFile = instance_filename + ".asc"
        inputFile = os.path.join("%s" % testcase_settings.INPUTFILES_PATH, testcase_settings.XML_FILE_VALID)
        #result = select.validate(HUDHMIS28XMLTest(), instance_filename)
        security.setFingerprint(testcase_settings.XML_ENCRYPT_FINGERPRINT)
        security.encryptFile(instance_filename, outputFile)
        dData = security.decryptFile(outputFile)
        # read the input file contents
        stream = open(inputFile, 'r')
        uData = stream.read()
        self.assertEqual(uData, dData)
        stream.close()
        
        
if __name__ == '__main__':
    # Wipe the DB first
    #import postgresutils
    #UTILS = postgresutils.Utils()
    #UTILS.blank_database()
    
    unittest.main()