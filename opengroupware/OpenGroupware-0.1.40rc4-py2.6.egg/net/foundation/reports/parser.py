# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import re, time
from itertools import izip
from xml.dom import minidom
from coils.core               import CoilsException
from namespaces               import XML_NAMESPACE, ALL_PROPS, REVERSE_XML_NAMESPACE
#from caldav_calendar_query    import caldav_calendar_query
#from caldav_calendar_multiget import caldav_calendar_multiget

"""
    ['name', 'parentname', 'href', 'ishidden', 'isreadonly',
     'getcontenttype', 'contentclass', 'getcontentlanguage',
     'creationdate', 'lastaccessed', 'getlastmodified',
     'getcontentlength', 'iscollection', 'isstructureddocument',
     'defaultdocument', 'displayname', 'isroot', 'resourcetype']

"""

class Parser(object):

    @staticmethod
    def get_depth(request):
        if 'Depth' in request.headers:
            return request.headers['Depth'].lower()
        else:
            return 'infinity'

    @staticmethod
    def _all_props():
        # TODO: Need namespace support
        return ALL_PROPS

    @staticmethod
    def domain_from_namespace(namespace):
        if (namespace is None):
            return 'unknown'
        return XML_NAMESPACE.get(namespace.lower(), 'unknown')

    @staticmethod
    def property_method_name(namespace, propname):
        return 'get_property_{0}_{1}'.format(Parser.domain_from_namespace(namespace),
                                              propname.lower().replace('-', '_'))

    @staticmethod
    def propfind(payload, user_agent=None):
        ''' Consumes a PROPFIND and returns a list of property sets. '''
        if (len(payload) == 0):
            return user_agent.default_properties()
        document = minidom.parseString(payload)
        return Parser.properties(document)

    @staticmethod
    def properties(document):
        ''' Return a list of the DAV:prop attributes from the provided document

            Each list entry is a set of
             - corresponding property member name for value retrieval
             - the original namespace of the property
             - the local name of the property
             - the domain of the propery (derived from namespace)
             - prefixed propertyname '''
        properties = [ ]
        namespaces = { 'http://apache.org/dav/props/':   'A',
                       'urn:ietf:params:xml:ns:caldav':  'C',
                       'DAV:':                           'D',
                       'urn:ietf:params:xml:ns:carddav': 'E',
                       'http://groupdav.org/':           'G',
                     }
        nm_ordinal = 74
        # TODO: if a request contains allprop, or propname, it must be solo!
        #        any combination of those to elements with each other or a
        #        prop element should raise an HTTP 400 Bad Request response
        if document.getElementsByTagNameNS("DAV:", "allprop"):
            properties = 'ALLPROP'
        elif document.getElementsByTagNameNS("DAV:", "propname"):
            properties = 'PROPNAME'
        else:
            for node in document.getElementsByTagNameNS("DAV:", "prop"):
                for element in node.childNodes:
                    if element.nodeType == minidom.Node.ELEMENT_NODE:
                        namespace = element.namespaceURI
                        if (namespace.upper() == 'DAV'):
                            prefix = 'D'
                        elif namespace in namespaces:
                            prefix = namespaces[namespace]
                        else:
                            prefix = chr(nm_ordinal)
                            namespaces[namespace] = prefix
                            nm_ordinal += 1
                        propname  = element.localName
                        properties.append((Parser.property_method_name(namespace, propname),
                                           namespace,
                                           propname,
                                           Parser.domain_from_namespace(namespace),
                                           '{0}:{1}'.format(prefix, propname)))
        keys = namespaces.iterkeys()
        values = namespaces.itervalues()
        return properties, dict(izip(values, keys))

    @staticmethod
    def report(payload):
        from caldav_calendar_query    import caldav_calendar_query
        from caldav_calendar_multiget import caldav_calendar_multiget
        document = minidom.parseString(payload)
        namespace = document.documentElement.namespaceURI
        if (namespace is None):
            domain = 'unknown'
        else:
            domain = XML_NAMESPACE.get(namespace.lower(), 'unknown')
        localname = document.documentElement.localName.lower().replace('-', '_')
        parserclassname = '{0}_{1}'.format(domain, localname)
        try:
            parserclass = eval(parserclassname)
            parser = parserclass(document)
        except Exception, e:
            #TODO: Add a logger here!
            #self.log.exception(e)
            #self.log.warn('No parser class for REPORT {0} {1}'.format(namespace, localname))
            #self.log.debug(payload)
            raise CoilsException('No parser available for specified report')
        else:
            return parser

