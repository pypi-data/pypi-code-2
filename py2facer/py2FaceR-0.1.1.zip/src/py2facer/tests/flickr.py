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
from py2facer.lib import image, picasa
from py2facer.lib.flickr import FlickrContactManager, FlickrContact, DbProxy,\
    FlickrImageManager, FlickrImage
from py2facer.lib.utils import InvalidState
from xml.etree import ElementTree
import flickrapi
from py2facer import tests

# W0212 : Unit tests are suppose to access proctected members
# W0104 : No apparent effect doesn't mean we're not exercising the code
# pylint: disable=W0212

class FlickrApiMgrStub(object):
    def __init__(self):
        self.result = None
        self.expected_args = None
        self.raise_exception = False
    
    def _check_args(self, kwargs):
        if self.expected_args is None or len(self.expected_args) == 0:
            return
        expected_args = self.expected_args
        if type(expected_args) is list:
            expected_args = expected_args.pop(0)
        if expected_args is None or len(expected_args) == 0:
            return
        for key, value in kwargs.iteritems():
            assert key in expected_args, 'Expected arg %s : %s not found in %s' % (key, value, kwargs)
            assert kwargs[key] == expected_args[key], '%s != %s' % (kwargs[key], expected_args[key])

    def _do_return(self, **kwargs):
        if self.raise_exception:
            raise AssertionError('Unexpected call')
        self._check_args(kwargs)
        if type(self.result) is list:
            result = self.result.pop(0)
        else:
            result = self.result
        if result.attrib['stat'] != 'ok':
            err = result.getchildren()[0]
            raise flickrapi.FlickrError('Error: %(code)s: %(msg)s' % err.attrib)
        return result
    
    def login(self):
        if self.raise_exception:
            raise AssertionError('Unexpected call')
        return
    
    def __getattr__(self, name):
        return self._do_return
    
    def xml_to_result(self, xml):
        if type(xml) in (list, tuple):
            self.result = []
            for xml_res in xml:
                self.result.append(ElementTree.XML(xml_res))
        else:
            self.result = ElementTree.XML(xml)
    
class TestFlickrContactManager(unittest.TestCase):
    CONTACT_FOUND = '''<rsp stat="ok"><user id="00000000@N00" nsid="11111111@N00"><username>bob</username></user></rsp>'''
    CONTACT_NOTFOUND = '''<rsp stat="fail"><err code="1" msg="User not found"/></rsp>'''
    
    def __init__(self, *args, **kwargs):
        super(TestFlickrContactManager, self).__init__(*args, **kwargs)
        
    def setUp(self):
        tests.delOldDb()
        self.flickr_api_mgr = FlickrApiMgrStub()
        self.picasa_contacts = picasa.ContactParser()
        self.db_proxy = DbProxy(db_url=tests.TESTDBURL % tests.DB_COUNTER)
        self.contactmgr = FlickrContactManager(db_proxy=self.db_proxy)
        
    def tearDown(self):
        # can't do a destroy on the DB every time
        # dispose doesn't actually close all the connections
        # need to go for a commit and rollback kind of scenario for this to work
        self.db_proxy._engine.dispose()
        tests.DB_COUNTER += 1
        tests.delOldDb()
        
    def addSimpleContact(self):
        contact = picasa.Contact('bob', ['bob@gmail.com'], 'simplehash')
        self.picasa_contacts._contacts[contact.google_hash] = contact
        
    def testNoProxy(self):
        self.assertRaises(InvalidState, self.contactmgr.sync_flickr, 
                          self.picasa_contacts)
        
    def testSyncEmpty(self):
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(0, self.contactmgr.session.query(FlickrContact).count())
    
    def testSyncOne(self):
        self.addSimpleContact()
        self.flickr_api_mgr.xml_to_result(self.CONTACT_FOUND)
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).count())
    
    def testSyncResync(self):
        self.addSimpleContact()
        self.flickr_api_mgr.xml_to_result(self.CONTACT_FOUND)
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).count())
        # Resync same set of contacts
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).count())
        # Add a new contact, then sync and expect both hashes, but one nsid
        contact = picasa.Contact('bob2', ['bob2@gmail.com'], 'simplehash2')
        self.flickr_api_mgr.xml_to_result(self.CONTACT_NOTFOUND)
        self.picasa_contacts._contacts[contact.google_hash] = contact
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(2, self.contactmgr.session.query(FlickrContact).count())
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).filter(FlickrContact.nsid != None).count())
        # Recheck but this shouldn't call flickr
        self.flickr_api_mgr.raise_exception = True
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(2, self.contactmgr.session.query(FlickrContact).count())
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).filter(FlickrContact.nsid != None).count())
        # Force recheck which should call once and this time we find Bob
        self.flickr_api_mgr.raise_exception = False
        self.flickr_api_mgr.xml_to_result(self.CONTACT_FOUND)
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    force_recheck=True,
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(2, self.contactmgr.session.query(FlickrContact).count())
        self.assertEqual(2, self.contactmgr.session.query(FlickrContact).filter(FlickrContact.nsid != None).count())
        
    def testSyncNotFound(self):
        self.addSimpleContact()
        self.flickr_api_mgr.xml_to_result(self.CONTACT_NOTFOUND)
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(0, self.contactmgr.session.query(FlickrContact).filter(FlickrContact.nsid != None).count())
    
    def testSyncMultiEmail(self):
        contact = picasa.Contact('bob2', ['bob2@hotmail.com', 'bob2@gmail.com'], 'simplehash2')
        self.picasa_contacts._contacts[contact.google_hash] = contact
        self.flickr_api_mgr.xml_to_result((self.CONTACT_NOTFOUND, self.CONTACT_FOUND))
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).count())
        # Resync same set of contacts
        self.contactmgr.sync_flickr(self.picasa_contacts, 
                                    flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.contactmgr.session.query(FlickrContact).count())

class TestFlickrPhotoManager(unittest.TestCase):
    ONE_FACES = '''<rsp stat="ok">
                   <people total="1">
                    <person nsid="11111111@N00" username="unchecked" iconserver="1" iconfarm="1"
                            realname="unchecked" added_by="12037949754@N01"/>
                   </people>
                  </rsp>'''
    ONE_FACE_WLOC = '''<rsp stat="ok">
                   <people total="1">
                    <person nsid="11111111@N00" username="unchecked" iconserver="1" iconfarm="1"
                            realname="unchecked" added_by="12037949754@N01" x="50" y="50"
                            w="100" h="100"/>
                   </people>
                  </rsp>'''
    OTHER_FACES = '''<rsp stat="ok">
                   <people total="1">
                    <person nsid="UnKNOWN@N00" username="unchecked" iconserver="1" iconfarm="1"
                            realname="unchecked" added_by="12037949754@N01"/>
                   </people>
                  </rsp>'''
    OK_RESULT = '''<rsp stat="ok" />'''
    NO_FACES = '''<rsp stat="ok"><people total="0" /></rsp>'''
    PHOTO_FOUND = '''<rsp stat="ok">
                <photos page="1" pages="1" perpage="10" total="1"> 
                 <photo id="2650" owner="47058503995@N01" secret="a123456" server="2" title="007" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-10 19:27:46" /> 
                </photos>
                </rsp>'''
    PHOTO_FOUNDPG1 = '''<rsp stat="ok">
                        <photos page="1" pages="2" perpage="10" total="15">
                            <photo id="2636" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2637" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2638" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2639" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2640" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2641" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2642" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2643" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2644" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                            <photo id="2645" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
                        </photos>
                        </rsp>'''
    PHOTO_FOUNDPG2 = '''<rsp stat="ok">
        <photos page="2" pages="2" perpage="10" total="15">
            <photo id="2646" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
            <photo id="2647" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
            <photo id="2648" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
            <photo id="2649" owner="47058503995@N01" secret="a123456" server="2" title="test_04" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-01 12:00:00" />
            <photo id="2650" owner="47058503995@N01" secret="a123456" server="2" title="007" ispublic="1" isfriend="0" isfamily="0" datetaken="2011-01-10 19:27:46" />
        </photos>
        </rsp>'''
    
    PHOTO_NOTFOUND = '''<rsp stat="fail"><err code="105" msg="Service currently unavailable"/></rsp>'''
    IMAGES = None # can be modified by other tests, so init in setUp
    
    def __init__(self, *args, **kwargs):
        super(TestFlickrPhotoManager, self).__init__(*args, **kwargs)
        
    def setUp(self):
        self.IMAGES = [image.Image(tests.TESTFILES['img']), 
                       image.Image('%s/testdata/007.JPG' % tests.BASEPATH),
                       image.Image('%s/testdata/Nobody.jpg' % tests.BASEPATH)]
        tests.delOldDb()
        self.flickr_api_mgr = FlickrApiMgrStub()
        self.db_proxy = DbProxy(db_url=tests.TESTDBURL % tests.DB_COUNTER)
        self.photomgr = FlickrImageManager(db_proxy=self.db_proxy)
        
    def tearDown(self):
        # can't do a destroy on the DB every time
        # dispose doesn't actually close all the connections
        # need to go for a commit and rollback kind of scenario for this to work
        self.db_proxy._engine.dispose()
        tests.DB_COUNTER += 1
        tests.delOldDb()
    
    def testNoResult(self):
        # Add a new contact, then sync and expect both hashes, but one nsid
        self.flickr_api_mgr.xml_to_result(self.PHOTO_NOTFOUND)
        self.photomgr.add_photo(self.IMAGES[1])
        self.assertRaises(flickrapi.FlickrError, self.photomgr.link_photos, flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(0, self.photomgr.session.query(FlickrImage).count())
    
    def testBadImg(self):
        self.assertRaises(InvalidState, self.photomgr.add_photo, 'NotAnImage')
        # Image with no exif data
        self.assertRaises(InvalidState, self.photomgr.add_photo, self.IMAGES[0])
    
    def testOneResult(self):
        self.flickr_api_mgr.xml_to_result(self.PHOTO_FOUND)
        self.photomgr.add_photo(self.IMAGES[1])
        self.photomgr.link_photos(flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.photomgr.session.query(FlickrImage).count())
        self.assertEqual(1, self.photomgr.session.query(FlickrImage).filter(FlickrImage.photo_id != None).count())

    def testMultiresult(self):
        self.flickr_api_mgr.xml_to_result((self.PHOTO_FOUNDPG1, self.PHOTO_FOUNDPG2))
        self.photomgr.add_photo(self.IMAGES[1])
        self.photomgr.link_photos(flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.photomgr.session.query(FlickrImage).count())
        self.assertEqual(1, self.photomgr.session.query(FlickrImage).filter(FlickrImage.photo_id != None).count())

    def testNoReAdd(self):
        '''If we've already added this photo to the DB but it happens to pop up
        in the query once again
        '''
        
        self.flickr_api_mgr.xml_to_result((self.PHOTO_FOUND, self.PHOTO_FOUNDPG1, self.PHOTO_FOUNDPG2))
        self.photomgr.add_photo(self.IMAGES[1])
        self.photomgr.link_photos(flickr_proxy=self.flickr_api_mgr)
        self.photomgr.link_photos(flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, self.photomgr.session.query(FlickrImage).count())
        self.assertEqual(1, self.photomgr.session.query(FlickrImage).filter(FlickrImage.photo_id != None).count())
        
    def syncface(self, img):
        picasa_contacts = picasa.ContactParser()
        picasa_faceparser = picasa.FaceParser()
        contactmgr = FlickrContactManager(db_proxy=self.db_proxy)
        contact = picasa.Contact('bob', ['bob@gmail.com'], 'contact_hash')
        picasa_contacts._contacts[contact.google_hash] = contact
        contactmgr.sync_flickr(picasa_contacts, 
                               flickr_proxy=self.flickr_api_mgr)
        self.assertEqual(1, contactmgr.session.query(FlickrContact).count())
        picasa_faceparser.add_people_to_image(self.IMAGES[1], bounding_box=True)
        self.photomgr.add_photo(img)
        self.photomgr.link_photos(flickr_proxy=self.flickr_api_mgr)
        self.photomgr.sync_faces(flickr_proxy=self.flickr_api_mgr)

    def testSimpleSyncNoFacesInImg(self):
        self.flickr_api_mgr.xml_to_result((TestFlickrContactManager.CONTACT_FOUND,
                                   self.PHOTO_FOUND,
                                   ))
        self.flickr_api_mgr.expected_args = [None, None, None]
        self.syncface(self.IMAGES[2])
        if type(self.flickr_api_mgr.result) is list and len(self.flickr_api_mgr.result) > 0:
            raise AssertionError('Results left over in flickr_api_mgr')

    
    def testSimpleSyncOneFace(self):
        self.flickr_api_mgr.xml_to_result((TestFlickrContactManager.CONTACT_FOUND,
                                   self.PHOTO_FOUND,
                                   self.NO_FACES,
                                   self.OK_RESULT
                                   ))
        # The fail call shouldn't happen since there are no people in the image
        self.flickr_api_mgr.expected_args = [None, None, None, 
                                             {'user_id' : u'11111111@N00',
                                              'person_h': 153.45149253731344, 
                                              'person_w': 132.34608208955225, 
                                              'photo_id': 2650, 
                                              'person_x': 111.70708955223881, 
                                              'person_y': 28.334888059701495}]
        self.syncface(self.IMAGES[1])
        if type(self.flickr_api_mgr.result) is list and len(self.flickr_api_mgr.result) > 0:
            raise AssertionError('Results left over in flickr_api_mgr')
    
    def testNoResyncFace(self):
        self.flickr_api_mgr.xml_to_result((TestFlickrContactManager.CONTACT_FOUND,
                                   self.PHOTO_FOUND,
                                   self.NO_FACES,
                                   self.OK_RESULT,
                                   self.ONE_FACE_WLOC
                                   ))
        self.syncface(self.IMAGES[1])
        self.photomgr.sync_faces(flickr_proxy=self.flickr_api_mgr)
        if type(self.flickr_api_mgr.result) is list and len(self.flickr_api_mgr.result) > 0:
            raise AssertionError('Results left over in flickr_api_mgr')
    
    def testResyncFaceWithCoords(self):
        self.flickr_api_mgr.xml_to_result((TestFlickrContactManager.CONTACT_FOUND,
                                   self.PHOTO_FOUND,
                                   self.NO_FACES,
                                   self.OK_RESULT,
                                   self.ONE_FACES,
                                   self.OK_RESULT,
                                   ))
        self.syncface(self.IMAGES[1])
        self.photomgr.sync_faces(flickr_proxy=self.flickr_api_mgr)
        if type(self.flickr_api_mgr.result) is list and len(self.flickr_api_mgr.result) > 0:
            raise AssertionError('Results left over in flickr_api_mgr')
    
    def testResyncWithNewFace(self):
        self.flickr_api_mgr.xml_to_result((TestFlickrContactManager.CONTACT_FOUND,
                                   self.PHOTO_FOUND,
                                   self.NO_FACES,
                                   self.OK_RESULT,
                                   self.NO_FACES,
                                   self.OK_RESULT,
                                   ))
        self.syncface(self.IMAGES[1])
        self.photomgr.sync_faces(flickr_proxy=self.flickr_api_mgr)
        if type(self.flickr_api_mgr.result) is list and len(self.flickr_api_mgr.result) > 0:
            raise AssertionError('Results left over in flickr_api_mgr')
    