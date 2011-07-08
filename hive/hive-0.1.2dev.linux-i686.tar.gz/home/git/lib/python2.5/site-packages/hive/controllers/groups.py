import logging
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from hive.lib.base import BaseController, render

from hive.lib.glam.api import Group
from hive.lib.glam.api import HTTPBadRequest
from hive.lib.glam.api import HTTPNotFound
from hive.lib.glam.api import HTTPConflict
from hive.lib.glam.api import HTTPNotImplemented
from hive.lib.glam.api import HTTPInternalServerError

log = logging.getLogger(__name__)

class GroupsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('group', 'groups')

    def index(self, repo_id, format='html'):
        """GET /groups: All items in the collection"""
        try:
            group_list = Group.index(repo_id)
        except HTTPInternalServerError:
            return abort(500)
        group_list = [url('group', id=group, repo_id=repo_id) for group in group_list]
        return json.dumps(group_list)

    def create(self, repo_id):
        """POST /groups: Create a new item"""
        params = json.loads(request.body)
        try:
            group = Group.create(repo_id, params['name'], params['member_list'])
        except (IndexError, HTTPBadRequest):
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)
        response.headers['Location'] = url('group', id=group, repo_id=repo_id)
        response.status_int = 201

    def new(self, format='html'):
        """GET /groups/new: Form to create a new item"""
        abort(501)

    def update(self, id, repo_id):
        """PUT /groups/id: Update an existing item"""
        params = json.loads(request.body)
        try:
            result = Group.update(repo_id, id, params)
        except (IndexError, HTTPBadRequest):
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)

    def delete(self, id, repo_id):
        """DELETE /groups/id: Delete an existing item"""
        try:
            Group.delete(repo_id, id)
        except HTTPBadRequest:
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)
        response.status_int = 200

    def show(self, id, repo_id, format='html'):
        """GET /groups/id: Show a specific item"""
        try:
            group = Group.show(repo_id, id)
        except HTTPBadRequest:
            abort(400)
        except HTTPConflict:
            abort(409)
        return json.dumps(group)

    def edit(self, id, repo_id, format='html'):
        """GET /groups/id/edit: Form to edit an existing item"""
        abort(501)
