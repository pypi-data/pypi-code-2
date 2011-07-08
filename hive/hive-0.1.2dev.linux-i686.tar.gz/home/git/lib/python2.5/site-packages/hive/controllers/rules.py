import logging
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from hive.lib.base import BaseController, render

from hive.lib.glam.api import Rule
from hive.lib.glam.api import HTTPBadRequest
from hive.lib.glam.api import HTTPNotFound
from hive.lib.glam.api import HTTPConflict
from hive.lib.glam.api import HTTPNotImplemented
from hive.lib.glam.api import HTTPInternalServerError

log = logging.getLogger(__name__)

class RulesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('rule', 'rules')

    def index(self, repo_id, format='html'):
        """GET /rules: All items in the collection"""
        try:
            rule_list = Rule.index(repo_id)
        except HTTPInternalServerError:
            return abort(500)
        rule_list = [url('rule', id=rule, repo_id=repo_id)
                     for rule in rule_list]
        return json.dumps(rule_list)

    def create(self, repo_id):
        """POST /rules: Create a new item"""
        params = json.loads(request.body)
        try:
            rule = Rule.create(repo_id, params['permission'],
                               params['refex_list'], params['member_list'])
        except (IndexError, HTTPBadRequest):
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)
        response.headers['Location'] = url('rule', id=rule, repo_id=repo_id)
        response.status_int = 201

    def new(self, repo_id, format='html'):
        """GET /rules/new: Form to create a new item"""
        abort(501)

    def update(self, id, repo_id):
        """PUT /rules/id: Update an existing item"""
        params = json.loads(request.body)
        try:
            result = Rule.update(repo_id, id, params['member_list'])
        except (IndexError, HTTPBadRequest):
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)

    def delete(self, id, repo_id):
        """DELETE /rules/id: Delete an existing item"""
        try:
            Rule.delete(repo_id, id)
        except HTTPBadRequest:
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)
        response.status_int = 200

    def show(self, id, repo_id, format='html'):
        """GET /rules/id: Show a specific item"""
        try:
            rule = Rule.show(repo_id, id)
        except HTTPBadRequest:
            abort(400)
        except HTTPNotFound:
            abort(404)
        except HTTPConflict:
            abort(409)
        return json.dumps(rule)

    def edit(self, id, repo_id, format='html'):
        """GET /rules/id/edit: Form to edit an existing item"""
        abort(501)
