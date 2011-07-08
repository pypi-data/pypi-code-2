import logging
import json

from pylons import request, response, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from hive.lib.base import BaseController, render

from hive.lib.glam.api import User
from hive.lib.glam.api import HTTPBadRequest
from hive.lib.glam.api import HTTPNotFound
from hive.lib.glam.api import HTTPConflict
from hive.lib.glam.api import HTTPNotImplemented
from hive.lib.glam.api import HTTPInternalServerError

log = logging.getLogger(__name__)

class UsersController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('user', 'users')

    def index(self, format='html'):
        """GET /users: All items in the collection"""
        try:
            user_list = User.index()
        except HTTPInternalServerError:
            return abort(500)
        user_list = [url('user', id=user) for user in user_list]
        return json.dumps(user_list)

    def create(self):
        """POST /users: Create a new item"""
        body = request.environ['wsgi.input'].read()
        params = json.loads(body)
        try:
            user = User.create(params['name'], params['pubkey'])
        except (IndexError, HTTPBadRequest):
            abort(400)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)
        response.headers['Location'] = url('user', id=user)
        response.status_int = 201

    def new(self, format='html'):
        """GET /users/new: Form to create a new item"""
        abort(501)

    def update(self, id):
        """PUT /users/id: Update an existing item"""
        body = request.environ['wsgi.input'].read()
        log.debug(body)
        param = json.loads(body)
        log.debug(param)
        try:
            result = User.update(id, param)
        except (IndexError, HTTPBadRequest):
            abort(400)
        except HTTPNotFound:
            abort(404)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)

    def delete(self, id):
        """DELETE /users/id: Delete an existing item"""
        try:
            User.delete(id)
        except HTTPBadRequest:
            abort(400)
        except HTTPNotFound:
            abort(404)
        except HTTPConflict:
            abort(409)
        except HTTPInternalServerError:
            abort(500)
        response.status_int = 200

    def show(self, id, format='html'):
        """GET /users/id: Show a specific item"""
        try:
            user = User.show(id)
        except HTTPBadRequest:
            abort(400)
        except HTTPNotFound:
            abort(404)
        except HTTPConflict:
            abort(409)
        return json.dumps(user)

    def edit(self, id, format='html'):
        """GET /users/id/edit: Form to edit an existing item"""
        abort(501)
