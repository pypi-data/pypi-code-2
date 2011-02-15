#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful resource handler."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

__all__ = ['Handler']

import sys
import os
from datetime import datetime
import mimetypes
import hashlib
import re
import cgi
import cgitb
import http.client
from .ZombieConfig import config, datadir
from .Executable import Executable


#cgitb.enable()


###
### TODO
###

### Pay attention to If-Modified-Since to allow return of 304 Not Modified
### Pay attention to If-None-Match to allow return of 304 Not Modified
### Pay attention to If-Unmodified-Since
### Pay attention to If-Modified-Since


CHUNK_SIZE = 256
FLUSHED = "Flushed"


class Handler:
    """Holds all the information necessary to handle a single resource dispatch.
    
    Properties
    ----------
    executable
        The Executable object for this handler. In rare cases no executable
        can be determined so this will return None.
    """
        
    @classmethod
    def initdispatch(cls, regex, allow, help):
        cls.regex = re.compile(regex)
        cls.allow = allow
        cls.help = help
        return cls

    @classmethod
    def match(cls, path):
        """Check to see if the path is recognized by the dispatch handler,
        if so then return a dictionary of recognized parts, otherwise
        return None."""
        ret = None
        mo = cls.regex.match(path)
        if mo != None:
            ret = mo.groupdict()
        return ret
    
    def __init__(self, req, urlargs):
        self.req = req
        self.urlargs = urlargs
        self.content = "Single"
        self.nocache = False
        self.__status = None
        self.headers = {}
        self.lines = []
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def startstamp(self):
        return self.req.server.stamp
    
    @property
    def startstamprfc850(self):
        return self.req.date_time_string()
        
    @property
    def datadir(self):
        return datadir()

    @property
    def executable(self, mediatype=None):
        if not hasattr(self, "_Handler__executable"):
            self.initexecutable()
        return self.__executable
            
    @property
    def accept(self):
        """Return an ordered set of media types that will be accepted."""
        if not hasattr(self, "acceptset"):
            astr = self.req.headers["Accept"]
            if astr is None:
                astr = "text/html"
            self.acceptset = self.__parseq(astr)
            self.acceptset.append(None)
        return self.acceptset
    
    @property
    def acceptlanguage(self):
        """Return an ordered set of languages that will be accepted."""
        if not hasattr(self, "acceptlangset"):
            astr = self.req.headers["Accept-Language"]
            if astr is None:
                astr = "en"
            self.acceptlangset = self.__parseq(astr)
            self.acceptlangset.append(None)
        return self.acceptlangset
    
    @property
    def acceptencoding(self):
        """Return an ordered set of langauges that will be accepted."""
        if not hasattr(self, "acceptencset"):
            astr = self.req.headers["Accept-Encoding"]
            if astr is None:
                astr = ""
            self.acceptencset = self.__parseq(astr)
            self.acceptencset.append(None)
        return self.acceptencset
    
    def __parseq(self, astr):
        qre = re.compile(r"([a-zA-Z*]+/[a-zA-Z*]+)(\s*;\s*q=(\d+(\.\d+))?)?")
        astr = astr.split(",")
        aset = ["DUMMY"]
        weight = [0.0]
        for a in astr:
            q = 1.0
            m = qre.match(a.strip())
            if m:
                a = m.group(1)
                if m.group(3):
                    q = float(m.group(3))
            for i, w in enumerate(weight):
                if q > w:
                    aset.insert(i, a)
                    weight.insert(i, q)
                    break
        return aset[:-1]
    
    def initexecutable(self, mediatype=None):
        """This will initialize the executable property with a given media
        type. Generally using the executable property directly will give
        correct results. This is really only used when POST of a new exectuable
        occurs."""
        if hasattr(self, "_Handler__executable"):
            raise AttributeError("Executable property is already initialized.")
        if 'execname' in self.urlargs:
            name = self.urlargs['execname']
        else:
            name = Executable.createname()            
        self.__executable = Executable.getcached(name, mediatype)        
        
    def serverurl(self, path):
        """Given a path to a resource create a full URL to that resource.
        
        Parameters
        ----------
        path
            The relative path on the server to the resource.
        
        Return
        ------
        The URL that can be given to this server to find the given resource.
        """
        return "http://{0}:{1}/{2}".format(
                self.req.server.server_name,
                self.req.server.server_port,
                path)
    
    def rfile_safe(self):
        return HttpServerFP(self.req)
    
    def multipart(self):
        ctype, pdict = cgi.parse_header(self.req.headers['Content-Type'])
        if ctype != 'multipart/form-data':
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
            return None
        fp = self.rfile_safe()
        fs = cgi.FieldStorage(fp=fp, headers=self.req.headers,
            environ={'REQUEST_METHOD':'POST'}, strict_parsing=True)
        return fs
    
    def readline(self):
        """Read a single line from the input stream in decoded format."""
        pass
        
    def writeline(self, line):
        """Write a single line of text to the output stream."""
        self.lines.append(line)
    
    def writelines(self, lines):
        """Write a string one line at a time to the output stream."""
        for l in lines.splitlines():
            self.writeline(l)
    
    def writefile(self, path):
        """Read and then write the file from the given path to the output
        stream. This will write all the headers before the file. If there is
        an error reading the file then the appropriate HTTP error code will
        be sent.
        
        This is meant for static files. Dynamic files should use writeline
        or writelines to operate.
        
        Parameters
        ----------
        path
            The normalized path to the file.
        """
        if os.path.isfile(path):
            mediatype, enc = mimetypes.guess_type(path)
            self.writefp(open(path, "rb"), mediatype=mediatype, enc=enc)
        else:
            self.error(http.client.NOT_FOUND)
    
    def writefp(self, fp, mediatype="text/plain", enc=None, chunked=None):
        """Read from the given file object and write the data to the output
        stream. If this is chunked then this will not return until the input
        file object is closed.
        
        Parameters
        ----------
        fp
            The file type object to read from.
        chunked
            If not ``None`` then the data should be sent in a chunked manner,
            and the value should be a function that returns a boolean value
            to indicate all data has been sent. The default is no chunked.
        """
        self.req.send_response(http.client.OK)
        self.req.send_header("Cache-Control", "public max-age={0}".format(self.req.server.maxagestatic))
        self.req.send_header("Last-Modified", self.req.date_time_string())
        if mediatype == None:
            self.req.send_header("Content-Type", "application/octet-stream")
        else:
            if mediatype in ["text/plain", "text/html"]:
                mediatype = "{0};UTF-8".format(mediatype)
            self.req.send_header("Content-Type", mediatype)
        if enc != None:
            self.req.send_header("Content-Encoding", enc)
        
        if chunked is not None:            
            self.__etag_init()
            self.content = "Chunked"
            self.req.send_header("Transfer-Encoding", "chunked")
            self.req.end_headers()
            length = 0
            done = False
            while not done:
                data = fp.read(CHUNK_SIZE)
                while not data and not done:
                    data = fp.read(CHUNK_SIZE)
                    done = chunked()
                if data:
                    datalen = len(data)
                    length = length + datalen
                    self.__etag_feed(data)
                    self.req.wfile.write("{0:x}".format(datalen).encode("UTF-8"))
                    self.req.wfile.write(os.linesep.encode("UTF-8"))
                    if isinstance(data, str):
                        self.req.wfile.write(data.encode("UTF-8"))
                    elif isinstance(data, bytes):
                        self.req.wfile.write(data)
                    self.req.wfile.write(os.linesep.encode("UTF-8"))
            self.req.wfile.write(b"0")
            self.req.wfile.write(os.linesep.encode("UTF-8"))
            self.req.send_header("Cache-Control", "public max-age={0}".format(self.req.server.maxagedynamic))
            self.req.send_header("ETag", self.__etag_value())
            self.req.wfile.write(os.linesep.encode("UTF-8"))
            self.content = FLUSHED
        else:
            data = fp.read()
            self.req.send_header("ETag", self.etag(data))
            self.req.send_header("Content-Length", len(data))
            self.req.end_headers()
            self.req.wfile.write(data)
            self.content = FLUSHED

    
    def error(self, code, message=None):
        self.req.send_error(code, message=message)
        self.content = FLUSHED
        
    def flush(self):
        """Flush the headers if they have not been written and all the lines
        that have been written to the http output stream."""
        
        if self.content == FLUSHED:
            return
        
        self.lines.append("")
        buf = os.linesep.join(self.lines).encode("UTF-8")
        self.lines = []
        
        if not self.nocache:
            if "Cache-Control" not in self.headers:
                self.headers["Cache-Control"] = "public max-age={0}".format(self.req.server.maxagedynamic)
            
            if "ETag" not in self.headers:
                self.headers["ETag"] = self.etag(buf)
                
        if self.content in ["Headers", "Single", "Chunked"]:
            self.req.send_response(self.status)
            for k in self.headers:
                self.req.send_header(k, self.headers[k])
                
        if self.content == "Headers":
            self.req.end_headers()
            self.content = FLUSHED
        elif self.content == "Single":
            self.req.send_header("Content-Length", len(buf))
            self.req.end_headers()
            self.req.wfile.write(buf)
            self.content = FLUSHED
        elif self.content == "Chunked":
            pass
    
    def etag(self, data):
        """Build an ETag representation for the data associated with the given
        name."""
        self.__etag_init()
        self.__etag_feed(data)
        return self.__etag_value()
    
    def __etag_init(self):
        self.__etag = hashlib.md5()
    
    def __etag_feed(self, data):
        if isinstance(data, str):
            self.__etag.update(data.encode("UTF-8"))
        elif isinstance(data, bytes):
            self.__etag.update(data)
        else:
            self.__etag.update(str(data).encode("UTF-8"))
    
    def __etag_value(self):
        return self.__etag.hexdigest()
    
    def __getitem__(self, key):
        return self.headers[key]
    
    def __setitem__(self, key, value):
        self.headers[key] = value
    
    

class HttpServerFP():
    """This will wrap the http.server request rfile so an EOF will be returned
    when reading from the rfile. That way the Content-Length is always handled
    correctly. This will also convert the binary stream into a character stream.
    """
    def __init__(self, req):
        self.req = req
        self.clen = int(self.req.headers['Content-Length'])
        self.rfile = self.req.rfile
    
    def read(self, size=-1):
        if size < 0:
            size = self.clen
        if size > self.clen:
            size = self.clen
        ret = ''
        if size > 0:
            ret = self.rfile.read(size)
            self.clen = self.clen - len(ret)
            ret = str(ret, 'UTF-8')
        return ret
