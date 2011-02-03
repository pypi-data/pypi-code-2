# -*- coding: utf-8 -*-
'''Testing the MongoGridFS adapter.'''
# pylint: disable=R0904

## Created: 2010-09-11 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import unittest
from mock import Mock
from hashlib import md5
import json

from gridfs.errors import NoFile

from matanui.exceptions import MataNuiStorerException
from matanui.exceptions import MataNuiStorerNotFoundException
from matanui.mongogridfs import MongoGridFS
from matanui.storerinterface import MetadataObject
from matanui import storerinterface
from test import testdata

class MongoGridFSTest(unittest.TestCase):
    """Testing of the MongoGridFS class."""
    # pylint: disable=W0212
    
    def setUp(self): # pylint: disable=C0111
        testdata.GOOD_GRIDFS.seek(0)
        testdata.GOOD_INPUT.data.seek(0)
        

    def test_make_instance(self):
        '''test making a MongoGridFS instance'''
        instance = MongoGridFS()
        self.assert_(isinstance(instance, MongoGridFS))


    def test_get_content_by_name(self):
        '''test of retrieving a file by name'''
        a_string = 'Hello Test!'
        a_chunk_size = 5
        gridfs_handle = Mock()
        gridfs_handle.get_last_version.return_value = testdata.GOOD_GRIDFS
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        a_file_object = a_gridfs.get_content('/spam/eggs.txt')
        content = a_file_object.data.read()
        self.assert_(a_gridfs._fs.get_last_version.called)
        self.assertEquals(content, a_string)
        self.assertEquals(a_file_object.length, len(a_string))
        self.assertEquals(a_file_object.block_size, a_chunk_size)
        self.assertEquals(a_file_object.checksum,
                          str(md5(a_string).hexdigest()))
        

    def test_get_content_by_oid(self):
        '''test of retrieving a file by object ID'''
        a_string = 'Hello Test!'
        a_chunk_size = 5
        gridfs_handle = Mock()
        gridfs_handle.get.return_value = testdata.GOOD_GRIDFS
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        a_file_object = a_gridfs.get_content(object_id='4c91b12838dd124df1000000')
        content = a_file_object.data.read()
        self.assert_(a_gridfs._fs.get.called)
        self.assertEquals(content, a_string)
        self.assertEquals(a_file_object.length, len(a_string))
        self.assertEquals(a_file_object.block_size, a_chunk_size)
        self.assertEquals(a_file_object.checksum,
                          str(md5(a_string).hexdigest()))
        

    def test_get_content_by_oid_wrong_name(self):
        '''test of retrieving a file by object ID with wrong file name'''
        gridfs_handle = Mock()
        content_handle = Mock()
        content_handle._id = testdata.GOOD_GRIDFS.object_id
        content_handle.filename = '/bacon/eggs.txt'
        gridfs_handle.get.return_value = content_handle
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        self.assertRaises(MataNuiStorerException, a_gridfs.get_content,
                          object_id=testdata.GOOD_GRIDFS.object_id,
                          filename=testdata.GOOD_GRIDFS.name)
        self.assert_(a_gridfs._fs.get.called)
        

    def test_get_non_existing_filename(self):
        '''test of retrieving a non existent file'''
        gridfs_handle = Mock()
        gridfs_handle.get_last_version.side_effect = NoFile() 
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        self.assertRaises(MataNuiStorerNotFoundException, a_gridfs.get_content,
                          '/bacon/eggs.txt')
        

    def test_put_content(self):
        '''test of uploading a file'''
        object_id_expected = '4c91b12838dd124df1000000'
        a_gridfs = MongoGridFS()
        a_gridfs._fs = Mock()
        a_gridfs._fs.put.return_value = object_id_expected
        a_gridfs._files_collection = Mock()
        a_gridfs._files_collection.find.return_value = []
        object_id = a_gridfs.put_content(testdata.GOOD_INPUT)
        self.assert_(a_gridfs.fs.put.called)
        self.assertEquals(object_id, object_id_expected)


    def test_delete_file_by_name(self):
        '''test of deleting a file by name'''
        gridfs_handle = Mock()
        gridfs_handle.get_last_version.return_value = testdata.GOOD_GRIDFS
        gridfs_handle.get_last_version.return_value._id = gridfs_handle.get_last_version.return_value.object_id
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        object_id = a_gridfs.delete_file('/spam/eggs.txt')
        self.assert_(a_gridfs._fs.get_last_version.called)
        self.assert_(a_gridfs._fs.delete.called)
        self.assertEqual(testdata.GOOD_GRIDFS.object_id, object_id)
    

    def test_delete_file_by_oid_without_name(self):
        '''test of deleting a file by oid without file name'''
        gridfs_handle = Mock()
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        object_id = '4c91b12838dd124df1000000'
        a_gridfs.delete_file(object_id=object_id)
        self.assert_(a_gridfs._fs.delete.called)
        
    
    def test_delete_file_by_oid_with_name(self):
        '''test of deleting a file by oid with file name'''
        gridfs_handle = Mock()
        gridfs_handle.get.return_value = testdata.GOOD_GRIDFS
        gridfs_handle.get.return_value._id = gridfs_handle.get.return_value.object_id
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        result = a_gridfs.delete_file(object_id=testdata.GOOD_GRIDFS.object_id,
                                      filename=testdata.GOOD_GRIDFS.name)
        self.assert_(a_gridfs._fs.get.called)
        self.assert_(a_gridfs._fs.delete.called)
        self.assertEqual(result, testdata.GOOD_GRIDFS.object_id)


    def test_delete_file_by_oid_with_name_slash(self):
        '''test of deleting a file by oid with file name "/"'''
        gridfs_handle = Mock()
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        a_gridfs.delete_file(object_id=testdata.GOOD_GRIDFS.object_id,
                             filename='/')
        self.assert_(a_gridfs._fs.delete.called)
        

    def test_delete_file_by_oid_with_wrong_name(self):
        '''test of deleting a file by oid with wrong file name'''
        gridfs_handle = Mock()
        content_handle = Mock()
        content_handle._id = testdata.GOOD_GRIDFS.object_id
        content_handle.name = '/bacon/eggs.txt'
        gridfs_handle.get.return_value = content_handle
        a_gridfs = MongoGridFS()
        a_gridfs._fs = gridfs_handle
        self.assertRaises(MataNuiStorerException, a_gridfs.delete_file,
                          object_id=testdata.GOOD_GRIDFS.object_id,
                          filename=testdata.GOOD_GRIDFS.name)
        self.assert_(a_gridfs._fs.get.called)
        self.assert_(not a_gridfs._fs.delete.called)


    def test_get_metadata_by_name(self):
        '''test of retrieving meta-data by file name'''
        a_file_object = {'_id': testdata.GOOD_GRIDFS.object_id,
                         'metadata': testdata.GOOD_METADATA,
                         'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find.return_value = [a_file_object]
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        oid, result = a_gridfs.get_metadata('/spam/eggs.txt')
        self.assert_(json.dumps(testdata.GOOD_METADATA) in result.json_string)
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find.called)
        

    def test_get_metadata_by_name_no_metadata(self):
        '''test of retrieving meta-data by file name with no metadata'''
        a_file_object = {'_id': testdata.GOOD_GRIDFS.object_id,
                         'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find.return_value = [a_file_object]
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        oid, result = a_gridfs.get_metadata('/spam/eggs.txt')
        self.assert_('metadata' not in result.content)
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find.called)
        

    def test_get_metadata_by_oid(self):
        '''test of retrieving meta-data by OID'''
        a_file_object = {'_id': testdata.GOOD_GRIDFS.object_id,
                         'metadata': testdata.GOOD_METADATA,
                         'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find_one.return_value = a_file_object
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        oid, result = a_gridfs.get_metadata(object_id='4c91b12838dd124df1000000')
        self.assert_(json.dumps(testdata.GOOD_METADATA) in result.json_string)
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find_one.called)

   
    def test_get_metadata_by_oid_no_metadata(self):
        '''test of retrieving meta-data by OID with no metadata'''
        a_file_object = {'_id': testdata.GOOD_GRIDFS.object_id,
                         'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find_one.return_value = a_file_object
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        oid, result = a_gridfs.get_metadata(object_id='4c91b12838dd124df1000000')
        self.assert_('metadata' not in result.content)
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find_one.called)


    def test_set_metadata_by_name(self):
        '''test of setting meta-data by file name'''
        an_entry = {'_id': testdata.GOOD_GRIDFS.object_id,
                    'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find.return_value = [an_entry]
        gridfs_handle.update.return_value = None
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        metadata = MetadataObject({'metadata': testdata.GOOD_METADATA})
        oid = a_gridfs.set_metadata(metadata, filename='/spam/eggs.txt')
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find.called)
        self.assert_(gridfs_handle.update.called)
        self.assertEqual(gridfs_handle.update.call_count, 1)
        self.assert_('$set' not in gridfs_handle.update.call_args_list[0][0][1].keys())
        self.assertEqual(testdata.GOOD_GRIDFS.object_id,
                         str(gridfs_handle.update.call_args[0][0]['_id']))
        self.assert_(str(testdata.GOOD_METADATA)
                     in str(gridfs_handle.update.call_args[0][1]))
        

    def test_set_metadata_by_oid(self):
        '''test of setting meta-data by OID'''
        an_entry = {'_id': testdata.GOOD_GRIDFS.object_id,
                    'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find_one.return_value = an_entry
        gridfs_handle.update.return_value = None
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        metadata = MetadataObject({'metadata': testdata.GOOD_METADATA})
        oid = a_gridfs.set_metadata(metadata,
                                    object_id=testdata.GOOD_GRIDFS.object_id,
                                    filename='/spam/eggs.txt')
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find_one.called)
        self.assert_(gridfs_handle.update.called)
        self.assertEqual(gridfs_handle.update.call_count, 1)
        self.assert_('$set' not in gridfs_handle.update.call_args_list[0][0][1].keys())
        self.assertEqual(testdata.GOOD_GRIDFS.object_id,
                         str(gridfs_handle.update.call_args[0][0]['_id']))
        self.assert_(str(testdata.GOOD_METADATA)
                     in str(gridfs_handle.update.call_args[0][1]))
    

    def test_set_sys_metadata_by_name(self):
        '''test of setting system meta-data by file name'''
        an_entry = {'_id': testdata.GOOD_GRIDFS.object_id,
                    'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find.return_value = [an_entry]
        gridfs_handle.update.return_value = None
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        metadata = MetadataObject({'owner': 'brian'})
        oid = a_gridfs.set_metadata(metadata, filename='/spam/eggs.txt')
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find.called)
        self.assert_(gridfs_handle.update.called)
        self.assertEqual(gridfs_handle.update.call_count, 1)
        self.assertEqual(testdata.GOOD_GRIDFS.object_id,
                         str(gridfs_handle.update.call_args[0][0]['_id']))
        self.assert_(str(metadata.content)[1:-1]
                     in str(gridfs_handle.update.call_args[0][1]))
        

    def test_set_sys_metadata_by_oid(self):
        '''test of setting system meta-data by OID'''
        an_entry = {'_id': testdata.GOOD_GRIDFS.object_id,
                    'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find_one.return_value = an_entry
        gridfs_handle.update.return_value = None
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        metadata = MetadataObject({'owner': 'brian'})
        oid = a_gridfs.set_metadata(metadata,
                                    object_id=testdata.GOOD_GRIDFS.object_id,
                                    filename='/spam/eggs.txt')
        self.assertEqual(oid, testdata.GOOD_GRIDFS.object_id)
        self.assert_(gridfs_handle.find_one.called)
        self.assert_(gridfs_handle.update.called)
        self.assertEqual(gridfs_handle.update.call_count, 1)
        self.assertEqual(testdata.GOOD_GRIDFS.object_id,
                         str(gridfs_handle.update.call_args[0][0]['_id']))
        self.assert_(str(metadata.content)[1:-1]
                     in str(gridfs_handle.update.call_args[0][1]))
    
    
    def test_set_metadata_by_oid_with_wrong_name(self):
        '''test of setting meta-data by OID with mis-matching file name'''
        an_entry = {'_id': testdata.GOOD_GRIDFS.object_id,
                    'filename': testdata.GOOD_GRIDFS.name}
        gridfs_handle = Mock()
        gridfs_handle.find_one.return_value = an_entry
        gridfs_handle.update.return_value = None
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        metadata = MetadataObject({'metadata': testdata.GOOD_METADATA})
        self.assertRaises(MataNuiStorerException, a_gridfs.set_metadata,
                          metadata,
                          object_id=testdata.GOOD_GRIDFS.object_id,
                          filename='/bacon/eggs.txt')
        self.assert_(gridfs_handle.find_one.called)
        self.assert_(not gridfs_handle.update.called)
    
    
    def test_set_metadata_by_name_missing_file(self):
        '''test of setting meta-data by name with missing file'''
        gridfs_handle = Mock()
        gridfs_handle.find_one.return_value = None
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        metadata = MetadataObject({'metadata': testdata.GOOD_METADATA})
        self.assertRaises(MataNuiStorerNotFoundException, a_gridfs.set_metadata,
                          metadata,
                          object_id=testdata.GOOD_GRIDFS.object_id,
                          filename='/bacon/eggs.txt')
        self.assert_(gridfs_handle.find_one.called)
        self.assert_(not gridfs_handle.update.called)


    def test_scrub_metadata(self):
        '''test for scrubbing the meta-data for setting'''
        # Input dict vs. the pair of output dicts.
        check_dicts = [({'filename': '/space/vessel/HeartOfGold.ship',
                         'owner': 'zaphod',
                         'contentType': 'application/x-spaceship',
                         'accessMode': 0644,
                         'metadata': {'property': 'fast as',
                                      'funFactor': 42}},
                        ({'filename': '/space/vessel/HeartOfGold.ship',
                          'owner': 'zaphod',
                          'contentType': 'application/x-spaceship',
                          'accessMode': 0644},
                         {'metadata': {'property': 'fast as',
                                       'funFactor': 42}})
                       ),
                       ({'length': 42}, ({}, {})),
                       ({'owner': 'arthur'}, ({'owner': 'arthur'}, {})),
                       ({'metadata': {'funFactor': 42}}, ({}, {'metadata': {'funFactor': 42}})),
                       ({'length': 42, 'owner': 'ford'}, ({'owner': 'ford'}, {})),
                       ({'length': 42, 'owner': 'trillian', 'metadata': {'funFactor': 42}},
                        ({'owner': 'trillian'}, {'metadata': {'funFactor': 42}})),
                      ]
        a_gridfs = MongoGridFS()
        for metadata, expected in check_dicts:
            updater, replacer = a_gridfs._scrub_metadata(metadata)
            self.assertEqual(updater, expected[0])
            self.assertEqual(replacer, expected[1])


    def test_validate_access_mode(self):
        '''test for scrubbing the meta-data for setting'''
        checks = [((0777, None, None), 0666),
                  ((0777, 0333, None), 0444),
                  ((0642, None, None), 0642),
                  ((0642, 0333, None), 0440),
                  ((0000, None, None), 0000),
                  ((0000, 0333, None), 0000),
                 ]
        a_gridfs = MongoGridFS()
        for parameters, expected in checks:
            access_mode, umask, default_permissions = parameters
            metadata = {'accessMode': access_mode}
            result = a_gridfs._validate_access_mode(metadata, umask, default_permissions)
            self.assertEqual(result, {'accessMode': expected})


    def test_list_resources(self):
        '''test for resources returned to list'''
        a_gridfs = MongoGridFS()
        for query in testdata.TEST_QUERIES:
            gridfs_handle = Mock()
            a_gridfs._files_collection = gridfs_handle
            gridfs_handle.find.return_value = testdata.make_dummy_fs_entries(testdata.TEST_ENTRIES)
            result = a_gridfs.list_resources(query)
            expected = testdata.TEST_QUERIES[query]
            self.assert_(a_gridfs._files_collection.find.called)
            self.assertEqual(len(result.content), len(expected))
            for item in result.content:
                self.assert_(item['filename'] in expected)


    def test_access_allowed_existing_files(self):
        '''test of access privilege checks to resources'''
        a_gridfs = MongoGridFS()
        for parameters, expected in testdata.PRIVILEGE_TESTS:
            entry, user, access_mode = parameters
            a_gridfs._get_mongo_file_handle_by_name = Mock()
            a_gridfs._get_mongo_file_handle_by_name.return_value = entry
            result = a_gridfs.is_access_allowed(user, access_mode,
                                                filename='/spam/eggs.txt')
            self.assertEqual(result, expected)
            self.assert_(a_gridfs._get_mongo_file_handle_by_name.called)


    def test_access_allowed_missing_files(self):
        '''test of access privilege checks to resources for a missing file'''
        a_gridfs = MongoGridFS()
        a_gridfs._get_mongo_file_handle_by_name = Mock()
        a_gridfs._get_mongo_file_handle_by_name.side_effect = MataNuiStorerNotFoundException('foo')
        result = a_gridfs.is_access_allowed('brian', storerinterface.PRIV_READ,
                                            filename='/spam/eggs.txt')
        self.assertEqual(result, False)
        self.assert_(a_gridfs._get_mongo_file_handle_by_name.called)


    def test_access_allowed_dir_mode(self):
        '''test of access privilege checks to resources for a missing file'''
        tests = [('/spam/bacon/eggs.txt', '/spam/bacon', 0666, True),
                 ('/spam/bacon/eggs.txt', '/spam', 0666, True),
                 ('/spam/bacon/eggs.txt', None, None, False),
                 ('/spam/bacon/', '/spam/bacon', 0666, True),
                 ('/spam/bacon/', '/spam', 0666, True),
                 ('/spam/bacon/', None, None, False),
                 ('/spam/bacon', '/spam/bacon', 0666, True),
                 ('/spam/bacon', '/spam', 0666, True),
                 ('/spam/bacon', None, None, False),
                 ('/spam/bacon/eggs.txt', '/spam/bacon', 0444, False),
                 ('/spam/bacon/eggs.txt', '/spam', 0444, False),
                 ('/spam/bacon/', '/spam/bacon', 0444, False),
                 ('/spam/bacon/', '/spam', 0444, False),
                 ('/spam/bacon', '/spam/bacon', 0444, False),
                 ('/spam/bacon', '/spam', 0444, False)]
        
        def mock_function_generator(trigger_path, access_mode):
            def mock_function(filename, object_id):
                entry = {'filename': trigger_path,
                         '_id': testdata.GOOD_GRIDFS.object_id,
                         'contentType': 'collection',
                         'accessMode': access_mode,
                         'owner': 'brian'}
                if filename == trigger_path:
                    return entry
                else:
                    raise MataNuiStorerNotFoundException('foo')
            return mock_function
        
        a_gridfs = MongoGridFS()
        for filename, trigger_path, access_mode, expected in tests:
            a_gridfs._get_mongo_file_handle = Mock()
            a_gridfs._get_mongo_file_handle = mock_function_generator(trigger_path, access_mode)
            result = a_gridfs.is_access_allowed('loretta',
                                                storerinterface.PRIV_WRITE,
                                                filename=filename,
                                                dir_mode=True)
            self.assertEqual(result, expected)


    def test_entries_starting_with(self):
        '''testing the return of entries starting with a certain path'''
        tests = [(MockCursor([]),
                  []),
                 (MockCursor(['/spamelicious.txt',
                              '/spam/eggs.txt',
                              '/spam/bacon/eggs.txt']),
                  ['/spamelicious.txt',
                   '/spam/eggs.txt',
                   '/spam/bacon/eggs.txt']),
                 (MockCursor(['/spamelicious.txt',
                              '/spam/eggs.txt',
                              '/spam/eggs.txt',
                              '/spam/bacon/eggs.txt']),
                  ['/spamelicious.txt',
                   '/spam/eggs.txt',
                   '/spam/bacon/eggs.txt'])]
        
        for entries, expected in tests:
            gridfs_handle = Mock()
            gridfs_handle.find.return_value = entries
            a_gridfs = MongoGridFS()
            a_gridfs._files_collection = gridfs_handle
            result = a_gridfs._entries_starting_with('/spam')
            self.assertEquals(result, expected)
        
        
    def test_is_file_with_entry(self):
        '''testing whether something is a file with an entry in the DB'''
        tests = [('collection', False),
                 ('application/foodlike', True),
                 (None, True)]
        
        for content_type, expected in tests:
            gridfs_handle = Mock()
            entry = {'filename': '/spam',
                     '_id': testdata.GOOD_GRIDFS.object_id}
            if content_type:
                entry['contentType'] = content_type
            gridfs_handle.find.return_value = [entry]
            a_gridfs = MongoGridFS()
            a_gridfs._files_collection = gridfs_handle
            result = a_gridfs.is_file('/spam')
            self.assertEquals(result, expected)
        
        
    def test_is_file_without_entry(self):
        '''testing whether something is a file without an entry in the DB'''
        tests = [(True, False),
                 (False, True)]
        
        for exists, expected in tests:
            gridfs_handle = Mock()
            gridfs_handle.find.side_effect = MataNuiStorerNotFoundException('foo')
            a_gridfs = MongoGridFS()
            a_gridfs._files_collection = gridfs_handle
            a_gridfs.exists = Mock()
            a_gridfs.exists.return_value = exists
            result = a_gridfs.is_file('/spam')
            self.assertEquals(result, expected)

        
    def test_exists_with_entry(self):
        '''testing the return of entries starting with a certain path'''
        gridfs_handle = Mock()
        gridfs_handle.find.return_value = MockCursor(['/spam'])
        a_gridfs = MongoGridFS()
        a_gridfs._files_collection = gridfs_handle
        result = a_gridfs.exists('/spam')
        self.assert_(result)
        
        
    def test_exists_without_entry(self):
        '''testing resource existance without a DB entry for it'''
        tests = [('/spam', [], False),
                 ('/spam', ['/spamelicious.txt',
                            '/spam/eggs.txt',
                            '/spam/bacon/eggs.txt'], True),
                 ('/spam/', ['/spamelicious.txt',
                             '/spam/eggs.txt',
                             '/spam/bacon/eggs.txt'], True),
                 ('/spam', ['/spamelicious.txt',
                            '/spamstein.txt',
                            '/spamdau/eggs.txt'], False)]
        
        for path, entries, expected in tests:
            gridfs_handle = Mock()
            gridfs_handle.find.side_effect = MataNuiStorerNotFoundException('foo')
            a_gridfs = MongoGridFS()
            a_gridfs._files_collection = gridfs_handle
            a_gridfs._entries_starting_with = Mock()
            a_gridfs._entries_starting_with.return_value = entries
            result = a_gridfs.exists(path)
            self.assertEquals(result, expected)
        
        




class MockCursor(list):
    def __init__(self, a_list):
        list.__init__(self)
        for item in a_list:
            self.append({'filename': item,
                         '_id': testdata.GOOD_GRIDFS.object_id})
    
    def count(self):
        return len(self)



if __name__ == "__main__":
    unittest.main()