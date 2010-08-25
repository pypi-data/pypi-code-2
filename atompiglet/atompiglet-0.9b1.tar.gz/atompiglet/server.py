#!/usr/bin/env python
# encoding: utf-8
"""
server.py

Created by Keith Fahlgren on Sat Jan 17 14:49:12 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

from lxml import etree
from cStringIO import StringIO

# ORM
import friendly_curl

from atompiglet import NAMESPACES, get_absolute_url
from atompiglet.workspace import Workspace
from atompiglet.errors import ServerError

class Server:
    """A class that encapsulates interaction between a client and
    AtomPub server."""

    def __init__(self, endpoint_url, auth=None):
        self.endpoint_url = endpoint_url
        self._accept_self_signed_SSL = True
        self._auth = auth
        self.workspaces = self._collect_workspaces()

    def service_doc(self):
        """Return the app:service document from the server's endpoint root."""
        headers = self._auth.headers() if self._auth else None
        try:
            resp, body = friendly_curl.threadCURLSingleton().get_url(
                self.endpoint_url, headers=headers)
        except friendly_curl.friendly_curl.PyCURLError, e:
            raise ServerError("Service document could not be retreived from server at %s (%s)!" % (self.endpoint_url, e))
        if resp['status'] != 200:
            raise ServerError("Service document could not be retreived from server at %s (%s)!" % (self.endpoint_url, resp['status']))

        try:
            app_service = etree.parse(body, base_url=self.endpoint_url)
        except etree.XMLSyntaxError, e:
            raise ServerError("Service document could not parsed from server at %s (%s)!" % (self.endpoint_url, e))
        return app_service

    def _collect_workspaces(self):
        workspaces = {}
        wksp_nodes = self.service_doc().xpath('/app:service/app:workspace', namespaces=NAMESPACES)
        for wksp_node in wksp_nodes:
            title = wksp_node.xpath('atom:title/text()', namespaces=NAMESPACES)[0]
            workspaces[title] = Workspace(title, wksp_node, auth=self._auth, server=self)
        return workspaces

