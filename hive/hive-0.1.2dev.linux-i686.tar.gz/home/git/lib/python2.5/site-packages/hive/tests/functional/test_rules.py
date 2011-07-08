import json
import urllib

from hive.tests import *

from hive.tests.functional import constants

_ = urllib.quote

class TestRulesController(TestController):

    def test_index(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.get(url('rules', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')

    # def test_index_as_xml(self):
    #     response = self.app.get(url('formatted_rules', format='xml'))

    def test_create(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('rules', repo_id='repo1'),
                                 params=json.dumps({'permission':'RW',
                                                    'refex_list':['refex1', 'refex2'],
                                                    'member_list':['user1@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/rules/refex1,refex2;user1@test.com')))

    # def test_new(self):
    #     response = self.app.get(url('new_rule'))

    # def test_new_as_xml(self):
    #     response = self.app.get(url('formatted_new_rule', format='xml'))

    def test_update(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('rules', repo_id='repo1'),
                                 params=json.dumps({'permission':'RW',
                                                    'refex_list':['refex3'],
                                                    'member_list':['user2@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/rules/refex3;user2@test.com')))
        response = self.app.put(url('rule', id='refex3;user2@test.com', repo_id='repo1'),
                                 params=json.dumps({'permission':'RW+',
                                                    'refex_list':['refex3'],
                                                    'member_list':['user1@test.com', 'user2@test.com']}),
                                content_type='application/json')
        self.assertEqual(response.status, '200 OK')

    # def test_update_browser_fakeout(self):
    #     response = self.app.post(url('rule', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('rules', repo_id='repo1'),
                                 params=json.dumps({'permission':'RW',
                                                    'refex_list':['refex4'],
                                                    'member_list':['user2@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/rules/refex4;user2@test.com')))
        response = self.app.delete(url('rule', id='refex4;user2@test.com', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')
        response = self.app.get(url('rules', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(_('/rules/refex4;user2@test.com') not in json.loads(response.body))

    # def test_delete_browser_fakeout(self):
    #     response = self.app.post(url('rule', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
        response = self.app.post(url('rules', repo_id='repo1'),
                                 params=json.dumps({'permission':'-',
                                                    'refex_list':['refex5'],
                                                    'member_list':['user3@test.com']}),
                                 content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/rules/refex5;user3@test.com')))
        response = self.app.get(url('rule', id='refex5;user3@test.com', repo_id='repo1'))
        self.assertEqual(response.status, '200 OK')
        self.assertDictEqual(json.loads(response.body),
                             {'permission':'-',
                              'refex_list':['refex5'],
                              'member_list':['user3@test.com']})

    # def test_show_as_xml(self):
    #     response = self.app.get(url('formatted_rule', id=1, format='xml'))

    # def test_edit(self):
    #     response = self.app.get(url('edit_rule', id=1))

    # def test_edit_as_xml(self):
    #     response = self.app.get(url('formatted_edit_rule', id=1, format='xml'))
