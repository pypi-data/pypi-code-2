import json
import urllib

from hive.tests import *

from hive.tests.functional import constants

_ = urllib.quote

class TestUsersController(TestController):

    def test_index(self):
        response = self.app.get(url('users'))
        self.assertEqual(response.status, '200 OK')

    # def test_index_as_xml(self):
    #     response = self.app.get(url('formatted_users', format='xml'))

    def test_create(self):
        response = self.app.post(url('users'),
                                 params=json.dumps({'name':'user1@test.com','pubkey':constants.USER1_PUBLIC_KEY}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/users/user1@test.com')))

    # def test_new(self):
    #     response = self.app.get(url('new_user'))

    # def test_new_as_xml(self):
    #     response = self.app.get(url('formatted_new_user', format='xml'))

    def test_update(self):
        response = self.app.post(url('users'),
                                 params=json.dumps({'name':'user2@test.com',
                                                    'pubkey':constants.USER2_PUBLIC_KEY}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/users/user2@test.com')))
        response = self.app.put(url('user', id='user2@test.com'),
                                json.dumps(constants.TMP_PUBLIC_KEY),
                                content_type='application/json')
        self.assertEqual(response.status, '200 OK')

    # def test_update_browser_fakeout(self):
    #     response = self.app.post(url('user', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.post(url('users'),
                                 params=json.dumps({'name':'user3@test.com','pubkey':constants.USER3_PUBLIC_KEY}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/users/user3@test.com')))
        response = self.app.delete(url('user', id='user3@test.com'))
        self.assertEqual(response.status, '200 OK')
        response = self.app.get(url('users'))
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(_('/users/user3@test.com') not in json.loads(response.body))

    # def test_delete_browser_fakeout(self):
    #     response = self.app.post(url('user', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('users'))
        if _('/users/user1@test.com') not in json.loads(response.body):
            response = self.app.post(url('users'),
                                     params=json.dumps({'name':'user1@test.com','pubkey':constants.USER1_PUBLIC_KEY}),
                                     content_type='application/json')
        response = self.app.get(url('user', id='user1@test.com'))
        self.assertEqual(response.status, '200 OK')
        self.assertDictEqual(json.loads(response.body), {'name':'user1@test.com', 'pubkey':constants.USER1_PUBLIC_KEY})

    # def test_show_as_xml(self):
    #     response = self.app.get(url('formatted_user', id=1, format='xml'))

    # def test_edit(self):
    #     response = self.app.get(url('edit_user', id=1))

    # def test_edit_as_xml(self):
    #     response = self.app.get(url('formatted_edit_user', id=1, format='xml'))
