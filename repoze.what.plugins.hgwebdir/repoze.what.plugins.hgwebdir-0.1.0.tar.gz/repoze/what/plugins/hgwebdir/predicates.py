# Copyright (c) 2010, Yaco Sistemas <lgs@yaco.es>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.

from repoze.what.predicates import All, Any, Not, Predicate
from repoze.what.predicates import has_permission


class is_read_access(Predicate):
    message = 'The method %(method)s does not use read access'

    def evaluate(self, environ, credentials):
        method = environ['REQUEST_METHOD']
        if method != 'GET':
            self.unmet(method=method)


class has_repo_access(Any):
    message = 'The user must have access to the repository %(repo_name)s'

    def __init__(self, repo_name, public_repos, **kwargs):
        self.repo_name = repo_name
        predicates = [
            All(is_read_access(), has_permission(repo_name + '-read')),
            All(Not(is_read_access()), has_permission(repo_name + '-write')),
            ]
        if repo_name in public_repos:
            predicates.append(is_read_access())

        super(has_repo_access, self).__init__(*predicates, **kwargs)

    def evaluate(self, environ, credentials):
        super(has_repo_access, self).evaluate(environ, credentials)
