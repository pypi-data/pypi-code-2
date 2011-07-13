import logging
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.templating import render_jinja2

from weborg.lib.base import BaseController
from weborg.lib import client

log = logging.getLogger(__name__)

class EntriesController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('entry', 'entries')

    def index(self, format='html'):
        """GET /entries: All items in the collection"""
        if format == 'json':
            return client.entry_index()
        if format == 'html':
            c.heading = 'index'
            c.items = [json.loads(client.entry_show(eid))
                       for eid in json.loads(client.entry_index())]
            print c.items
            return render_jinja2('entry-list.html')

    def create(self, id, format='html'):
        """POST /entries: Create a new item"""
        return client.entry_create(id, json.dumps(request.params))

    def new(self, format='html'):
        """GET /entries/new: Form to create a new item"""
        # url('new_entry')

    def update(self, id):
        """PUT /entries/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('entry', id=ID),
        #           method='put')
        # url('entry', id=ID)

    def delete(self, id):
        """DELETE /entries/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('entry', id=ID),
        #           method='delete')
        # url('entry', id=ID)

    def show(self, id, format='html'):
        """GET /entries/id: Show a specific item"""
        if format == 'json':
            return client.entry_show(id)
        if format == 'html':
            entry = json.loads(client.entry_show(id))
            c.back = url.current(id=entry['parent'])
            c.heading = entry['heading']
            if entry['children']:
                c.items = [json.loads(client.entry_show(child))
                           for child in entry['children']]
            return render_jinja2('entry-list.html')

    def edit(self, id, format='html'):
        """GET /entries/id/edit: Form to edit an existing item"""
        # url('edit_entry', id=ID)
