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
import xmldict, urllib
from StringIO            import StringIO
from coils.core          import *
from coils.net           import *
from bufferedwriter      import BufferedWriter
from reports             import Parser, REVERSE_XML_NAMESPACE
from xml.sax.saxutils    import escape
from useragent           import UserAgent

PATH_CACHE = { }
USE_CACHE = False

PROP_METHOD    = 0
PROP_NAMESPACE = 1
PROP_LOCALNAME = 2
PROP_DOMAIN    = 3

class DAV(PathObject):
    def __init__(self, parent, name, **params):
        ''' Root DAV Object;  provides utility methods for implementing WebDAV.

        Keyword Arguments:
        parent - The parent object in the DAV hierarchy, should be a DAV object
        name - The name of this object, as used in the URL

        Additional named parameters are used to directly set attributes of this
        object,  so you you set fred=123 an attribute of fred will be set on the
        object with a value of 123.
        '''
        self.name = name
        self._contents = None
        self._aliases  = None
        self._depth    = -1
        PathObject.__init__(self, parent, **params)

    #
    # Core
    #

    @property
    def is_folder(self):
        return False

    @property
    def is_object(self):
        return False

    @property
    def user_agent(self):
        return UserAgent(self.request.headers.get('USER-AGENT', None))

    def get_path(self):
        ''' Reconstruct the path used to arrive at this object'''
        path = self.name
        x = self.parent
        while (x is not None):
            path = '%s/%s' % (x.get_name(), path)
            x = x.parent
        return path

    def get_parent_path(self):
        return self.parent.get_path()

    @property
    def url(self):
        return self.get_path()

    @property
    def webdav_url(self):
        return self.url

    #
    # Contents
    #
    def insert_child(self, key, value, alias=None):
        key = unicode(key)
        if (self._contents is None): self._contents = { }
        if (self._aliases is None): self._aliases = { }
        self._contents[unicode(key)] = value
        if (alias is not None):
            self._aliases[unicode(alias)] = key

    def empty_content(self):
        if (self._contents is None): self._contents = { }
        if (self._aliases is None): self._aliases = { }

    def get_alias_for_key(self, key):
        if (self._aliases is None):
            return key
        name = self._aliases.get(unicode(key), key)
        return name

    def get_child(self, key, minimum_components = 1,
                             component_seperator='.',
                             supports_aliases=True):
        result = None
        # We always process keys as strings
        key = str(key)
        if (self._aliases is None): self.log.error('Aliases is not initialized')
        if (self._contents is None): self.log.error('Contents is not initialized')
        if (supports_aliases):
            # If aliases are enabled and the key matches then the key is replaced by the
            # value from the _aliases dict
            if (key in self._aliases):
                key = self._aliases[key]
        key = key.split(component_seperator)
        for i in range(len(key), 0 , -1):
            if (i < minimum_components): break
            result = self._contents.get(u'.'.join(key[0:i]), None)
            if (result is not None):
                break;
        return result

    def has_child(self, key, minimum_components = 1,
                             component_seperator='.',
                             supports_aliases=True):
        if (self.get_child(key, minimum_components=minimum_components,
                                component_seperator=component_seperator,
                                supports_aliases=supports_aliases) is None):
            return False
        return True

    def get_children(self):
        return self._contents.values()

    @property
    def is_loaded(self):
        if (self._contents is None):
            return False
        return True

    def load_contents(self):
        ''' If the DAV objects does not contain any data (self.data is None) then
            an attempt is made to retrieve the relevent information.  This method
            calls the _load_self() which the child is expected to implement. '''
        if (self.is_loaded):
            return True
        if (self._load_contents()):
            if (self._contents is None): self._contents = {}
            if (self._aliases is None): self._aliases = {}
            return True
        return False

    def _load_contents(self):
        # NOTE: All children must implement this method
        return True

    def get_keys(self):
        if (self.load_contents()):
            return self._contents.keys()
        return []

    #
    # Properties
    #

    @property
    def properties(self):
        # WARN: This does *not* work correctly.  It only returns the properties that
        # the object implements, it does not return the properties whose implementation
        # the object inherits
        properties = []
        methods = [ method for method in dir(self) if method.startswith('get_property_')]
        for method in methods:
            parts = method.split('_', 3)
            if (len(parts) == 4):
                # Filter out unknown namespace properties
                if (parts[2] != 'unknown'):
                    namespace = REVERSE_XML_NAMESPACE.get(parts[2], 'DAV')
                    properties.append( ( method,
                                         namespace,
                                         parts[3].replace('_', '-'),
                                         parts[2] ) )
        return properties

    def get_ctag(self):
        ''' Return a ctag appropriate for this object.
            Actual WebDAV objects should override this method '''
        # Child should override, it knows how to compute or derive its ctag.
        return '0'

    # PROP: EXECUTABLE

    def get_property_unknown_executable(self):
        return self.get_property_webdav_executable()

    def get_property_webdav_executable(self):
        return '0'

    # PROP: CREATIONDATE

    def get_property_unknown_creationdate(self):
        return self.get_property_webdav_creationdate()

    def get_property_webdav_creationdate(self):
        if (hasattr(self, 'entity')):
            if ((self.load_contents()) and hasattr(self.entity, 'created')):
                if (self.entity.created is not None):
                    return self.entity.created.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return 'Thu, 09 Sep 2010 10:17:06 GMT'

    # PROP: GETLASTMODIFIED

    def get_property_unknown_getlastmodified(self):
        return self.get_property_webdav_getlastmodified()

    def get_property_webdav_getlastmodified(self):
        if (hasattr(self, 'entity')):
            #self.log.debug('DAV presentation object has entity attribute')
            if ((self.load_contents()) and hasattr(self.entity, 'modified')):
                if (self.entity.modified is not None):
                    #self.log.debug('DAV presentation object has modified time')
                    return self.entity.modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        #self.log.debug('DAV presentation object {0} returning default modified timestamp')
        return 'Thu, 09 Sep 2010 10:17:06 GMT'

    #
    # Options
    #

    def supports_GET(self):
        return False

    def supports_POST(self):
        return False

    def supports_PUT(self):
        return False

    def supports_DELETE(self):
        return False

    def supports_PROPFIND(self):
        return True

    def supports_PROPATCH(self):
        return False

    def supports_MKCOL(self):
        return False

    def supports_MOVE(self):
        return False

    def supports_UNLOCK(self):
        return False

    def supports_LOCK(self):
        return False

    def supports_REPORT(self):
        return False

    def supports_ACL(self):
        return False

    def get_methods(self):
        return ['GET', 'POST', 'PUT', 'DELETE', 'PROPFIND', 'PROPPATCH', 'MKCOL',
                 'MOVE', 'UNLOCK', 'LOCK', 'REPORT', 'ACL']

    def supports_operation(self, operation):
        operation = operation.upper().strip()
        method = 'supports_{0}'.format(operation)
        if (hasattr(self, method)):
            return getattr(self, method)()
        return False

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'HEAD', 'OPTIONS' ]
        for method in self.get_methods():
            if (self.supports_operation(method)):
                methods.append(method)
        self.request.simple_response(200,
                                     data=None,
                                     headers={ 'DAV': '1',
                                               'Allow': ','.join(methods),
                                               'Connection': 'close',
                                               'MS-Author-Via': 'DAV'})

    #
    # PROPFIND support
    #

    def parse_propfind_for_property_names(self, payload):
        return Parser.propfind(payload)

    def do_PROPFIND(self):
        ''' Respond to a PROPFIND request.

            RFC2518 Section 8.1

            The depth property of the request determines if this is an
            examination of the collection object (depth 0) or an
            examination of the collections contents (depth 1). If no
            depth is specified a depth of inifinity must be assumed
            [according to the spec; yes, that is stupid, but that is
            the spec].'''

        depth = Parser.get_depth(self.request)
        if (depth == '1'):
            depth = 2
        elif (depth == '0'):
            depth = 1
        else:
            # HACK: infinity = 25
            depth = 25

        payload = self.request.get_request_payload()
        props = self.parse_propfind_for_property_names(payload)
        # Create buffer for response
        #w = BufferedWriter(self.request.wfile, False)
        w = StringIO('')
        # Debugging
        # TODO: Allow request / response logging to be enabled via a default
        #self.log.debug('PROPFIND REQUEST: %s' % payload)
        #self.log.debug('PROPERTIES: %s' % props)
        #Header

        if (isinstance(props, basestring)):
            if (props  == 'ALLPROP'):
                self.do_property_propfind(props=None, depth=depth, wfile=w)
            elif (props == 'PROPNAME'):
                self.do_propname_propfind(depth=depth, wfile=w)
            else:
                raise CoilsException('Unimplemented special case from PROPFIND parser')
        elif (isinstance(props, list)):
            # Send PROPFIND response header
            self.do_property_propfind(props=props, depth=depth, wfile=w)
        else:
            raise CoilsException('Unrecognzed response from PROPFIND parser')

        headers={'X-Dav-Error': '200 No error',
                 'Ms-Author-Via': 'DAV' }
        if (hasattr(self, 'location')):
            if (self.user_agent.supports_301):
                headers['Location'] = self.location
        self.request.simple_response(207,
                                     data=w.getvalue(),
                                     mimetype='text/xml; charset="utf-8"',
                                     headers=headers)


    def do_propname_propfind(self, depth=25, wfile=None):
        # Status: Implemented
        wfile.write(u'<?xml version="1.0" encoding="utf-8" ?>')
        wfile.write(u'<multistatus xmlns="DAV:">\n')
        self.do_propname_response(depth=depth, wfile=wfile)
        wfile.write(u'</multistatus>\n')

    def do_propname_response(self, depth=25, wfile=None):
        # Generate a propname response for "target" object, this method will
        # recurse until depth reaches -1
        abbreviations = {}
        properties = []
        for prop in self.properties:
            namespace = prop[PROP_NAMESPACE]
            propname = prop[PROP_LOCALNAME]
            if namespace in abbreviations:
                abbrevation = abbreviations.get(namespace)
            else:
                abbreviation = 97 + len(abbreviations)
                abbreviations[namespace] = u'{0}'.format(chr(abbreviation))
            properties.append((u'{0}'.format(chr(abbreviation)), propname))
        z = StringIO()
        z.write(u'  <response>\n')
        z.write(u'    <href>{0}</href>\n'.format(escape(self.webdav_url)))
        z.write(u'    <prop')
        for namespace in abbreviations:
            z.write(u' xmlns:{0}="{1}"'.format(abbreviations[namespace], namespace))
        z.write(u'>\n')
        for prop in properties:
            z.write(u'      <{0}:{1}/>\n'.format(prop[0], prop[1]))
        z.write(u'    </prop>\n')
        z.write(u'    <status>HTTP/1.1 200 OK</status>\n')
        z.write(u'  </response>\n')
        result = z.getvalue()
        z.close()
        wfile.write(result)
        depth += -1
        if ((depth > 0) and (self.is_folder)):
            self.load_contents()
            for key in self.get_keys():
                result = self.get_object_for_key(key, auto_load_enabled=True, is_webdav=True)
                result.do_propname_response(depth=depth, wfile=wfile)

    def do_property_propfind(self, props=[], depth=25, wfile=None):
        # Status: TODO
        wfile.write(u'<?xml version="1.0" encoding="utf-8"?>')
        wfile.write(u'<multistatus xmlns="DAV:">\n')
        self.do_property_response(props=props, depth=depth, wfile=wfile)
        wfile.write(u'</multistatus>\n')

    def do_property_response(self, props=[], depth=25, wfile=None):
        #
        # TODO: What is the correct thing to do for a moved resource?
        #        Reply with the href requested or reply with the
        #        resources "real" location?
        #
        # TODO: Handle namespaces in a more intelligent way [2010-08-17, ATW]
        #
        allprops = False
        known = {}
        unknown = []
        wfile.write(u'  <response>\n')
        wfile.write(u'    <href>{0}</href>\n'.format(urllib.quote(self.webdav_url)))
        if ((props is None) or (len(props) == 0)):
            allprops = True
            props = self.properties
        for i in range(len(props)):
            prop = props[i]
            if (hasattr(self, prop[PROP_METHOD])):
                x = getattr(self, prop[PROP_METHOD])
                known[prop] = x()
                x = None
            else:
                unknown.append(prop)
        # render found properties
        if (len(known) > 0):
            wfile.write(u'    <propstat>\n')
            wfile.write(u'      <status>HTTP/1.1 200 OK</status>\n')
            wfile.write(u'      <prop>\n')
            for prop in known.keys():
                if (known[prop] is None):
                    # PROPERTY VALUE NONE
                    if (prop[PROP_DOMAIN] == u'webdav'):
                        wfile.write(u'        <%s/>\n' % prop[PROP_LOCALNAME])
                    elif (prop[PROP_NAMESPACE] is None):
                        wfile.write(u'        <{0}/>\n'.format(prop[PROP_LOCALNAME]))
                    else:
                        wfile.write(u'        <{0} xmlns="{1}"/>\n'.format(prop[PROP_LOCALNAME],
                                                             prop[PROP_NAMESPACE]))
                else:
                   # PROPERTY HAS VALUE
                   value = unicode(known[prop])
                   if (value[0:1] != u'<'):
                       value = escape(value)
                   if (prop[PROP_DOMAIN] == u'webdav'):
                       wfile.write(u'        <{0}>{1}</{2}>\n'.format(prop[PROP_LOCALNAME],
                                                             value,
                                                             prop[PROP_LOCALNAME]))
                   elif (prop[PROP_NAMESPACE] is None):
                       wfile.write(u'        <{0}>{1}</{2}>\n'.format(prop[PROP_LOCALNAME],
                                                         value,
                                                         prop[PROP_LOCALNAME]))
                   else:
                       wfile.write(u'        <{0} xmlns="{1}">{2}</{3}>\n'.format(prop[PROP_LOCALNAME],
                                                                     prop[PROP_NAMESPACE],
                                                                     value,
                                                                     prop[PROP_LOCALNAME]))
            wfile.write(u'      </prop>\n')
            wfile.write(u'    </propstat>\n')
        # UNKNOWN PROPERTIES
        if (len(unknown) > 0):
            wfile.write(u'    <propstat>\n')
            wfile.write(u'      <status>HTTP/1.1 404 Not found</status>\n')
            wfile.write(u'      <prop>\n')
            for prop in unknown:
                if (prop[PROP_DOMAIN] == 'webdav'):
                    wfile.write(u'        <{0}/>\n'.format(prop[PROP_LOCALNAME]))
                elif (prop[PROP_NAMESPACE] is None):
                    wfile.write(u'        <{0}/>\n'.format(prop[PROP_LOCALNAME]))
                else:
                    wfile.write(u'        <{0} xmlns="{1}"/>\n'.format(prop[PROP_LOCALNAME],
                                                                          prop[PROP_NAMESPACE]))
            wfile.write(u'      </prop>\n')
            wfile.write(u'    </propstat>\n')
        wfile.write(u'  </response>\n')

        depth += -1
        if ((depth > 0) and (self.is_folder)):
            self.load_contents()
            for key in self.get_keys():
                result = self.get_object_for_key(key, auto_load_enabled=True, is_webdav=True)
                if (allprops):
                    result.do_property_response(props=None, depth=depth, wfile=wfile)
                else:
                    result.do_property_response(props=props, depth=depth, wfile=wfile)
