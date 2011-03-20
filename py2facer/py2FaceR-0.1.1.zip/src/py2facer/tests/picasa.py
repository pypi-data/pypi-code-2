license = ''' Copyright (C) 2011  <see AUTHORS file>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import unittest
from py2facer.lib import picasa, image
from py2facer import tests
import os

# W0212 : Unit tests are suppose to access proctected members
# W0104 : No apparent effect doesn't mean we're not exercising the code
# pylint: disable=W0104,W0212

class TestPicasaContact(unittest.TestCase):
    def testBasicContact(self):
        contact = picasa.Contact('Bob Smith', emails='email@server.com', google_hash='testhash')
        self.assertEqual(type(contact.emails), list)
        contact = picasa.Contact('Bob Smith', emails=['email@server.com', 'email2@server.com'], google_hash='testhash')
        self.assertEqual(type(contact.emails), list)
        contact = picasa.Contact('Bob Smith', emails=('email@server.com', 'email2@server.com'), google_hash='testhash' )
        self.assertEqual(type(contact.emails), list)
        
class TestPicasaContactParser(unittest.TestCase):
    def setUp(self):
        self.contact_parser = picasa.ContactParser()

    def tearDown(self):
        self.contact_parser = None

    def testBlankStream(self):
        from xml.parsers.expat import ExpatError
        self.assertRaises(ExpatError, self.contact_parser.parse_xml, ())
    
    def testBadContact(self):
        try:
            self.contact_parser['badkey']
        except KeyError, e:
            assert e.message == 'badkey'
    
    def testParseSimple(self):
        self.contact_parser.parse_xml(open(tests.TESTFILES['contacts']))
        self.contact_parser['contact_hash']
    
    def testSetContact(self):
        self.contact_parser.parse_xml(open(tests.TESTFILES['contacts']))
        try:
            self.contact_parser['contact_hash'] = 'NewValue'
        except TypeError, e:
            assert str(e.message).endswith('object does not support item assignment'), e.message

  
class TestPicasaIniParser(unittest.TestCase):
    def setUp(self):
        self.iniparser = picasa.FaceParser()
        
    def testBadPath(self):
        self.iniparser._parse_directory('NotAPath')
        self.assertEqual(len(self.iniparser._ini_files), 0)
        
    def testParse(self):
        parsed = self.iniparser._parse_ini(open(tests.TESTFILES['ini']), base_path=os.path.dirname(tests.TESTFILES['ini']))
        self.assertEqual(len(parsed['test.jpg']), 2)
        self.assertEqual(len(parsed['007.jpg']), 1)
    
    def testAddFaces(self):
        img = image.Image(image_path=tests.TESTFILES['img'])
        self.iniparser.add_people_to_image(img)
        self.assertEqual(len(img._people), 2)
