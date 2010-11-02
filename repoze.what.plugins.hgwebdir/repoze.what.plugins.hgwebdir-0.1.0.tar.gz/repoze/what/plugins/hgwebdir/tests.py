# Copyright (c) 2010, Yaco Sistemas <lgs@yaco.es>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.

import os
import tempfile
import unittest

from repoze.what.adapters.testutil import ReadOnlyGroupsAdapterTester
from repoze.what.adapters.testutil import ReadOnlyPermissionsAdapterTester

from repoze.what.plugins.hgwebdir.adapters import HgwebdirGroupsAdapter
from repoze.what.plugins.hgwebdir.adapters import HgwebdirPermissionsAdapter
from repoze.what.plugins.hgwebdir.adapters import get_public_repositories
from repoze.what.plugins.hgwebdir.middleware import _get_repo_from_path_info
from repoze.what.plugins.hgwebdir.middleware import protect_repositories
from repoze.what.plugins.hgwebdir.predicates import is_read_access
from repoze.what.plugins.hgwebdir.predicates import has_repo_access


sample_authz = """
[groups]
rolling = mick, keith, ronnie, charlie
beatles = john, paul, george, ringo

[sticky-fingers]
@rolling = rw
@beatles = r

[sargent-peppers]
@beatles = rw
@rolling = r

[pet-sounds]
* = r

[white-album]
@beatles = rw

[imagine]
john = rw
* = r
"""


class CommonTester(unittest.TestCase):

    def setUp(self):
        super(CommonTester, self).setUp()
        self.authz_file = tempfile.mkstemp('repoze_what_plugins_hgwebdir')[1]
        self.write(sample_authz)

    def tearDown(self):
        super(CommonTester, self).tearDown()
        os.remove(self.authz_file)

    def write(self, data):
        fd = open(self.authz_file, 'w')
        fd.write(data)
        fd.close()


class HgwebdirGroupsTester(CommonTester, ReadOnlyGroupsAdapterTester):

    def setUp(self):
        super(HgwebdirGroupsTester, self).setUp()

        self.adapter = HgwebdirGroupsAdapter(self.authz_file)

        self.all_sections = {
            u'rolling': set((u'mick', u'keith', u'ronnie', u'charlie')),
            u'beatles': set((u'john', u'paul', u'george', u'ringo')),
            u'john': set((u'john', )),
            }


class HgwebdirPermissionsTester(CommonTester, ReadOnlyPermissionsAdapterTester):

    def setUp(self):
        super(HgwebdirPermissionsTester, self).setUp()

        self.adapter = HgwebdirPermissionsAdapter(self.authz_file)

        self.all_sections = {
            u'sticky-fingers-read': set((u'rolling', u'beatles')),
            u'sticky-fingers-write': set((u'rolling', )),
            u'sargent-peppers-read': set((u'rolling', u'beatles')),
            u'sargent-peppers-write': set((u'beatles', )),
            u'pet-sounds-read': set(),
            u'pet-sounds-write': set(),
            u'white-album-read': set((u'beatles', )),
            u'white-album-write': set((u'beatles', )),
            u'imagine-read': set((u'john', )),
            u'imagine-write': set((u'john', )),
            }


class PublicRepositoriesTester(CommonTester):

    def test_get_public_repositories(self):
        self.assertEquals(get_public_repositories(self.authz_file),
                          [u'pet-sounds', u'imagine'])


class PredicatesTester(unittest.TestCase):

    def test_read_access(self):
        assert is_read_access().is_met({'REQUEST_METHOD': 'GET'}), \
            "A GET should be read access"
        assert not is_read_access().is_met({'REQUEST_METHOD': 'POST'}), \
            "A POST should not be read access"
        assert not is_read_access().is_met({'REQUEST_METHOD': 'PUT'}), \
            "A PUT should not be read access"
        assert not is_read_access().is_met({'REQUEST_METHOD': 'DELETE'}), \
            "A DELETE should not be read access"

    def test_repo_access(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'repoze.what.credentials': {
                'repoze.what.userid': 'john',
                'groups': tuple(),
                'permissions': (u'repo1-read', u'repo1-write', u'repo2-read'),
                },
            }
        assert has_repo_access('repo1', []).is_met(environ)
        assert has_repo_access('repo2', []).is_met(environ)
        assert not has_repo_access('repo3', []).is_met(environ)

        environ['REQUEST_METHOD'] = 'POST'
        assert has_repo_access('repo1', []).is_met(environ)
        assert not has_repo_access('repo2', []).is_met(environ)
        assert not has_repo_access('repo3', []).is_met(environ)

        # test public repositories
        environ['REQUEST_METHOD'] = 'GET'
        assert has_repo_access('repo4', ['repo4']).is_met(environ)


class MiddlewareTester(unittest.TestCase):

    def test_get_repo_from_path_info(self):
        self.assertEquals(_get_repo_from_path_info(''), None)
        self.assertEquals(_get_repo_from_path_info('/'), None)
        self.assertEquals(_get_repo_from_path_info('/repo1'), 'repo1')
        self.assertEquals(_get_repo_from_path_info('/repo1/'), 'repo1')
        self.assertEquals(_get_repo_from_path_info('/repo1/foo'), 'repo1')
        self.assertEquals(_get_repo_from_path_info('/repo1/foo/'), 'repo1')

        # media files are not repositories
        self.assertEquals(_get_repo_from_path_info('/favicon.ico'), None)
        self.assertEquals(_get_repo_from_path_info('/static'), None)
        self.assertEquals(_get_repo_from_path_info('/static/icon.png'), None)
        self.assertEquals(_get_repo_from_path_info('/static/styles.css'), None)

    def test_protect_repositories(self):

        content_type_header = ('Content-type', 'text/plain')

        def hello_world(environ, start_response):
            start_response('200 OK', [content_type_header])
            return ['Hello world\n']

        protected_app = protect_repositories(hello_world, [])

        log = []

        def start_response(status, headers):
            log.append((status, headers))

        env = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            }
        response = protected_app(env, start_response)
        self.assertEquals(response, ['Hello world\n'])
        self.assertEquals(log[-1], ('200 OK', [content_type_header]))

        env = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/repo1',
            }
        response = protected_app(env, start_response)
        self.assertEquals(response, [])
        self.assertEquals(log[-1], ('401 not authorized', []))

        env = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/repo1',
            'repoze.what.credentials': {
                'repoze.what.userid': 'john',
                'groups': tuple(),
                'permissions': (u'repo1-read', u'repo1-write'),
                },
            }
        response = protected_app(env, start_response)
        self.assertEquals(response, ['Hello world\n'])
        self.assertEquals(log[-1], ('200 OK', [content_type_header]))

        env = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/repo1',
            'repoze.what.credentials': {
                'repoze.what.userid': 'john',
                'groups': tuple(),
                'permissions': (u'repo1-read', u'repo1-write'),
                },
            }
        response = protected_app(env, start_response)
        self.assertEquals(response, ['Hello world\n'])
        self.assertEquals(log[-1], ('200 OK', [content_type_header]))

        env = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/repo2',
            'repoze.what.credentials': {
                'repoze.what.userid': 'john',
                'groups': tuple(),
                'permissions': (u'repo1-read', u'repo1-write'),
                },
            }
        response = protected_app(env, start_response)
        self.assertEquals(response, [])
        self.assertEquals(log[-1], ('401 not authorized', []))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HgwebdirGroupsTester),
        unittest.makeSuite(HgwebdirPermissionsTester),
        unittest.makeSuite(PredicatesTester),
        unittest.makeSuite(MiddlewareTester),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
