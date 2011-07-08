import json
import urllib

from hive.tests import *

from hive.tests.functional import constants

_ = urllib.quote

class TestGroupsController(TestController):

    def test_index(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.get(url('groups', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')

    # def test_index_as_xml(self):
    #     response = self.app.get(url('formatted_groups', format='xml'))

    def test_create(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('groups', repo_id='repo1'),
                                 params=json.dumps({'name':'@group1',
                                                    'member_list':['user1@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(_('/groups/@group1') in response.headers['location'])

    # def test_new(self):
    #     response = self.app.get(url('new_group'))

    # def test_new_as_xml(self):
    #     response = self.app.get(url('formatted_new_group', format='xml'))

    def test_update(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('groups', repo_id='repo1'),
                                 params=json.dumps({'name':'@group2',
                                                    'member_list':['user2@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/groups/@group2')))
        response = self.app.put(url('group', id='@group2', repo_id='repo1'),
                                params=json.dumps(['user2@test.com', 'user3@test.com']),
                                content_type='application/json')
        self.assertEqual(response.status, '200 OK')

    # def test_update_browser_fakeout(self):
    #     response = self.app.post(url('group', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('groups', repo_id='repo1'),
                                 params=json.dumps({'name':'@group3',
                                                    'member_list':['user2@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/groups/@group3')))
        response = self.app.delete(url('group', id='@group3', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')
        response = self.app.get(url('groups', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(_('/groups/@group3') not in json.loads(response.body))

    # def test_delete_browser_fakeout(self):
    #     response = self.app.post(url('group', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('groups', repo_id='repo1'),
                                 params=json.dumps({'name':'@group4',
                                                    'member_list':['user2@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/groups/@group4')))
        response = self.app.get(url('group', id='@group4', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')
        self.assertItemsEqual(json.loads(response.body),['user2@test.com'])

    # def test_show_as_xml(self):
    #     response = self.app.get(url('formatted_group', id=1, format='xml'))

    # def test_edit(self):
    #     response = self.app.get(url('edit_group', id=1))

    # def test_edit_as_xml(self):
    #     response = self.app.get(url('formatted_edit_group', id=1, format='xml'))
