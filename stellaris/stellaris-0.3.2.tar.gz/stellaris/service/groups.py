# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, simplejson

from stellaris.store.exceptions import GroupNotFound, GroupAlreadyExists, Unauthorized
from stellaris.service.security import authorize
from stellaris.security import AUTHENTICATED_USER, PUBLIC_USER, READ, READ_WRITE, ADMIN_READ_WRITE

from uuid import uuid4 as uuid

from benri.app import WSGICollection
from benri.app.json import JSON_CONTENT_TYPE, json
from urlparse import urlunparse, urljoin
from mimetypes import types_map as mimetype
from cStringIO import StringIO

from paste.fileapp import _FileIter
from paste.httpexceptions import HTTPMultipleChoices, HTTPSeeOther, HTTPNotFound, HTTPBadRequest, HTTPConflict, HTTPInternalServerError, HTTPMethodNotAllowed, HTTPUnauthorized
from paste.request import parse_querystring

log = logging.getLogger(__name__)

class Groups(WSGICollection):
    """
    A collection of groups.
    """
    def __init__(self, store, prefix='/system/groups/'):
        self.store = store
        if not prefix.endswith('/'):
            prefix += '/'

        self.__prefix = prefix
        WSGICollection.__init__(self, uri_prefix=prefix)

    def _group_id(self, env):
        if env['REQUEST_METHOD'] == 'POST':
        # POST is for when a new graph is created
        
        # the slug contains the value recommended by the client to
        # create the URI where the file will be accessible via
            try:
                group_id = env['HTTP_SLUG']
            except KeyError, e:
                raise HTTPBadRequest('A group create request must contain an HTTP_SLUG environment-variable that indicates the name of the group')
        else:
            (_, args) = env['wsgiorg.routing_args']        
            group_id = self._check_arg('id', args)
            
        return group_id

    # GET /graphs/
    # this is the same as retrieve
    @json
    def list(self, env, resp):
        try:
            groups = self.store.group_list()
        except Exception, e:
            log.debug(str(e))
            raise HTTPInternalServerError(str(e))
                    
        resp('200 OK', [])
        return [groups]

    # POST /groups/
    
    # Creates a new group in the collection
    # Uses the 'Slug'-header for the name of the group
    
    @authorize(access_type=ADMIN_READ_WRITE)
    @json
    def create(self, env, resp):
        group_id = self._group_id(env)
        content_size = self._check_content_size(env)
        #format = self._check_format(self._check_content_type(env))

        req = env['benri.json']
        try:
            self.store.group_create(group_id, users=req['users'])
        except GroupAlreadyExists, e:
            raise HTTPConflict("Group: %s, already exists." % (str(e)))
        except Exception, e:
            raise HTTPInternalServerError(str(e))
        
        # remove leading slash from group_id to get correct behaviour for 
        # urljoin
        location = urljoin(urlunparse((env['wsgi.url_scheme'], env['HTTP_HOST'], self.__prefix, '','','')), group_id)
        
        headers = [('Location', location)]
        resp('201 Created', headers)
        return []
        
    # GET /groups/{id:any}
    # Return the list of users in the given group.        
    @authorize(access_type=ADMIN_READ_WRITE)
    @json
    def retrieve(self, env, resp):
    
        group_id = self._group_id(env)
        
#        content_type = self._check_accept(env)

        try:
            users = self.store.group_retrieve(group_id)
            resp('200 OK', [])
            return [{'users': users}]
        except GroupNotFound, e:
            raise HTTPNotFound('Group: %s, not found' % str(group_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e) + str(type(e)))

    # PUT /groups/{id:any}
    # Replaces the current user list with the given list
    @authorize(access_type=ADMIN_READ_WRITE)
    @json
    def update(self, env, resp):
        group_id = self._group_id(env)

        req = env['benri.json']
        
        try:
            self.store.group_update(group_id, users=req['users'])
        except GroupNotFound, e:
            raise HTTPNotFound('Group: %s, not found' % str(group_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e))        

        resp('200 OK', [])
        return []
        
    # DELETE /graphs/{id:any}
    # deletes the group from the system
    @authorize(access_type=ADMIN_READ_WRITE)    
    def delete(self, env, resp):
        group_id = self._group_id(env)

        try:
            self.store.group_delete(group_id)
        except GroupNotFound, e:
            raise HTTPNotFound('Group: %s, not found' % str(group_id))
        except Exception, e:
            raise HTTPInternalServerError(str(e))        

        resp('200 OK', [])
        return []
