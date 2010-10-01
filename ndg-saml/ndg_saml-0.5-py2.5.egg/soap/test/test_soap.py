#!/usr/bin/env python
"""SOAP module unit test module

NERC DataGrid Project
"""
__author__ = "P J Kershaw"
__date__ = "24/07/09"
__copyright__ = "(C) 2009 Science and Technology Facilities Council"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id: test_soap.py 7134 2010-06-30 13:49:40Z pjkersha $"
import logging
logging.basicConfig(level=logging.DEBUG)

import unittest
import socket
from cStringIO import StringIO
from os import path
import paste.fixture
from urllib2 import HTTPHandler, URLError

from ndg.soap.etree import SOAPEnvelope
from ndg.soap.client import UrlLib2SOAPClient, UrlLib2SOAPRequest
from ndg.soap.test import PasteDeployAppServer


class SOAPBindingMiddleware(object):
    """Simple WSGI interface for SOAP service"""
        
    def __call__(self, environ, start_response):
        requestFile = environ['wsgi.input']
        
        print("Server received request from client:\n\n%s" % 
              requestFile.read())
        
        soapResponse = SOAPEnvelope()
        soapResponse.create()
        
        response = soapResponse.serialize()
        start_response("200 OK",
                       [('Content-length', str(len(response))),
                        ('Content-type', 'text/xml')])
        return [response]
    
    
class SOAPTestCase(unittest.TestCase):
    SOAP_SERVICE_PORTNUM = 10080
    ENDPOINT = 'http://localhost:%d/soap' % SOAP_SERVICE_PORTNUM
    THIS_DIR = path.abspath(path.dirname(__file__))
    
    def __init__(self, *args, **kwargs):
        """Use paste.fixture to test client/server SOAP interface"""
        self.services = []
        self.disableServiceStartup = False

        wsgiApp = SOAPBindingMiddleware()
        self.app = paste.fixture.TestApp(wsgiApp)
         
        super(SOAPTestCase, self).__init__(*args, **kwargs)
        
    def test01Envelope(self):
        envelope = SOAPEnvelope()
        envelope.create()
        soap = envelope.serialize()
        
        self.assert_(len(soap) > 0)
        self.assert_("Envelope" in soap)
        self.assert_("Body" in soap)
        self.assert_("Header" in soap)
        
        print(envelope.prettyPrint())
        stream = StringIO()
        stream.write(soap)
        stream.seek(0)
        
        envelope2 = SOAPEnvelope()
        envelope2.parse(stream)
        soap2 = envelope2.serialize()
        self.assert_(soap2 == soap)

    def test02SendRequest(self):
        requestEnvelope = SOAPEnvelope()
        requestEnvelope.create()
        request = requestEnvelope.serialize()
        
        response = self.app.post('/my-soap-endpoint', 
                                 params=request, 
                                 status=200)
        print(response.headers)
        print(response.status)
        print(response.body)

    def test03Urllib2Client(self):
        
        # Paster based service is threaded from this call
        self.addService(app=SOAPBindingMiddleware(), 
                        port=SOAPTestCase.SOAP_SERVICE_PORTNUM)
        
        client = UrlLib2SOAPClient()
        
        # ElementTree based envelope class
        client.responseEnvelopeClass = SOAPEnvelope
        
        request = UrlLib2SOAPRequest()
        request.url = SOAPTestCase.ENDPOINT
        request.envelope = SOAPEnvelope()
        request.envelope.create()
        
        client.openerDirector.add_handler(HTTPHandler())
        try:
            response = client.send(request)
        except URLError, e:
            self.fail("soap_server.py must be running for this test")
        
        print("Response from server:\n\n%s" % response.envelope.serialize())
        
    def addService(self, *arg, **kw):
        """Utility for setting up threads to run Paste HTTP based services with
        unit tests
        
        @param arg: tuple contains ini file path setting for the service
        @type arg: tuple
        @param kw: keywords including "port" - port number to run the service 
        from
        @type kw: dict
        """
        if self.disableServiceStartup:
            return
        
        try:
            self.services.append(PasteDeployAppServer(*arg, **kw))
            self.services[-1].startThread()
            
        except socket.error:
            pass

    def __del__(self):
        """Stop any services started with the addService method and clean up
        the CA directory following the trust roots call
        """
        if hasattr(self, 'services'):
            for service in self.services:
                service.terminateThread()


if __name__ == "__main__":
    unittest.main()