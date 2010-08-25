#!/usr/bin/env python
# encoding: utf-8
"""
workspace.py

Created by Keith Fahlgren on Sun Jan 18 06:51:25 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

from lxml import etree

from atompiglet import NAMESPACES
from atompiglet.collection import Collection

import friendly_curl

class Workspace:
    """A class that encapsulates the behavior of an AtomPub workspace."""
    def __init__(self, title, node, auth=None, server=None):
        self.title = title
        self._node = node
        self._auth = auth
        self._server = server
        self.collections = self._collect_collections()
        
    def collections_for_mimetype(self, mimetype):
        """Returns a list of collections that accept the given mimetype."""
        collections = []
        coll_nodes = self._node.xpath('app:collection', namespaces=NAMESPACES)
        for coll_node in coll_nodes:
            mimetypes = coll_node.xpath('app:accept/text()', namespaces=NAMESPACES)
            if mimetype in mimetypes:
                title = coll_node.xpath('atom:title/text()', namespaces=NAMESPACES)[0]
                collection = Collection(title, coll_node, auth=self._auth, server=self._server)
                collections.append(collection)
        return collections

    def _collect_collections(self):
        collections = {}
        coll_nodes = self._node.xpath('app:collection', namespaces=NAMESPACES)
        for coll_node in coll_nodes:
            title = coll_node.xpath('atom:title/text()', namespaces=NAMESPACES)[0]
            collections[title] = Collection(title, coll_node, auth=self._auth, server=self._server)
        return collections
