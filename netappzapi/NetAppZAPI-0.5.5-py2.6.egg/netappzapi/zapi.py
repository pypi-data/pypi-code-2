#!/usr/bin/python

"""
A set of twisted classes that provide an implementation of the
NetApp ZAPI protocol so you can administer your Filers from Python.
"""

import os
import sys
import re
import base64
import binascii
import random

from twisted.internet import defer, reactor
from twisted.internet import protocol, ssl
from twisted.python import log as tlog
from twisted.web import http, error, client

import util

from lxml import etree
import logging
import debug
log = logging.getLogger('zapi')

class ZAPIProtocol(client.HTTPPageGetter):
    """
    A renamed HTTPPageGetter, used for talking ZAPI to NetApp filers.
    """
    # Ensure we get connection failure errors
    quietLoss = False

    def connectionMade(self):
        """
        Custom method for sending a ZAPI request to a filer in the
        format that it expects.
        """
        method = getattr(self.factory, 'method', 'GET')
        self.sendCommand(method, self.factory.path)
        self.sendHeader('Host', self.factory.headers.get("host", self.factory.host))
        self.sendHeader('User-Agent', self.factory.agent)
        data = getattr(self.factory, 'postdata', None)
        if data is not None:
            self.sendHeader("Content-Length", str(len(data)))

        # We may need to authenticate. Filers use Basic authentication.
        if self.factory.user:
            auth = base64.encodestring('%s:%s' % (
                self.factory.user, self.factory.password))
            self.sendHeader('Authorization', 'Basic %s' % auth)
            
        if self.factory.cookies:
            l=[]
            for cookie, cookval in self.factory.cookies.items():  
                l.append('%s=%s' % (cookie, cookval))
            self.sendHeader('Cookie', '; '.join(l))
            pass

        self.endHeaders()
        self.headers = {}
        
        if data is not None:
            self.transport.write(data)

    def endHeaders(self):
        pass

class ZAPIResult:
    """
    An encapsulation of a ZAPI result.
    """
    zapi_namespace_id = "http://www.netapp.com/filer/admin"

    re_xmlns = re.compile("(?P<start>.*)\s+xmlns='(?P<namespace>.*)'(?P<end>.*)", re.S) 
    #re_xmlns = re.compile(r"(.*)xmlns='http://www.netapp.com/filer/admin'(.*)", re.M)
    
    def __init__(self, xmlstring):

        self.status = None
        self.errno = None
        self.reason = None

        self.rawxml = xmlstring

        # strip off the xmlns bit before parsing
        # This is done because lxml puts a namespace string at the front of
        # every tag, and doesn't appear to support a default namespace.
        m = self.re_xmlns.match(xmlstring)
        if m:
            xmlstring = '%s%s' % (m.group('start'), m.group('end') )
            pass
        
        self.xmlstring = xmlstring

        log.debug("xmlstring is: %s", self.xmlstring)
        
        parser = etree.XMLParser(ns_clean=True)

        self.tree = etree.fromstring(xmlstring, parser)
        
        self.results = self.tree.find('results')
        self.status = self.results.attrib['status']
        log.debug("zapi status: %s", self.status)
        if self.status == 'failed':
            self.errno = int(self.results.attrib['errno'])
            self.reason = self.results.attrib['reason']

    def __repr__(self):
        return '<%s: %s (%s: %s), %s>' % (self.__class__, self.status, self.errno, self.reason, etree.tostring(self.tree) )

class ZAPIFactory(client.HTTPClientFactory):
    """
    A renamed HTTPClientFactory
    """
    protocol = ZAPIProtocol

    def __init__(self, url, method='GET', postdata=None, headers=None,
                 agent="eigenmagic NetAppZAPI", timeout=300, cookies=None,
                 followRedirect=1):
        """
        Custom init method to override timeout and agent string
        """
        client.HTTPClientFactory.__init__(self, url, method, postdata, headers,
                 agent, timeout, cookies, followRedirect)

class GetFileException(Exception):
    """
    Exception raised when get_file() fails.
    """

class PutFileException(Exception):
    """
    Exception raised when put_file() fails.
    """

class ZAPITool:
    """
    A ZAPITool abstracts the ZAPIFactory and ZAPIProtocol to
    provide a useful object that can handle comms to multiple
    remote NetApp devices.
    """
    zapi_request_header = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE netapp SYSTEM 'file:/etc/netapp_filer.dtd'>
<netapp xmlns='http://www.netapp.com/filer/admin' version='1.3'>
"""
    zapi_request_footer = r"</netapp>"
    zapi_request_path = "/servlets/netapp.servlets.admin.XMLrequest_filer"

    def __init__(self, delay=0):
        # Key up a series of zapi requests that are outstanding
        # so we can parse the results before returning them via .callback()
        self.zapi_defer = {}

        self.delay = delay

        self.request_id = long(random.randint(1,0x7FFFFFFF))

    def increment_request_id(self):
        """
        Get a new request ID
        """
        self.request_id += 1
        self.request_id %= 0x100000000L
        
        return self.request_id

    def zapi_request(self, device, command, username='root', password='netapp1', scheme='https', realm='Administrator', timeout=30):
        """
        Issue a ZAPI request to a device.
        """
        log.debug("zapi user: %s", username)
        log.debug("zapi password: %s", password)
        log.debug("scheme: %s", scheme)
        log.debug("realm: %s", realm)
        full_command = "%s\r\n%s\r\n%s\r\n" % (self.zapi_request_header, command, self.zapi_request_footer)

        url = '%s://%s%s' % (scheme, device, self.zapi_request_path)

        log.debug("url: %s", url)
        log.debug("zapi command: %s", full_command)

        factory = ZAPIFactory(url, postdata=full_command, timeout=timeout)
        factory.user = username
        factory.password = password

        # Set up the callback chain for the request
        zapi_key = self.increment_request_id()
        self.zapi_defer[zapi_key] = defer.Deferred()
        #factory.deferred.addCallbacks(self.zapi_success, self.zapi_failure, callbackArgs=(zapi_key,), errbackArgs=(zapi_key,) )
        factory.deferred.addCallback(self.zapi_success, zapi_key)
        factory.deferred.addErrback(self.zapi_failure, zapi_key)

        # Connect to the device and issue command in a moment
        reactor.callLater(self.delay, self.do_connect, url, factory)
        
        return self.zapi_defer[zapi_key]

    def do_connect(self, url, factory):
        """
        Called after a delay, if one is set.
        """
        scheme, host, port, path = client._parse(url)
        if scheme == 'https':
            from twisted.internet import ssl
            contextFactory = ssl.ClientContextFactory()
            reactor.connectSSL(host, port, factory, contextFactory)
        else:
            reactor.connectTCP(host, port, factory)
            pass
    
    def zapi_success(self, result, zapi_key):
        try:
            result = self.parse_zapi_result(result)
            self.zapi_defer[zapi_key].callback(result)
        except Exception, e:
            self.zapi_defer[zapi_key].errback(e)

    def zapi_failure(self, failure, zapi_key):
        self.zapi_defer[zapi_key].errback(failure)

    def parse_zapi_result(self, resultxml):
        """
        Parse the zapi result XML tree
        """
        result = ZAPIResult(resultxml)
        return result

    def zapi_system_command(self, device, command, username='root', password='netapp1', scheme='https', realm='Administrator', timeout=30):
        """
        Run a commandline command via ZAPI.
        """
        argset = []
        args = command.split(' ')
        for arg in args:
            argset.append("<arg>%s</arg>" % arg)
            pass
        argset = ''.join(argset)
        command = "<system-cli><args>%s</args></system-cli>" % argset

        return self.zapi_request(device, command, username, password, scheme, realm, timeout)

#     @defer.inlineCallbacks
#     def get_file(self, device, filename, root='/vol/vol0', username='root', password='netapp1', scheme='https'):
#         """
#         Retrieve an arbitrary file from the filer
#         """
#         buffer_size = 1024 * 512
#         offset = 0

#         filename = os.path.join(root, filename.strip('/'))

#         # Fetch file one fragment at a time
#         fragments = []
#         frag_count = 0
#         while 1:
#             log.debug("getting fragment: %d", frag_count)
#             command = "<file-read-file><path>%s</path><length>%s</length><offset>%s</offset></file-read-file>" % (filename, buffer_size, offset)
#             results = yield self.zapi_request(device, command, username, password, scheme)

#             log.debug("got a part. checking status...")
#             if results.status == 'failed':
#                 raise GetFileException("Error fetching file '%s': %s" % (filename, results.reason))

#             result_dict = util.build_dict(results.results)
#             length = int(result_dict['length'])
#             #log.debug("file is %d bytes long", length)
#             if length > 0:
#                 data = binascii.a2b_hex(result_dict['data'])
#                 fragments.append(data)
#                 pass
            
#             if length != buffer_size:
#                 break

#             offset += length
#             pass

#         file = ''.join(fragments)
#         defer.returnValue( (results, file) )
#         pass
    
#     @defer.inlineCallbacks
#     def _put_file_broken(self, device, filename, data, root='/vol/vol0', offset=0, overwrite=True, username='root', password='netapp1', scheme='https'):
#         """
#         Put an arbitrary file onto the filer.
#         """
#         filename = os.path.join(root, filename.strip('/'))

#         send_data = binascii.b2a_hex(data)

#         # Send a file to the filer
#         command = "<file-write-file><path>%s</path><offset>%s</offset><data>%s</data><overwrite>%s</overwrite></file-read-file>" % (filename, offset, send_data, overwrite)
#         results = yield self.zapi_request(device, command, username, password, scheme)

#         if results.status == 'failed':
#             raise PutFileException("Error sending file '%s': %s" % (filename, results.reason))

#         defer.returnValue( results )
#         pass
#     pass

    def get_file(self, device, filename, root='/vol/vol0', username='root', password='netapp1', scheme='https'):
        """
        Retrieve an arbitrary file from the filer
        """
        buffer_size = 1024 * 512
        offset = 0

        filename = os.path.join(root, filename.strip('/'))

        # Fetch file one fragment at a time
        fragments = []
        frag_count = 0

        got_file_d = defer.Deferred()

        def got_part(results, offset):

            log.debug("got a part. checking status...")
            if results.status == 'failed':
                got_file_d.errback(GetFileException("Error fetching file '%s': %s" % (filename, results.reason)))

            result_dict = util.build_dict(results.results)
            length = int(result_dict['length'])
            #log.debug("file is %d bytes long", length)
            if length > 0:
                data = binascii.a2b_hex(result_dict['data'])
                fragments.append(data)
                pass
            
            if length != buffer_size:
                file = ''.join(fragments)
                got_file_d.callback( (results, file) )

            offset += length
            command = "<file-read-file><path>%s</path><length>%s</length><offset>%s</offset></file-read-file>" % (filename, buffer_size, offset)
            d = self.zapi_request(device, command, username, password, scheme)
            d.addCallback(got_part, offset)
            pass

        log.debug("getting fragment: %d", frag_count)
        command = "<file-read-file><path>%s</path><length>%s</length><offset>%s</offset></file-read-file>" % (filename, buffer_size, offset)
        d = self.zapi_request(device, command, username, password, scheme)
        d.addCallback(got_part, offset)
        return got_file_d
    
    def put_file(self, device, filename, data, root='/vol/vol0', offset=0, overwrite=True, username='root', password='netapp1', scheme='https'):
        """
        Put an arbitrary file onto the filer.
        """
        buffer_size = 1024 * 32
        filename = os.path.join(root, filename.strip('/'))

        bufferdata = data[:]

        file_sent_d = defer.Deferred()

        def got_result(results, bufferdata):
            if results.status == 'failed':
                file_sent_d.errback(PutFileException("Error sending file '%s': %s" % (filename, results.reason)))
                return
            
            # If no more data to send, trigger callback
            if len(bufferdata) == 0:
                file_sent_d.callback(results)
            else:
                d = send_data(bufferdata)
        
        def send_data(bufferdata):
            send_buf = bufferdata[:buffer_size]
            send_data = binascii.b2a_hex(send_buf)
            bufferdata = bufferdata[buffer_size:]
            # Send a file to the filer, always appending
            command = "<file-write-file><path>%s</path><offset>-1</offset><data>%s</data><overwrite>%s</overwrite></file-write-file>" % (filename, send_data, overwrite)
            
            d = self.zapi_request(device, command, username, password, scheme)
            d.addCallback(got_result, bufferdata)
            return d
        
        send_data(bufferdata)
        return file_sent_d
    pass
    
if __name__ == '__main__':

    # If you run this directly, the module provides a very simple
    # commandline interface to the filer, which runs system-cli
    # commands via ZAPI.
    # FIXME: Because of the way twisted works, exitcodes aren't
    # possible yet.
    #log.setLevel(logging.DEBUG)

    try:
        device_name = sys.argv[1]
        command = sys.argv[2]
        #command = ' '.join(sys.argv[2:])

        if len(sys.argv) > 2:
            username = sys.argv[3]
        else:
            username = 'root'

        if len(sys.argv) > 3:
            password = sys.argv[4]
        else:
            password = 'netapp1'
            
    except IndexError, e:
        log.error("Usage: netapp.py <device> <zapi_command> [<username>] [<password>]")
        raise

    log.debug("device: %s, command: %s", device_name, command)
    log.debug("username: %s, password: %s", username, password)
    zapi_scheme = 'https'

    zapitool = ZAPITool()
    d = zapitool.zapi_system_command(device_name, command, username, password)

    def got_result(result):
        log.debug("result is: %s", result)
        # Find the result output
        output = result.results.find('cli-output').text
        print output
        cli_errno = int(result.results.find('cli-result-value').text)
        #print "errno: %d" % cli_errno
        reactor.stop()
        
    def error(failure):
        log.error("error fetching page")
        tlog.err(failure)
        reactor.stop()

    d.addCallback(got_result)
    d.addErrback(error)

    reactor.run()
