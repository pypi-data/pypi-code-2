# The MIT License
# 
# Copyright (c) 2007 Suncoast Partnership 
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

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class DuplicateXMLDocumentError(Exception):
    def __init__(self, *args):
        message = "Error %s: \nIndicates: %s\nIn Location: %s" % (args[0], args[1], args[2])
        print message
        self.message = message

class UndefinedXMLWriter(Exception):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[0], args[1], args[2])

class DatabaseAuthenticationError(Exception):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[0], args[1], args[2])
        
class SoftwareCompatibilityError(Exception):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
        
class XSDError(Exception):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
        
class dbLayerNotFoundError(Exception):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])

class VPNFailure(Error):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
        
class FTPUploadFailureError(Error):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
        
class KeyboardInterrupt(Error):
    def __init__(self, *args):
        print "Intercepted Keyboard Interupt"
        
class fileNotFoundError(Error):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])

class dataFormatError(Error):
    def __init__(self, *args):
            print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])

class InvalidSSNError(Error):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
        
class ethnicityPickNotFound(Error):
    def __init__(self, *args):
        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
        
class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message