#!/usr/bin/env python

# Copyright (c) 2011 Ben Croston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import hashlib
from threading import Thread
import time
from wsgiref import simple_server
import platform
import urllib

try:
    urllib.urlopen('http://www.wyre-it.co.uk/')
    NO_INTERNET = False
except IOError:
    NO_INTERNET = True

##### server vvv #####
class api(object):
    def mymethod(self):
        return 'wibbler woz ere'

    def echo(self, mystring):
        return 'ECHO: ' + mystring

    def raiseexception(self):
        dividebyzeroerror = 1/0

    def returnnothing(self):
        pass

def myauth(username, password, useragent=None):
    return username == 'testuser' and \
           hashlib.md5('s3cr3t').hexdigest() == password and \
           useragent == 'AuthRPC_unittest'

def make_server():
    from server import AuthRPCApp
    class myhandler(simple_server.WSGIRequestHandler):
        def log_request(self, *a, **b):
            pass # do not output log messages
    application = AuthRPCApp(api(), auth=myauth)
    return simple_server.make_server('localhost', 1337, application, handler_class=myhandler)
##### server ^^^ #####

##### client vvv #####
class AuthTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, UnauthorisedException
        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='s3cr3t',
                                  user_agent='InternetExploiter')
        with self.assertRaises(UnauthorisedException):
            self.client.api.mymethod()

        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='wrongpassword',
                                  user_agent='AuthRPC_unittest')
        with self.assertRaises(UnauthorisedException):
            self.client.api.mymethod()

        self.client = ServerProxy('http://localhost:1337/',
                                  username='wronguser',
                                  password='s3cr3t',
                                  user_agent='AuthRPC_unittest')
        with self.assertRaises(UnauthorisedException):
            self.client.api.mymethod()


@unittest.skipIf(NO_INTERNET, 'http://www.wyre-it.co.uk/ not contactable')
class NotFoundTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, NotFoundException
        self.client = ServerProxy('http://www.wyre-it.co.uk/this_should_generate_404.txt')
        with self.assertRaises(NotFoundException):
            self.client.api.mymethod()

class NetworkSocketTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, NetworkSocketException
        self.client = ServerProxy('http://localhost:666/')
        with self.assertRaises(NetworkSocketException):
            self.client.api.mymethod()

class AuthRPCTests(unittest.TestCase):
    def setUp(self):
        from client import ServerProxy
        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='s3cr3t',
                                  user_agent='AuthRPC_unittest')

class IgnoreClassNameTest(AuthRPCTests):
    def runTest(self):
        self.assertEqual(self.client.api.mymethod(),self.client.mymethod())

class ExceptionTest(AuthRPCTests):
    def runTest(self):
        with self.assertRaises(Exception):
            self.client.raiseexception()

class BadRequestTest(AuthRPCTests):
    def runTest(self):
        from client import BadRequestException
        with self.assertRaises(BadRequestException):
            self.client.FunctionDoesNotExist()

class EchoTest(AuthRPCTests):
    def runTest(self):
        if platform.python_version().startswith('3'):
            POUND = '\u00A3'
        else:
            POUND = unicode('\u00A3')
        self.assertEqual(self.client.echo(POUND), 'ECHO: ' + POUND)
        self.assertEqual(self.client.echo('hello mum!'), 'ECHO: hello mum!')

class ReturnNothing(AuthRPCTests):
    def runTest(self):
        self.assertEqual(self.client.returnnothing(), None)
##### client ^^^ #####

finished = False
def suite():
    if platform.python_version().startswith('2'):
        # create server
        def test_wrapper():
            server = make_server()
            while not finished:
                server.handle_request()
        thread = Thread(target=test_wrapper)
        thread.start()
        time.sleep(0.1) # wait for server thread to start

    # tests are as client
    suite = unittest.TestSuite()
    suite.addTest(AuthTest())
    suite.addTest(NotFoundTest())
    suite.addTest(NetworkSocketTest())
    suite.addTest(IgnoreClassNameTest())
    suite.addTest(ExceptionTest())
    suite.addTest(BadRequestTest())
    suite.addTest(EchoTest())
    suite.addTest(ReturnNothing())
    return suite

if __name__ == '__main__':
    import sys
    if platform.python_version().startswith('2') and 'serve' in sys.argv:
        print 'Listening on port 1337 (Ctrl-C qo quit)...'
        server = make_server()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            sys.exit()

    unittest.TextTestRunner(verbosity=2).run(suite())
    finished = True

    # make a dummy request to get server thread out of loop
    try:
       import urllib
       urllib.urlopen('http://localhost:1337/')
    except:
       pass

