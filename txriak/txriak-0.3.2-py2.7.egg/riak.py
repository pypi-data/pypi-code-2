"""
.. module:: riak.py

.. moduleauthor:: Appropriate Solutions, Inc. <asi@AppropriateSolutions.com>

Main file of txriak module, a twisted module for
communicating with Basho Technology's Riak data store.

Copyright (c) 2010-2011 Appropriate Solutions, Inc. All rights reserved.
See txriak.LICENSE for specifics.

Important note about Riak meta data and Twisted.
Twisted always lowercases the meta data header.
However, Twisted _does not_ lowercase the data returned by that header.

.. todo:: Handle meta-data on Riak objects.
.. todo:: Test for invalid data in meta data strings.
.. todo:: Move DEBUG into class initialization.
.. todo:: Convert getters and setters to properties.
.. todo:: Remove RiakUtils.get_values.
.. todo:: unit vs. functional tests.
.. todo:: more robust _assemble
"""

import random
import base64
import urllib
import re
import json
import codecs
from twisted.internet import defer
from twisted.internet import reactor
from zope.interface import implements
from twisted.web import client
from twisted.web.http import PotentialDataLoss
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.internet.protocol import Protocol
from twisted.web._newclient import ResponseDone
from StringIO import StringIO


DEBUG = False


class StringProducer(object):
    """
    Body producer for t.w.c.Agent
    """
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        return defer.maybeDeferred(consumer.write, self.body)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


class ResponseReceiver(Protocol):
    """
    Assembles HTTP response from return stream.
    """

    def __init__(self, deferred):
        self.writer = codecs.getwriter("utf_8")(StringIO())
        self.deferred = deferred

    def dataReceived(self, bytes):
        self.writer.write(bytes)

    def connectionLost(self, reason):
        if reason.check(ResponseDone) or reason.check(PotentialDataLoss):
            self.deferred.callback(self.writer.getvalue())
        else:
            self.deferred.errback(reason)


def getPageWithHeaders(contextFactory=None,
                      scheme='http', host='127.0.0.1', port=80, path='/',
                      *args, **kwargs):
    """Download a web page as a string.

    :returns: twisted.web.client.Agent deferred.

    Download a page. Return a deferred, which will callback with a
    page (as a string) or errback with a description of the error.

    See t.w.c.Agent to see what extra args can be passed.
    """

    def cb_recv_resp(response):
        d_resp_recvd = defer.Deferred()
        if response.length:
            response.deliverBody(ResponseReceiver(d_resp_recvd))
            return d_resp_recvd.addCallback(cb_process_resp, response)
        else:
            return cb_process_resp("", response)

    def cb_process_resp(body, response):
        _headers = {"http_code": response.code}

        for header in response.headers.getAllRawHeaders():
            _headers[header[0].lower()] = header[1][0]

        return _headers, body

    url = str("http://%s:%d%s" % (host, port, path))

    if DEBUG:
        print "==========================="
        print ">>uri: %s" % url
        print ">>method: %s" % kwargs.get('method', None)
        print ">>headers: %s" % kwargs.get('headers', None)
        print ">>cookies: %s" % kwargs.get('cookies', None)
        print ">>postdata: %s" % kwargs.get('postdata', None)

    if not "headers" in kwargs:
        kwargs["headers"] = {}
    else:
        for header in kwargs["headers"]:
            kwargs["headers"][header] = [kwargs["headers"][header]]

    if not "method" in kwargs:
        kwargs["method"] == "GET"

    if "postdata" in kwargs:
        body = StringProducer(kwargs["postdata"])
    else:
        body = None

    d = client.Agent(reactor).request(kwargs["method"],
                                      url,
                                      Headers(kwargs["headers"]),
                                      body)

    d.addCallback(cb_recv_resp)
    return d


def flatten_js(js_func):
    """Flatten a JavaScript function into a single line.

    :returns: String.

    Take a JavaScript function and strip out all of the
    newlines so that it is suitable for passing into a
    Riak map/reduce phase.
    """

    return "".join(js_func.split("\n"))


class RiakClient(object):
    """
    The RiakClient object holds information necessary to connect to
    Riak.
    """
    def __init__(self, host='127.0.0.1', port=8098,
                prefix='riak', mapred_prefix='mapred',
                client_id=None, r_value=2, w_value=2, dw_value=0):
        """
        Construct a new RiakClient object.

        If a client_id is not provided, generate a random one.
        """
        self._host = host
        self._port = port
        self._prefix = prefix
        self._mapred_prefix = mapred_prefix
        if client_id:
            self._client_id = client_id
        else:
            self._client_id = 'py_' + base64.b64encode(
                                      str(random.randint(1, 1073741824)))
        self._r = r_value
        self._w = w_value
        self._dw = dw_value
        return None

    def get_r(self):
        """
        Get the R-value setting for this RiakClient. (default 2)
        :returns: integer representing current r-value
        .. todo:: remove accessor
        """
        return self._r

    def set_r(self, r):
        """
        Set the R-value for this RiakClient. This value will be used
        for any calls to get(...) or get_binary(...) where where 1) no
        R-value is specified in the method call and 2) no R-value has
        been set in the RiakBucket.
        @param integer r - The R value.
        @return self
        .. todo:: remove accessor
        """
        self._r = r
        return self

    def get_w(self):
        """
        Get the W-value setting for this RiakClient. (default 2)
        @return integer
        .. todo:: remove accessor
        """
        return self._w

    def set_w(self, w):
        """
        Set the W-value for this RiakClient. See set_r(...) for a
        description of how these values are used.
        @param integer w - The W value.
        @return self
        .. todo:: remove accessor
        """
        self._w = w
        return self

    def get_dw(self):
        """
        Get the DW-value for this ClientOBject. (default 2)
        @return integer
        .. todo:: remove accessor
        """
        return self._dw

    def set_dw(self, dw):
        """
        Set the DW-value for this RiakClient. See set_r(...) for a
        description of how these values are used.
        @param integer dw - The DW value.
        @return self
        .. todo:: remove accessor
        """
        self._dw = dw
        return self

    def get_client_id(self):
        """
        Get the client_id for this RiakClient.
        @return string
        .. todo:: remove accessor
        """
        return self._client_id

    def set_client_id(self, client_id):
        """
        Set the client_id for this RiakClient. Should not be called
        unless you know what you are doing.
        @param string client_id - The new client_id.
        @return self
        .. todo:: remove accessor
        """
        self._client_id = client_id
        return self

    def bucket(self, name):
        """
        Get the bucket by the specified name. Since buckets always exist,
        this will always return a RiakBucket.
        :returns: RiakBucket instance.
        """
        return RiakBucket(self, name)

    @defer.inlineCallbacks
    def is_alive(self):
        """
        Check if the Riak server for this RiakClient is alive.
        :returns: True if alive -- via deferred.
        """
        response = yield RiakUtils.http_request_deferred('GET', self._host,
                                          self._port, '/ping')
        defer.returnValue((response != None) and (response[1] == 'OK'))

    def add(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.add()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self)
        return apply(mr.add, args)

    def link(self, args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.link()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self)
        return apply(mr.link, args)

    @defer.inlineCallbacks
    def list_buckets(self):
        """
        Retrieve a list of all buckets.

        :returns: list -- via deferred
        """
        # Create the request
        params = {"buckets": "true"}

        host, port, url = RiakUtils.build_rest_path(self,
                                                    None,
                                                    None,
                                                    None,
                                                    params)
        raw_response = yield RiakUtils.http_request_deferred('GET', host,
                                                             port, url)

        if raw_response[0]["http_code"] != 200:
            raise Exception('Error listing buckets.')

        # Parse the bucket list
        buckets = json.loads(raw_response[1])["buckets"]

        defer.returnValue([urllib.unquote(x) for x in buckets])

    def map(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.map()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self)
        return apply(mr.map, args)

    def reduce(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.reduce()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self)
        return apply(mr.reduce, args)


class RiakMapReduce(object):
    """
    The RiakMapReduce object allows you to build up and run a
    map/reduce operation on Riak.
    """

    def __init__(self, client):
        """
        Initialize a Map/Reduce object.
        :param client: a RiakClient object.
        :returns: Nothing
        """
        self._client = client
        self._phases = []
        self._inputs = []
        self._input_mode = None
        return None

    def add(self, arg1, arg2=None, arg3=None):
        """
        Add inputs to a map/reduce operation. This method takes three
        different forms, depending on the provided inputs. You can
        specify either a RiakObject, a string bucket name, or a bucket,
        key, and additional arg.
        :param arg1: RiakObject or Bucket or Key Filter
        :param arg2: Key or blank
        :param arg3: Arg or blank
        :returns: RiakMapReduce

        Key filters are dictionaries of the form:

            {"bucket": "<bucket_name>",
             "key_filters": [ ["<operation>", "<arg1>", "<argN>"],
                             ]}
        """
        if (arg2 == None) and (arg3 == None):
            if isinstance(arg1, RiakObject):
                return self.add_object(arg1)
            elif isinstance(arg1, dict):
                return self.add_key_filter(arg1)
            else:
                return self.add_bucket(arg1)
        else:
            return self.add_bucket_key_data(arg1, arg2, arg3)

    def add_object(self, obj):
        """Set bucket key data with object."""
        return self.add_bucket_key_data(obj._bucket._name, obj._key, None)

    def add_bucket_key_data(self, bucket, key, data):
        """Add data to the bucket."""
        if self._input_mode == 'bucket' or \
           self._input_mode == 'key_filter':
            raise Exception(('Already added a %s, ' % self._input_mode) +
                            'can\'t add an object.')
        else:
            self._inputs.append([bucket, key, data])
            return self

    def add_bucket(self, bucket):
        """Set bucket to work with."""
        self._input_mode = 'bucket'
        self._inputs = bucket
        return self

    def add_key_filter(self, key_filter):
        """Set up key filter to use."""
        if self._input_mode == 'bucket':
            raise Exception('Already added a bucket can\'t add a key filter.')
        else:
            self._input_mode = "key_filter"
            self._inputs = key_filter
            return self

    def link(self, bucket='_', tag='_', keep=False):
        """
        Add a link phase to the map/reduce operation.
        :param bucket: Bucket name (default '_' means all buckets)
        :param tag: Tag (default '_' means all tags)
        :param keep: Boolean flag to keep results from this stage.
        :returns: self
        """
        self._phases.append(RiakLinkPhase(bucket, tag, keep))
        return self

    def map(self, function, options=None):
        """
        Add a map phase to the map/reduce operation.
        :param function: Function to run
        :param options: Optional dictionary.
        :returns: self

        The function can be either a named Javascript function:
            'Riak.mapValues'
        an anonymous JavaScript function:
            'function(...)  ... )'
        or a list:
            ['erlang_module', 'function']

        The options is an associative array containing:
            'language',
            'keep' flag, and/or
            'arg'

        .. todo:: Remove get_value and use {}.get()
        """
        if options == None:
            options = []

        if isinstance(function, list):
            language = 'erlang'
        else:
            language = 'javascript'

        mr = RiakMapReducePhase('map',
                                function,
                                RiakUtils.get_value('language', options,
                                                     language),
                                RiakUtils.get_value('keep', options,
                                                     False),
                                RiakUtils.get_value('arg', options,
                                                     None))
        self._phases.append(mr)
        return self

    def reduce(self, function, options=None):
        """
        Add a reduce phase to the map/reduce operation.

        :param function: Function to run
        :param options: Optional dictionary.
        :returns: self

        The function can be either a named Javascript function:
            'Riak.mapValues'
        an anonymous JavaScript function:
            'function(...)  ... )'
        or a list:
            ['erlang_module', 'function']

        The optios is an associative array containing:
            'language',
            'keep' flag, and/or
            'arg'

        .. todo:: Remove get_value and use {}.get()
        """
        if options == None:
            options = []

        if isinstance(function, list):
            language = 'erlang'
        else:
            language = 'javascript'

        mr = RiakMapReducePhase('reduce',
                                function,
                                RiakUtils.get_value('language', options,
                                                     language),
                                RiakUtils.get_value('keep', options,
                                                     False),
                                RiakUtils.get_value('arg', options,
                                                     None))
        self._phases.append(mr)
        return self

    @defer.inlineCallbacks
    def run(self, timeout=None):
        """
        Run the map/reduce operation. Returns a list of results, or an
        array of RiakLink objects if the last phase is a link phase.

        :param timeout: Timeout in seconds. Defaults to waiting forever.
        :returns: list of results  -- via deferred
        """

        # Convert all phases to associative arrays. Also,
        # if none of the phases are accumulating, then set the last one to
        # accumulate.
        num_phases = len(self._phases)
        keep_flag = False
        query = []
        for i in range(num_phases):
            phase = self._phases[i]
            if (i == (num_phases - 1)) and (not keep_flag):
                phase._keep = True
            if phase._keep:
                keep_flag = True
            query.append(phase._to_array())

        # Construct the job, optionally set the timeout...
        job = {'inputs': self._inputs, 'query': query}
        if timeout != None:
            job['timeout'] = timeout

        content = json.dumps(job)

        # Do the request...
        host = self._client._host
        port = self._client._port
        url = "/" + self._client._mapred_prefix
        response = yield RiakUtils.http_request_deferred('POST', host, port,
                                                          url, {}, content)
        if response[0]["http_code"] > 299:
            raise Exception("Error running map/reduce job. Error: " +
                            response[1])
        result = json.loads(response[1])

        # If the last phase is NOT a link phase, then return the result.
        lastIsLink = isinstance(self._phases[-1], RiakLinkPhase)
        if not lastIsLink:
            defer.returnValue(result)

        # Otherwise, if the last phase IS a link phase, then convert the
        # results to RiakLink objects.
        a = []
        for r in result:
            link = RiakLink(r[0], r[1], r[2])
            link._client = self._client
            a.append(link)

        defer.returnValue(a)


class RiakMapReducePhase(object):
    """
    The RiakMapReducePhase holds information about a Map phase or
    Reduce phase in a RiakMapReduce operation.
    """

    def __init__(self, type, function, language, keep, arg):
        """
        Construct a RiakMapReducePhase object.

        :param type: 'map' or 'reduce'
        :param function: string or array
        :param language: 'javascript' or 'erlang'
        :param keep: True to return the output of this phase in results.
        :param arg: Additional value to pass into the map or reduce function.
        :returns: None
        """
        self._type = type
        self._language = language
        self._function = function
        self._keep = keep
        self._arg = arg
        return None

    def _to_array(self):
        """
        Convert the RiakMapReducePhase to an associative array. Used
        internally.
        """
        stepdef = {'keep': self._keep,
                   'language': self._language,
                   'arg': self._arg}

        if ((self._language == 'javascript') and
              isinstance(self._function, list)):
            stepdef['bucket'] = self._function[0]
            stepdef['key'] = self._function[1]
        elif ((self._language == 'javascript') and
                isinstance(self._function, str)):
            if ("{" in self._function):
                stepdef['source'] = self._function
            else:
                stepdef['name'] = self._function

        elif (self._language == 'erlang' and isinstance(self._function, list)):
            stepdef['module'] = self._function[0]
            stepdef['function'] = self._function[1]

        return {self._type: stepdef}


class RiakLinkPhase(object):
    """
    The RiakLinkPhase object holds information about a Link phase in a
    map/reduce operation.
    """

    def __init__(self, bucket, tag, keep):
        """
        Construct a RiakLinkPhase object.
        @param string bucket - The bucket name.
        @param string tag - The tag.
        @param boolean keep - True to return results of this phase.
        """
        self._bucket = bucket
        self._tag = tag
        self._keep = keep
        return None

    def _to_array(self):
        """
        Convert the RiakLinkPhase to an associative array. Used
        internally.
        """
        stepdef = {'bucket': self._bucket,
                   'tag': self._tag,
                   'keep': self._keep}
        return {'link': stepdef}


class RiakLink(object):
    """
    The RiakLink object represents a link from one Riak object to
    another.
    @package RiakLink
    """

    def __init__(self, bucket, key, tag=None):
        """
        Construct a RiakLink object.

        :param bucket: The bucket name
        :param key: The key name
        :param tag: The tag name
        :returns: None
        """
        self._bucket = bucket
        self._key = key
        self._tag = tag
        self._client = None
        return None

    def get(self, r=None):
        """
        Retrieve the RiakObject to which this link points.

        :param r: R-value to use for this call.
        :returns: RiakObject

        .. todo:: this looks wrong. r should be override of r, not _key.
        """
        return self._client.bucket(self._bucket).get(self._key, r)

    def get_binary(self, r=None):
        """
        Retrieve the RiakObject to which this link points, as a binary.

        :param r: R-value to use for this call.
        :returns: RiakObject

        .. todo:: this looks wrong. r should be override of r, not _key.
        """
        return self._client.bucket(self._bucket).get_binary(self._key, r)

    def get_bucket(self):
        """
        Get the bucket name of this link.

        :returns: bucket name, not the object

        .. todo:: remove accessor
        """
        return self._bucket

    def set_bucket(self, name):
        """
        Set the bucket name of this link.
        @param string name - The bucket name.
        @return self

        .. todo:: remove accessor
        """
        self._bucket = name
        return self

    def get_key(self):
        """
        Get the key of this link.
        @return string

        .. todo:: remove accessor
        """
        return self._key

    def set_key(self, key):
        """
        Set the key of this link.
        @param string key - The key.
        @return self
        .. todo:: remove accessor
        """
        self._key = key
        return self

    def get_tag(self):
        """
        Get the tag of this link.
        @return string
        .. todo:: convert to a property
        """
        if (self._tag == None):
            return self._bucket
        else:
            return self._tag

    def set_tag(self, tag):
        """
        Set the tag of this link.
        @param string tag - The tag.
        @return self
        .. todo:: convert to a property
        """
        self._tag = tag
        return self

    def _to_link_header(self, client):
        """
        Convert this RiakLink object to a link header string. Used internally.
        """
        link = ''
        link += '</'
        link += client._prefix + '/'
        link += urllib.quote_plus(self._bucket) + '/'
        link += urllib.quote_plus(self._key) + '>; riaktag="'
        link += urllib.quote_plus(self.get_tag()) + '"'
        return link

    def isEqual(self, link):
        """
        Return True if this link and self are equal.

        :param link: RiakLink object
        :returns: True if equal
        """
        is_equal = ((self._bucket == link._bucket) and
                     (self._key == link._key) and
                     (self.get_tag() == link.get_tag())
                   )
        return is_equal


class RiakBucket(object):
    """
    The RiakBucket object allows you to access and change information
    about a Riak bucket, and provides methods to create or retrieve
    objects within the bucket.
    """

    def __init__(self, client, name):
        """
        Initialize RiakBucket
        """
        self._client = client
        self._name = name
        self._r = None
        self._w = None
        self._dw = None
        return None

    def get_name(self):
        """
        Get the bucket name.
        .. todo:: remove accessors
        """
        return self._name

    def get_r(self, r=None):
        """
        Get the R-value for this bucket, if it is set, otherwise return
        the R-value for the client.
        :rtype: return integer
        .. todo:: make into property
        """
        if (r != None):
            return r
        if (self._r != None):
            return self._r
        return self._client.get_r()

    def set_r(self, r):
        """
        Set the R-value for this bucket. get(...) and get_binary(...)
        operations that do not specify an R-value will use this value.
        @param integer r - The new R-value.
        @return self
        .. todo:: convert to property
        """
        self._r = r
        return self

    def get_w(self, w):
        """
        Get the W-value for this bucket, if it is set, otherwise return
        the W-value for the client.
        @return integer
        .. todo:: convert to property
        """
        if (w != None):
            return w
        if (self._w != None):
            return self._w
        return self._client.get_w()

    def set_w(self, w):
        """
        Set the W-value for this bucket. See set_r(...) for more information.
        @param integer w - The new W-value.
        @return self
        .. todo:: convert to property
        """
        self._w = w
        return self

    def get_dw(self, dw):
        """
        Get the DW-value for this bucket, if it is set, otherwise return
        the DW-value for the client.
        @return integer
        .. todo:: convert to property
        """
        if (dw != None):
            return dw
        if (self._dw != None):
            return self._dw
        return self._client.get_dw()

    def set_dw(self, dw):
        """
        Set the DW-value for this bucket. See set_r(...) for more information.
        @param integer dw - The new DW-value
        @return self
        .. todo:: convert to property
        """
        self._dw = dw
        return self

    def new(self, key, data=None):
        """
        Create a new Riak object that will be stored as JSON.

        :param key: Name of the key.
        :param data: The data to store.
        :returns: RiakObject
        """
        obj = RiakObject(self._client, self, key)
        obj.set_data(data)
        obj.set_content_type('text/json')
        obj._jsonize = True
        return obj

    def new_binary(self, key, data, content_type='text/json'):
        """
        Create a new Riak object that will be stored as plain text/binary.

        :param key: Name of the key.
        :param data: The data to store.
        :param content_type: The content type of the object.
        :returns: RiakObject
        """
        obj = RiakObject(self._client, self, key)
        obj.set_data(data)
        obj.set_content_type(content_type)
        obj._jsonize = False
        return obj

    @defer.inlineCallbacks
    def get(self, key, r=None):
        """
        Retrieve a JSON-encoded object from Riak.

        :param key: Name of the key.
        :param r: R-Value of this request (defaults to bucket's R)
        :returns: RiakObject -- via deferred
        """
        obj = RiakObject(self._client, self, key)
        obj._jsonize = True
        r = self.get_r(r)
        result = yield obj.reload(r)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def get_binary(self, key, r=None):
        """
        Retrieve a binary/string object from Riak.

        :param key: Name of the key.
        :param r: R-Value of this request (defaults to bucket's R)
        :returns: RiakObject -- via deferred
        """
        obj = RiakObject(self._client, self, key)
        obj._jsonize = False
        r = self.get_r(r)
        result = yield obj.reload(r)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def set_n_val(self, nval):
        """
        Set the N-value for this bucket, which is the number of replicas
        that will be written of each object in the bucket. Set this once
        before you write any data to the bucket, and never change it
        again, otherwise unpredictable things could happen. This should
        only be used if you know what you are doing.
        @param integer nval - The new N-Val.
        .. todo:: Given the danger, some way to first check for existence?
        """
        result = yield self.set_property('n_val', nval)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def get_n_val(self):
        """
        Retrieve the N-value for this bucket.
        @return integer
        .. todo:: what happens if you ask for n_val before ever writing?
        """
        result = yield self.get_property('n_val')
        defer.returnValue(result)

    @defer.inlineCallbacks
    def set_allow_multiples(self, the_bool):
        """
        If set to True, then writes with conflicting data are stored
        and returned to the client. This situation can be detected by
        calling has_siblings() and get_siblings(). This should only be used
        if you know what you are doing.

        :param the_bool: True to store and return conflicting writes.
        :returns: deferred
        """
        result = yield self.set_property('allow_mult', the_bool)

        defer.returnValue(result)

    @defer.inlineCallbacks
    def get_allow_multiples(self):
        """
        Retrieve the 'allow multiples' setting.

        :returns: Boolean -- via deferred
        """
        result = yield self.get_property('allow_mult')

        defer.returnValue(result)

    @defer.inlineCallbacks
    def set_property(self, key, value):
        """
        Set a bucket property. This should only be used if you know what
        you are doing.

        :param key: property to set.
        :param value: property value to set.
        :returns: deferred result
        """
        result = yield self.set_properties({key: value})

        defer.returnValue(result)

    @defer.inlineCallbacks
    def get_property(self, key):
        """
        Retrieve a bucket property.

        :param key: property to retrieve
        :returns: property value -- as deferred
        """

        props = yield self.get_properties()

        if (key in props.keys()):
            defer.returnValue(props[key])
        else:
            defer.returnValue(None)

    @defer.inlineCallbacks
    def set_properties(self, props):
        """
        Set multiple bucket properties in one call. This should only be
        used if you know what you are doing.

        :param props: a dictionary of keys and values to store.
        :returns: deferred
        """
        host, port, url = RiakUtils.build_rest_path(self._client, self)
        headers = {'Content-Type': 'application/json'}
        content = json.dumps({'props': props})

        #Run the request...
        response = yield RiakUtils.http_request_deferred('PUT', host,
                                                         port, url,
                                                         headers, content)

        # Handle the response...
        if (response == None):
            raise Exception('Error setting bucket properties.')

        # Check the response value...
        status = response[0]['http_code']
        if (status != 204):
            raise Exception('Error setting bucket properties.')
        defer.returnValue(response)

    @defer.inlineCallbacks
    def get_properties(self):
        """
        Retrieve a dictionary of all bucket properties.

        :returns: dictionary -- via deferred
        """

        # Run the request...
        params = {'props': 'True', 'keys': 'False'}
        host, port, url = RiakUtils.build_rest_path(self._client, self,
                                                    None, None, params)
        response = yield RiakUtils.http_request_deferred('GET', host,
                                                         port, url)

        # Use a RiakObject to interpret the response.
        # We are just interested in the value.
        obj = RiakObject(self._client, self, None)
        obj._populate(response, [200])
        if (not obj.exists()):
            raise Exception('Error getting bucket properties.')

        props = obj.get_data()
        props = props['props']
        defer.returnValue(props)

    @defer.inlineCallbacks
    def list_keys(self):
        """
        Retrieve a list of all bucket keys.

        :returns: list -- via deferred
        """
        # Create the request
        params = {"keys": "stream"}

        host, port, url = RiakUtils.build_rest_path(self._client,
                                                    self,
                                                    None,
                                                    None,
                                                    params)
        raw_response = yield RiakUtils.http_request_deferred('GET', host,
                                                             port, url)

        if raw_response[0]["http_code"] != 200:
            raise Exception('Error listing keys in bucket %s.' % self._name)

        # Hacky method to deal with the concatenated response
        # we get due to the chunked encoding method.
        parts = raw_response[1].split('{"keys":[')
        keys = []

        for part in parts[1:]:
            temp_keys = json.loads('{"keys":[' + part)["keys"]
            keys = keys + temp_keys

        defer.returnValue([urllib.unquote(x) for x in keys])

    @defer.inlineCallbacks
    def purge_keys(self):
        """
        Purge all keys from the bucket.

        :returns: None

        This is a convenience function that lists all of the keys
        in the bucket and then deletes them.

        NB: This is a VERY resource-intensive operation, and is
            IRREVERSIBLE. Be careful.
        """

        # Get the current key list
        keys = yield self.list_keys()

        # Major key-killing action
        for key in keys:
            obj = yield self.get(key)
            yield obj.delete()

        return


class RiakObject(object):
    """
    The RiakObject holds meta information about a Riak object, plus the
    object's data.
    """

    def __init__(self, client, bucket, key=None):
        """
        Construct a new RiakObject.
        :param client: A RiakClient object.
        :param bucket: A RiakBucket object.
        :param key: Optional key.

        If key is not specified, then it is generated by server when
        store(...) is called.
        """
        self._client = client
        self._bucket = bucket
        self._key = key
        self._jsonize = True
        self._headers = {}
        self._links = []
        self._siblings = []
        self._metas = {}
        self._exists = False
        self._data = None
        return None

    def get_bucket(self):
        """
        Get the bucket of this object.
        @return RiakBucket
        .. todo:: remove accessor
        """
        return self._bucket

    def get_key(self):
        """
        Get the key of this object.
        @return string
        .. todo:: remove accessor
        """
        return self._key

    def get_data(self):
        """
        Get the data stored in this object. Will return a associative
        array, unless the object was constructed with new_binary(...) or
        get_binary(...), in which case this will return a string.
        @return array or string
        .. todo:: remove accessor
        """
        return self._data

    def set_data(self, data):
        """
        Set the data stored in this object. This data will be
        JSON encoded unless the object was constructed with
        new_binary(...) or get_binary(...).
        @param mixed data - The data to store.
        @return data
        .. todo:: remove accessor
        """
        self._data = data
        return self

    def status(self):
        """
        Get the HTTP status from the last operation on this object.
        @return integer
        .. todo:: convert to property
        """
        return self._headers['http_code']

    def exists(self):
        """
        Return True if the object exists, False otherwise. Allows you to
        detect a get(...) or get_binary(...) operation where the
        object is missing.
        @return boolean
        .. todo:: remove accessor
        """
        return self._exists

    def get_content_type(self):
        """
        Get the content type of this object. This is either text/json, or
        the provided content type if the object was created via
        new_binary(...).
        @return string
        .. todo:: convert to property
        """
        return self._headers['content-type']

    def set_content_type(self, content_type):
        """
        Set the content type of this object.
        @param string content_type - The new content type.
        @return self
        .. todo:: convert to property
        """
        self._headers['content-type'] = content_type
        return self

    def add_link(self, obj, tag=None):
        """
        Add a link to a RiakObject.
        :param obj:  RiakObject or a RiakLink object.
        :param tag: Optional link tag.
        :returns: RiakObject

        Default for the tag is the bucket name.
        Tag is ignored if obj is a RiakLink object.
        """
        if isinstance(obj, RiakLink):
            newlink = obj
        else:
            newlink = RiakLink(obj._bucket._name, obj._key, tag)

        self.remove_link(newlink)
        self._links.append(newlink)
        return self

    def remove_link(self, obj, tag=None):
        """
        Remove a link to a RiakObject.

        :param obj:RiakObject or a RiakLink object.
        :param tag: Optional link tag.
        :returns: self

        Default for the tag is the bucket name.
        Tag is ignored if obj is a RiakLink object.
        """
        if isinstance(obj, RiakLink):
            oldlink = obj
        else:
            oldlink = RiakLink(obj._bucket._name, obj._key, tag)

        a = []
        for link in self._links:
            if not link.isEqual(oldlink):
                a.append(link)

        self._links = a
        return self

    def get_links(self):
        """
        Return a list of RiakLink objects.

        :returns: list of RiakLink objects
        """
        # Set the clients before returning...
        for link in self._links:
            link._client = self._client
        return self._links

    def add_meta_data(self, key, data):
        """
        Add one meta data to object.
        Store in a dictionary so there's only one copy.

        :param key: string to add to metas dictionary
        :param data: data value for key
        :returns: self
        """
        self._metas[key] = data
        return self

    def remove_meta_data(self, data):
        """
        Remove meta data from object.

        :param data: string to remove from meta data.
        :returns: self
        """

        try:
            del(self._metas[data])
        except KeyError:
            pass

        return self

    def get_all_meta_data(self):
        """
        Return dictionary of meta data.
        """

        return self._metas

    @defer.inlineCallbacks
    def store(self, w=None, dw=None):
        """
        Store the object in Riak. When this operation completes, the
        object could contain new metadata and possibly new data if Riak
        contains a newer version of the object according to the object's
        vector clock.

        :param w: Wait for this many partitions to respond
                  before returning to client.
        :param dw: Wait for this many partitions to confirm the
                   write before returning to client.

        :returns: deferred

        .. todo:: pass in 'returnbody' value as parameter.
        .. todo:: make q a parameter.
        """
        # Use defaults if not specified...
        w = self._bucket.get_w(w)
        dw = self._bucket.get_dw(w)

        # Construct the URL...
        params = {'returnbody': 'true', 'w': w, 'dw': dw}
        host, port, url = RiakUtils.build_rest_path(self._client, self._bucket,
                                                    self._key, None, params)

        # Construct the headers...
        headers = {'Accept': 'text/plain, */*; q=0.5',
                   'Content-Type': self.get_content_type(),
                   'X-Riak-ClientId': self._client.get_client_id()}

        # Add the vclock if it exists...
        if (self.vclock() != None):
            headers['X-Riak-Vclock'] = self.vclock()

        # Add the meta data
        for key in self._metas.keys():
            # Riak spec says to send with this case.
            headers['X-Riak-Meta-%s' % key] = self._metas[key]

        # Add the Links...
        headers['Link'] = ''
        for link in self._links:
            if headers['Link'] != '':
                headers['Link'] += ', '
            headers['Link'] += link._to_link_header(self._client)

        if (self._jsonize):
            content = json.dumps(self.get_data())
        else:
            content = self.get_data()

        # Run the operation.
        response = yield RiakUtils.http_request_deferred('PUT', host, port,
                                                         url,
                                                         headers,
                                                         content)
        self._populate(response, [200, 300])
        defer.returnValue(self)

    @defer.inlineCallbacks
    def reload(self, r=None):
        """
        Reload the object from Riak. When this operation completes, the
        object could contain new metadata and a new value, if the object
        was updated in Riak since it was last retrieved.

        :param r: Wait for this many partitions to respond before
                  returning to client.
        :returns: self -- via deferred
        """
        # Do the request...
        r = self._bucket.get_r(r)
        params = {'r': r}
        host, port, url = RiakUtils.build_rest_path(self._client,
                                self._bucket, self._key, None, params)
        response = yield RiakUtils.http_request_deferred('GET', host,
                                                          port, url)

        self._populate(response, [200, 300, 404])

        # If there are siblings, load the data for the first one by default...
        if (self.has_siblings()):
            obj = yield self.get_sibling(0)
            self.set_data(obj.get_data())
        defer.returnValue(self)

    @defer.inlineCallbacks
    def delete(self, dw=None):
        """
        Delete this object from Riak.

        :param dw: Wait until this many partitions have deleted
                   the object before responding.
        :returns: self -- via deferred
        """
        # Use defaults if not specified...
        dw = self._bucket.get_dw(dw)

        # Construct the URL...
        params = {'dw': dw}
        host, port, url = RiakUtils.build_rest_path(self._client,
                                    self._bucket, self._key, None, params)

        # Run the operation...
        response = yield RiakUtils.http_request_deferred('DELETE', host,
                                                         port, url)
        self._populate(response, [204, 404])
        defer.returnValue(self)

    def clear(self):
        """
        Reset this object.
        This is a local operation that clears the object,
        not the Riak stored version.
        :returns: self
        """
        self._headers = []
        self._links = []
        self._data = None
        self._metas = {}
        self._exists = False
        self._siblings = []
        return self

    def vclock(self):
        """
        Get the vclock of this object.
        @return string
        .. todo:: convert to property
        """
        if ('x-riak-vclock' in self._headers.keys()):
            return self._headers['x-riak-vclock']
        else:
            return None

    def _populate(self, response, expected_statuses):
        """
        Populate the object given the output of RiakUtils.http_request_deferred
        and a list of expected statuses.

        :param response: http response body plus status
        :param expected_statuses: allowed statuses for which there
                                  are known actions.
        :returns: self
        """
        self.clear()
        # If no response given, then return.
        if (response == None):
            return self
        # Update the object...
        self._headers = response[0]
        self._data = response[1]
        status = self.status()

        # Check if the server is down(status==0)
        if (status == 0):
            m = 'Could not contact Riak Server: http://'
            m += self._client._host + ':' + str(self._client._port) + '!'
            raise Exception(m)

        # Verify that we got one of the expected statuses.
        # Otherwise, raise an exception.
        if (not status in expected_statuses):
            m = 'Expected status %s, received %s.\n' % (str(expected_statuses),
                                                       str(status))
            # And interesting details are in the response.
            m += 'Body: %s' % str(response)
            raise Exception(m)

        # If 404(Not Found), then clear the object.
        if (status == 404):
            self.clear()
            return self

        # If we are here, then the object exists...
        self._exists = True

        # Parse the Meta data
        self._populate_metas()

        # Parse the link header...
        if 'link' in self._headers.keys():
            self._populate_links(self._headers['link'])

        # If 300(Siblings), then load the first sibling, and
        # store the rest.
        if (status == 300):
            siblings_data = self._data

            siblings = siblings_data.strip().split('\n')

            # Get rid of 'Siblings:' string.
            siblings.pop(0)

            self._siblings = siblings
            self._exists = True
            return self

        # Possibly json_decode...
        if (status == 200 and self._jsonize):
            self._data = json.loads(self._data)

        return self

    def _populate_metas(self):
        """
        Scan headers looking for x-riak-meta-
        """
        self._metas = {}
        for head in self._headers.keys():
            # Twisted lowercases headers.
            if 'x-riak-meta-' in head:
                data = self._headers[head]
                key = head.replace('x-riak-meta-', '')
                self._metas[key] = data

    def _populate_links(self, link_headers):
        """
        Parse out the links.

        :param link_headers: comma-delimited list of links
        :returns: self
        """
        # Twisted returns this as a list.
        for link_header in link_headers.strip().split(','):
            link_header = link_header.strip()
            matches = re.match(
                 "\<\/([^\/]+)\/([^\/]+)\/([^\/]+)\>; ?riaktag=\"([^\']+)\"",
                 link_header)
            if (matches != None):
                link = RiakLink(matches.group(2), matches.group(3),
                                matches.group(4))
                self._links.append(link)

        return self

    def has_siblings(self):
        """
        Return True if this object has siblings.

        """
        return(self.get_sibling_count() > 0)

    def get_sibling_count(self):
        """
        Get the number of siblings that this object contains.

        """
        return len(self._siblings)

    @defer.inlineCallbacks
    def get_sibling(self, i, r=None):
        """
        Retrieve a sibling by sibling number.

        :param i: sibling number
        :param r: R-Value. Wait until this many particitions have responded.
        :returns: RiakObject

        """
        # Use defaults if not specified.
        r = self._bucket.get_r(r)

        # Run the request...
        vtag = self._siblings[i]
        params = {'r': r, 'vtag': vtag}
        host, port, url = RiakUtils.build_rest_path(self._client,
                                    self._bucket, self._key, None, params)
        response = yield RiakUtils.http_request_deferred('GET', host,
                                                         port, url)

        # Respond with a new object...
        obj = RiakObject(self._client, self._bucket, self._key)
        obj._jsonize = self._jsonize
        obj._populate(response, [200])
        defer.returnValue(obj)

    @defer.inlineCallbacks
    def get_siblings(self, r=None):
        """
        Retrieve an array of siblings.

        :param r: R-Value. Wait until this many particitions have responded.
        :returns: array of RiakObject -- via deferred
        """
        a = []
        for i in range(self.get_sibling_count()):
            result = yield self.get_sibling(i, r)
            a.append(result)
        defer.returnValue(a)

    def add(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.add()

        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self._client)
        mr.add(self._bucket._name, self._key)
        return apply(mr.add, args)

    def link(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.link()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self._client)
        mr.add(self._bucket._name, self._key)
        return apply(mr.link, args)

    def map(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.map()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self._client)
        mr.add(self._bucket._name, self._key)
        return apply(mr.map, args)

    def reduce(self, *args):
        """
        Start assembling a Map/Reduce operation.
        see RiakMapReduce.reduce()
        :returns: RiakMapReduce
        """
        mr = RiakMapReduce(self._client)
        mr.add(self._bucket._name, self._key)

        return apply(mr.reduce, args)


class RiakUtils(object):
    """
    Utility functions used by Riak library.
    """
    def __init__(self):
        return None

    @classmethod
    def get_value(cls, key, array, default_value):
        """
        Overkill for array.get(key, default_value).
        Likely due to porting from another language.
        """
        if (key in array):
            return array[key]
        else:
            return default_value

    @classmethod
    def build_rest_path(cls, client,
                        bucket=None, key=None, spec=None, params=None):
        """
        Given a RiakClient, RiakBucket, Key, LinkSpec, and Params,
        construct and return a URL.
        """
        # Build 'http://hostname:port/prefix/bucket'
        path = ''
        path += '/' + client._prefix

        # Add '.../bucket'
        if bucket:
            path += '/' + urllib.quote_plus(bucket._name)

        # Add '.../key'
        if bucket and key:
            path += '/' + urllib.quote_plus(key)

        # Add query parameters.
        if (params != None):
            s = ''
            for key in params.keys():
                if (s != ''):
                    s += '&'
                s += (urllib.quote_plus(key) + '=' +
                      urllib.quote_plus(str(params[key])))
            path += '?' + s

        # Return.
        return client._host, client._port, path

    @classmethod
    def http_request_deferred(cls, method, host, port, path,
                              headers=None, obj=''):
        """
        Given a Method, URL, Headers, and Body, perform an HTTP request,
        and return deferred.
        :returns: deferred
        """
        if headers == None:
            headers = {}

        return getPageWithHeaders(contextFactory=None,
                                  scheme='http',
                                  host=host,
                                  method=method,
                                  port=port,
                                  path=path,
                                  headers=headers,
                                  postdata=obj,
                                  timeout=20)

    @classmethod
    def build_headers(cls, headers):
        """
        Build up the header string.
        """
        headers1 = []
        for key in headers.keys():
            headers1.append('%s: %s' % (key, headers[key]))
        return headers1

    @classmethod
    def parse_http_headers(cls, headers):
        """
        Parse an HTTP Header string into dictionary of response headers.
        """
        result = {}
        fields = headers.split("\n")
        for field in fields:
            matches = re.match("([^:]+):(.+)", field)
            if (matches == None):
                continue
            key = matches.group(1).lower()
            value = matches.group(2).strip()
            if (key in result.keys()):
                if  isinstance(result[key], list):
                    result[key].append(value)
                else:
                    result[key] = [result[key]].append(value)
            else:
                result[key] = value
        return result


if __name__ == "__main__":
    pass
