###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Scrapy s01.worker proxy

"""

import zope.component
from z3c.json import interfaces
from z3c.json.converter import JSONReader
from z3c.json.converter import JSONWriter
from z3c.json.proxy import JSONRPCProxy
from z3c.json.transport import BasicAuthTransport


def ensureJSONSupport():
    if zope.component.queryUtility(interfaces.IJSONReader) is None:
        zope.component.provideUtility(JSONReader(), interfaces.IJSONReader)
    if zope.component.queryUtility(interfaces.IJSONWriter) is None:
        zope.component.provideUtility(JSONWriter(), interfaces.IJSONWriter)


def getScrapyProxy(uri='http://localhost:6800', username='Manager',
    password='password', verbose=0, jsonId='scrapy', handleErrors=True):
    """Scrapy JSON-RPC 2.0 proxy"""
    # fist ensure that we can read and write json
    ensureJSONSupport()
    # setup JSONRPCProxy
    encoding = None
    jsonVersion = '2.0'
    
    transport = BasicAuthTransport(username, password)
    transport.handleErrors = handleErrors
    return JSONRPCProxy(uri, transport, encoding, verbose, jsonId, jsonVersion)
