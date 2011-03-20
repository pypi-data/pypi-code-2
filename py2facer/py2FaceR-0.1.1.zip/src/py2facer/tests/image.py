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
from py2facer import tests
from py2facer.lib import picasa, image
from py2facer.lib.utils import InvalidState

class TestImagePhotoFaces(unittest.TestCase):
    def testBasic(self):
        picasacontact = picasa.Contact('bob', ['bob@gmail.com'], 'simplehash')
        img = image.Image(image_path=tests.TESTFILES['img'])
        img.add_face(google_id=picasacontact)
        self.assertEqual(len(img.people), 1)
        self.assertRaises(AttributeError, setattr, img, 'people', [])
        self.assertEqual(len(img.people), 1)

class TestImageProperties(unittest.TestCase):
    def testKnownImage(self):
        img = image.Image(image_path=tests.TESTFILES['img'])
        self.assertEqual(img.height, 362)
        self.assertEqual(img.width, 585)

class TestContainedPerson(unittest.TestCase):
    def setUp(self):
        self.img = image.Image(image_path=tests.TESTFILES['img'])

    def testOnePerson(self):
        self.img.add_face(google_id='testhash',
                          x_pos=100,
                          y_pos=101,
                          width=5,
                          height=6)
        for person in self.img.people:
            self.assertEqual(person.google_id, 'testhash')
            self.assertEqual(person.x_pos, 100)
            self.assertEqual(person.y_pos, 101)
            self.assertEqual(person.width, 5)
            self.assertEqual(person.height, 6)
    
    def testInvalidSpecs(self):
        self.assertRaises(InvalidState, self.img.add_face, google_id='testhash',
                          x_pos=600, y_pos=640, width=5, height=6)
        self.assertRaises(InvalidState, self.img.add_face, google_id='testhash',
                          x_pos=500, y_pos=540, width=500, height=6)
