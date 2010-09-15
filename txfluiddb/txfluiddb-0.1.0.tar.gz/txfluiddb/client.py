from urllib import quote, urlencode
from re import compile, U
from base64 import b64encode
import types
import simplejson as json

from txfluiddb.errors import InvalidName, InvalidTagValueType
from txfluiddb.http import getPage



class _HasPath(object):
    """
    Base class for FluidDB identifiers composed of path components.

    @type components: C{list} of C{unicode}
    @ivar components: A list of path components for this identifier.

    @type collectionName: C{unicode}
    @cvar collectionName: The top-level path component under which these
        identifiers exist.

    @type _nameRegex: compiled regex
    @cvar _nameRegex: A regex that matches valid component names.
    """
    _nameRegex = compile(u'^[\w:.-]+$', U)
    collectionName = None


    def __init__(self, name, *rest):
        """
        Accepts one or path components as positional arguments.

        @type  name: C{unicode}
        @param name: The first component.

        @type  rest: C{list} of C{unicode}
        @param rest: Additional components.
        """
        self.components = [name]
        self.components.extend(rest)
        for component in self.components:
            self.checkComponent(component)


    def checkComponent(self, name):
        """
        Verify that a component is a legal name.

        @raise InvalidName: if the name is not legal.

        @return: C{None}
        """
        if not isinstance(name, unicode):
            raise InvalidName(
                'Name of type %r is not unicode: %r' % (type(name), name))

        if self._nameRegex.match(name) is None:
            raise InvalidName('Name contains invalid characters: %r' % name)


    def getPath(self):
        """
        Get the path for this identifier.

        @rtype: C{unicode}
        """
        return u'/'.join(self.components)


    def getURL(self, endpoint, prefix=None, suffix=None, collectionName=None):
        """
        Get the URL for this path as accessed through the given endpoint.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  prefix: C{list} of C{unicode}
        @param prefix: A list of components to prepend before this path.

        @type  suffix: C{list} of C{unicode}
        @param suffix: A list of components to append after this path.

        @type  collectionName: C{unicode}
        @param suffix: A collectionName to use instead of self.collectionName.

        @rtype: C{str}
        """
        if self.collectionName is None:
            raise NotImplementedError(
                'Must override collectionName on _HasPath subclasses')

        components = []
        if prefix:
            components.extend(prefix)
        components.append(collectionName or self.collectionName)
        components.extend(self.components)
        if suffix:
            components.extend(suffix)

        components = [quote(component.encode('utf-8'), safe='')
                      for component in components]
        return endpoint.getRootURL() + '/'.join(components)


class _HasPerms(object):
    """
    Mixin base class for FluidDB elements that have permissions.
    """


    def getPerms(self, endpoint, action):
        url = self.getURL(endpoint,
                          prefix=[u'permissions']) + '?action=%s' % action
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(lambda res: (res[u'policy'], res[u'exceptions']))


    def setPerms(self, endpoint, action, policy, exceptions):
        return endpoint.submit(
            url=self.getURL(endpoint,
                            prefix=[u'permissions']) + '?action=%s' % action,
            method='PUT',
            data={u'policy' : policy, u'exceptions' : exceptions })



class Namespace(_HasPath, _HasPerms):
    """
    Representation of a FluidDB namespace.
    """
    collectionName = u'namespaces'


    def child(self, name):
        """
        Get a sub-namespace.

        @type  name: C{unicode}
        @param name: The name of the new sub-namespace.

        @rtype:  L{Namespace}
        @return: A new namespace object representing a sub-namespace of this
            one of the given name.
        """
        path = list(self.components)
        path.append(name)
        return type(self)(*path)


    def tag(self, name):
        """
        Get a tag.

        @type  name: C{unicode}
        @param name: The name of the tag.

        @rtype:  L{Tag}
        @return: A tag object representing the tag with the given name.
        """
        path = list(self.components)
        path.append(name)
        return Tag(*path)


    def tagValues(self, name):
        """
        Get the tag values.

        @type  name: C{unicode}
        @param name: The name of the tag.

        @rtype:  L{Tag}
        @return: A TagValues object for the tag with the given name.
        """
        path = list(self.components)
        path.append(name)
        return TagValues(*path)


    def getDescription(self, endpoint):
        """
        Get a description of the namespace.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype:  C{Deferred} -> C{unicode}
        @return: The description.
        """
        url = self.getURL(endpoint) + '?returnDescription=true'
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(lambda res: res[u'description'])


    def setDescription(self, endpoint, description):
        """
        Update the namespace description.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  description: C{unicode}
        @param description: The new description.

        @rtype: C{Deferred}
        """
        return endpoint.submit(url=self.getURL(endpoint),
                               method='PUT',
                               data={u'description': description})


    def getNamespaces(self, endpoint):
        """
        Get the namespaces that are children of this namespace.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype:  C{Deferred} -> C{list} of L{Namespace}
        @return: A list of all child namespaces.
        """
        def _parseResponse(response):
            namespaces = []
            for name in response[u'namespaceNames']:
                namespaces.append(self.child(name))
            return namespaces

        url = self.getURL(endpoint) + '?returnNamespaces=true'
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(_parseResponse)


    def getTags(self, endpoint):
        """
        Get the tags in this namespace.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype:  C{Deferred} -> C{list} of L{Tag}
        @return: A list of tags.
        """
        def _parseResponse(response):
            tags = []
            for name in response[u'tagNames']:
                tags.append(self.tag(name))
            return tags

        url = self.getURL(endpoint) + '?returnTags=true'
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(_parseResponse)


    def createChild(self, endpoint, name, description):
        """
        Create a new namespace in this one.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  name: C{unicode}
        @param name: Name of the new namespace.

        @type  description: C{unicode}
        @param description: Description of the new namespace.

        @rtype:  C{Deferred} -> L{Namespace}
        @return: The newly created namespace.
        """
        self.checkComponent(name)
        return endpoint.submit(url=self.getURL(endpoint),
                               method='POST',
                               data={u'name': name,
                                     u'description': description})


    def createTag(self, endpoint, name, description, indexed):
        """
        Create a new tag in this namespace.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  name: C{unicode}
        @param name: Name of the new namespace.

        @type  description: C{unicode}
        @param description: Description of the new namespace.

        @type  indexed: C{bool}
        @param indexed: Should this tag be indexed?

        @rtype:  C{Deferred} -> L{Tag}
        @return: The newly-created tag.
        """
        self.checkComponent(name)
        return endpoint.submit(url=self.getURL(endpoint, collectionName='tags'),
                               method='POST',
                               data={u'name': name,
                                     u'description': description,
                                     u'indexed': indexed})


    def delete(self, endpoint):
        """
        Delete this namespace.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype: C{Deferred}
        """
        return endpoint.submit(url=self.getURL(endpoint),
                               method='DELETE')



class Tag(_HasPath, _HasPerms):
    """
    Representation of a FluidDB tag.
    """
    collectionName = u'tags'


    def getDescription(self, endpoint):
        """
        Get a description of the tag.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype:  C{Deferred} -> C{unicode}
        @return: The description.
        """
        url = self.getURL(endpoint) + '?returnDescription=true'
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(lambda res: res[u'description'])


    def setDescription(self, endpoint, description):
        """
        Update the tag description.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  description: C{unicode}
        @param description: The new description.

        @rtype: C{Deferred}
        """
        return endpoint.submit(url=self.getURL(endpoint),
                               method='PUT',
                               data={u'description': description})


    def delete(self, endpoint):
        """
        Delete this tag.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype: C{Deferred}
        """
        return endpoint.submit(url=self.getURL(endpoint),
                               method='DELETE')



class TagValues(_HasPath, _HasPerms):
    """
    Representation of the set of values of a tag.
    """
    collectionName = u'tag-values'



class BasicCreds(object):
    """
    Credentials for HTTP Basic Authentication.

    @type username: C{str}
    @ivar username: The username.

    @type password: C{str}
    @ivar password: The password.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password


    def encode(self):
        """
        Encode these credentials.

        @rtype:  C{str}
        @return: Encoded form for use in HTTP Authorization header.
        """
        return 'Basic %s' % b64encode(
            '%s:%s' % (self.username, self.password))



FLUIDDB_ENDPOINT = 'http://fluiddb.fluidinfo.com/'
PRIMITIVE_CONTENT_TYPE = 'application/vnd.fluiddb.value+json'



class Endpoint(object):
    """
    A FluidDB endpoint.

    Used to submit requests to FluidDB.

    @type baseURL: C{str}
    @ivar baseURL: The base URL of this endpoint, including the trailing slash.

    @type version: C{str} or C{None}
    @ivar version: The API version to use, or C{None} for the latest.

    @type creds: L{BasicCreds}
    @ivar creds: A credentials object, or C{None} to authenticate anonymously.
    """
    def __init__(self, baseURL=FLUIDDB_ENDPOINT, version=None, creds=None):
        if creds is not None and not isinstance(creds, BasicCreds):
            raise ValueError('Only basic authentication is supported')

        if not baseURL.endswith("/"):
            baseURL = baseURL + "/"
        self.baseURL = baseURL
        self.version = version
        self.creds = creds


    def getRootURL(self):
        """
        Get the root endpoint URL, including trailing slash.
        """
        url = self.baseURL
        if self.version is not None:
            url += self.version + '/'
        return url


    def getPage(self, *a, **kw):
        """
        Wrap getPage to allow overriding for test purposes.
        """
        return getPage(*a, **kw)


    def submit(self, url, method, data=None, headers=None, parsePayload=True):
        """
        Submit a request through this endpoint.

        If a string is passed as the data, it will be used as-is; otherwise, it
        will be encoded as JSON and sent with an appropriate Content-Type.

        @type  url: C{str}
        @param url: The URL to request.

        @type  method: C{str}
        @param method: The HTTP verb to be used in the request.

        @type  data: C{str} or C{None} or JSON-encodable value
        @param data: The request body, or C{None} to omit it.

        @type  headers: C{dict} of C{str}: C{str}
        @param headers: HTTP headers to include in the request.

        @type  parsePayload: C{bool}
        @param parsePayload: If True, any payload will be parsed as JSON
        """
        if headers is None:
            headers = {}

        if data is not None:
            if isinstance(data, dict):
                assert 'Content-Type' not in headers
                headers['Content-Type'] = 'application/json'
                data = json.dumps(data)
            else:
                assert 'Content-Type' in headers

        if self.creds is not None:
            headers['Authorization'] = self.creds.encode()

        def _parse((status, headers, page)):
            if page:
                # assert headers['content-type'] == 'application/json'
                return loads(page)

        d = self.getPage(url=url,
                         method=method,
                         postdata=data,
                         headers=headers,
                         agent='txFluidDB')
        
        if parsePayload:
            d.addCallback(_parse)

        return d


    def setTagValue(self, url, value=None, valueType=None):
        """
        Submit a request through this endpoint.

        @type  url: C{str}
        @param url: The URL of the tag.

        @type  value: Variable (None, bool, int, float, str, list of str).
        @param value: The value to store.

        @type  valueType: C{None} or a MIME content-type string.
        @param value: The content type of the value to store.
        """
        headers = {}

        if valueType:
            # We're sending a blob whose type has been passed.
            headers['Content-Type'] = valueType
            data = value
        else:
            tv = type(value)
            if tv in (types.NoneType, bool, int, float, str, unicode, list,
                      tuple):
                if tv in (list, tuple):
                    if not all([isinstance(v, basestring) for v in value]):
                        raise InvalidTagValueType(
                            'Non-string in list payload %r.' % (value,))
                headers['Content-Type'] = PRIMITIVE_CONTENT_TYPE
                data = json.dumps(value)
            else:
                raise InvalidTagValueType(
                    "Can't handle payload %r of type %s" % (value, tv))

        return self.submit(url, 'PUT', data, headers)


    def getTagValue(self, url):
        def _parse((status, headers, page)):
            # Let this raise a KeyError if there's no content-type header?
            ct = headers['content-type'][0]
            if ct == PRIMITIVE_CONTENT_TYPE:
                return loads(page)
            else:
                return Blob(ct, page)
            
        d = self.submit(url, 'GET', parsePayload=False)
        return d.addCallback(_parse)



class Object(_HasPath):
    """
    A FluidDB object.

    @type uuid: C{unicode}
    @ivar uuid: The UUID of the object.
    """
    collectionName = u'objects'


    def __init__(self, uuid):
        self.uuid = uuid


    @property
    def components(self):
        """
        Our only path component is the object UUID.
        """
        return [self.uuid]


    @classmethod
    def create(cls, endpoint, about=None):
        """
        Create a new object.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  about: C{unicode} or C{None}
        @param about: The value for the about tag, if desired.

        @rtype:  C{Deferred} -> L{Object}
        @return: The newly created object.
        """
        url = endpoint.getRootURL() + 'objects'
        
        if about is not None:
            data = {u'about' : about}
        else:
            data = None

        def _parseResponse(response):
            return Object(response[u'id'])

        d = endpoint.submit(url=url, method='POST', data=data)
        return d.addCallback(_parseResponse)


    @classmethod
    def query(cls, endpoint, query):
        """
        Search for objects that match a query.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  query: C{unicode}
        @param query: A query string to search on.

        @rtype:  C{list} of L{Object}
        @return: The matching objects.
        """
        qs = '?' + urlencode({'query': query.encode('utf-8')})
        url = endpoint.getRootURL() + 'objects' + qs

        def _parseResponse(response):
            return [Object(uuid) for uuid in response['ids']]

        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(_parseResponse)


    def getTags(self, endpoint):
        """
        Get the visible tags on this object.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @rtype:  C{Deferred} -> (C{unicode}, C{list} of L{Tag})
        @return: A tuple of the about tag value and the list of tags.
        """
        def _parseResponse(response):
            about = response[u'about']
            tags = [Tag(*path.split(u'/')) for path in response[u'tagPaths']]
            # I'm not sure it makes sense to return the about value. Why is
            # this method called getTags?
            return (about, tags)

        qs = '?' + urlencode({'showAbout': 'True'})
        url = self.getURL(endpoint) + qs
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(_parseResponse)


    def get(self, endpoint, tag):
        """
        Get the value of a tag on this object.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  tag: L{Tag}
        @param tag: The tag to retrieve.

        @rtype:  Varies depending on what value is stored.
        @return: The stored value.
        """
        url = self.getURL(endpoint, suffix=tag.components)
        return endpoint.getTagValue(url)
        

    def set(self, endpoint, tag, value, valueType=None):
        """
        Set the value of a tag on this object.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  tag: L{Tag}
        @param tag: The tag to set or replace.

        @type  value: Variable (None, bool, int, float, str, list of str).
        @param value: The value to store.

        @type  valueType: C{None} or a MIME content-type string.
        @param value: The content type of the value to store.
        """
        url = self.getURL(endpoint, suffix=tag.components)
        return endpoint.setTagValue(url,
                                    value=value,
                                    valueType=valueType)


    def setBlob(self, endpoint, tag, value):
        """
        Set the value of a tag on this object to a blob.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  tag: L{Tag}
        @param tag: The tag to set or replace.

        @type  value: L{Blob}
        @param value: The value to store.
        """
        url = self.getURL(endpoint, suffix=tag.components)
        return endpoint.setTagValue(url,
                                    value=value.data,
                                    valueType=value.contentType)


    def delete(self, endpoint, tag):
        """
        Delete a tag from this object.

        Note that FluidDB does not support deleting objects themselves.

        @type  endpoint: L{Endpoint}
        @param endpoint: The endpoint to operate through.

        @type  tag: L{Tag}
        @param tag: The tag to retrieve.
        """
        url = self.getURL(endpoint, suffix=tag.components)
        return endpoint.submit(url=url, method='DELETE')



class Blob(object):
    """
    A binary blob with a MIME content type.

    @type contentType: C{unicode}
    @ivar contentType: The MIME content-type of the data.

    @type data: C{str}
    @ivar data: The actual data.
    """
    def __init__(self, contentType, data):
        self.contentType = contentType
        self.data = data



def loads(data):
    """
    Load JSON data and decode it into Python objects.

    This function always converts JSON data to C{unicode} before decoding it
    into Python objects.  This guarantees that strings are always represented
    as C{unicode} objects.

    @type data: C{str} or C{unicode}
    @param data: The JSON data to load, assumed to be encoded in UTF-8.
    @return: A Python representation of C{data}.
    """
    if isinstance(data, str):
        data = unicode(data, 'utf-8')
    return json.loads(data)



__all__ = ['Namespace', 'Tag', 'BasicCreds', 'FLUIDDB_ENDPOINT', 'Endpoint',
           'Object', 'Blob']
