# Copyright (c) 2010, Yaco Sistemas <lgs@yaco.es>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.

from repoze.what.plugins.hgwebdir.predicates import has_repo_access

MEDIA_FILES = ("static", "favicon.ico")


def _get_repo_from_path_info(path_info):
    parts = path_info.strip('/').split('/')
    if not parts:
        return None
    else:
        repo = parts[0]
        if repo and repo not in MEDIA_FILES:
            return repo


def protect_repositories(app, public_repos):

    def protected_app(environ, start_response):
        repo = _get_repo_from_path_info(environ['PATH_INFO'])
        if not repo or has_repo_access(repo, public_repos).is_met(environ):
            return app(environ, start_response)
        else:
            start_response('401 not authorized', [])
            return []

    return protected_app
