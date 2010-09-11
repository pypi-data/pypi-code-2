# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Example WSDL described SOAP use.

Note: the ``no_zope_xmlrpc`` needs only be registered for Zope before 2.12.
It is then required to prevent Zope's xmlrpc support to interfere.
"""

# deactivate Zope's xmlrpc support
from zope.interface import alsoProvides
from dm.zopepatches.xmlrpc.publisher.interfaces import IXmlrpcChecker

def no_zope_xmlrpc(request): return False
alsoProvides(no_zope_xmlrpc, IXmlrpcChecker)
