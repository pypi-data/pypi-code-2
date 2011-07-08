import json
import urllib

from hive.tests import *

from hive.tests.functional import constants

_ = urllib.quote

class TestReposController(TestController):

    def test_index(self):
        response = self.app.get(url('repos'))
        self.assertEqual(response.status, '200 OK')

    # def test_index_as_xml(self):
    #     response = self.app.get(url('formatted_repos', format='xml'))

    def test_create(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo1') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo1'}),
                                     content_type='application/json')
            self.assertEqual(response.status, '201 Created')
            self.assertTrue(response.headers['location'].endswith(_('/repos/repo1')))
        response = self.app.get(url('repos'))
        self.assertTrue(_('/repos/repo1') in json.loads(response.body))

    # def test_new(self):
    #     response = self.app.get(url('new_repo'))

    # def test_new_as_xml(self):
    #     response = self.app.get(url('formatted_new_repo', format='xml'))

    # def test_update(self):
    #     pass

    # def test_update_browser_fakeout(self):
    #     response = self.app.post(url('repo', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.get(url('repos'))
        if _('/repos/repo2') not in json.loads(response.body):
            response = self.app.post(url('repos'),
                                     params=json.dumps({'name':'repo2'}),
                                     content_type='application/json')
        self.assertEqual(response.status, '201 Created')
        self.assertTrue(response.headers['location'].endswith(_('/repos/repo2')))
        response = self.app.delete(url('repo', id='repo2'))
        self.assertEqual(response.status, '200 OK')
        response = self.app.get(url('repos'))
        self.assertEqual(response.status, '200 OK')
        self.assertTrue(_('/repos/repo2') not in json.loads(response.body))

    # def test_delete_browser_fakeout(self):
    #     response = self.app.post(url('repo', id=1), params=dict(_method='delete'))

    # def test_show(self):
    #     response = self.app.get(url('repos'))
    #     if _('/repos/repo1@test.com') not in json.loads(response.body):
    #         response = self.app.post(url('repos'),
    #                                  params=json.dumps({'name':'repo1@test.com','pubkey':constants.REPO1_PUBLIC_KEY}),
    #                                  content_type='application/json')
    #     response = self.app.get(url('repo', id='repo1@test.com'))
    #     self.assertEqual(response.status, '200 OK')
    #     self.assertDictEqual(json.loads(response.body), {'name':'repo1@test.com', 'pubkey':constants.REPO1_PUBLIC_KEY})

    # def test_show_as_xml(self):
    #     response = self.app.get(url('formatted_repo', id=1, format='xml'))

    # def test_edit(self):
    #     response = self.app.get(url('edit_repo', id=1))

    # def test_edit_as_xml(self):
    #     response = self.app.get(url('formatted_edit_repo', id=1, format='xml'))
