# -*- coding: utf-8 -*-

import sys
import re
from optparse import OptionParser

VERSION = "11.02.01"

def get_option_parser():
  def version(*args):
    print VERSION
    sys.exit(0)
  
  parser = OptionParser()
  parser.add_option("-v", "--version", help="print software version and exit",
                    callback=version, action="callback")
  
  return parser

class UsageError(Exception):
  pass

class HTTPMessage:
  LINESEP = re.compile(r"\r\n|\n|\r")
  
  def __init__(self):
    self.headers = {}
    self.body = ""
  
  def add_content_length_header(self):
    if self.body and "Content-Length" not in self.headers:
        self.headers["Content-Length"] = str(len(self.body))
  
  def set_header_from_string(self, string):
    name, value = string.split(":", 1)
    self.headers[name.strip()] = value.strip()
  
  def parse_body(self, line_gen):
    self.body = "".join(line_gen)
  
  @property
  def head(self):
    return self.render_first_line() + "\r\n" + \
           "\r\n".join("%s: %s" % item for item in self.headers.items()) + \
           "\r\n"
  
  def __str__(self):
    lines = [self.render_first_line()]
    
    for name, value in self.headers.items():
      lines.append("%s: %s" % (name, value))
    
    return "\r\n".join(lines) + "\r\n\r\n" + self.body
  
  @classmethod
  def parse(cls, string):
    search = HTTPMessage.LINESEP.search
    
    lines = (line for line in HTTPMessage.LINESEP.split(string))
    message = cls()
    
    m1 = search(string)
    end = m1.start()
    message.parse_first_line(string[0:end].lstrip())
    
    m2 = search(string, m1.end())
    while m1.end() != m2.start():
      message.set_header_from_string(string[m1.end():m2.start()])
      m1 = m2
      m2 = search(string, m1.end())
    
    message.body = string[m2.end():]
    
    return message
  
  @classmethod
  def read(cls, stream):
    return cls.parse(stream.read())

class HTTPRequest(HTTPMessage):
  REQ_LINE = re.compile(r"^(?P<method>\w+) +(?P<uri>[^ ]+) +HTTP/(?P<version>\d+\.\d+)$")
  
  def __init__(self, uri="/", method="GET", version="1.0"):
    HTTPMessage.__init__(self)
    
    self.uri = uri
    self.method = method
    self.version = version
    
    self.port = 80
  
  def render_first_line(self):
    return "%s %s HTTP/%s" % (self.method, self.uri, self.version)
  
  def parse_first_line(self, line):
    m = HTTPRequest.REQ_LINE.match(line)
    
    if m is None:
      raise ValueError("Cannot parse HTTP request")
    
    d = m.groupdict()
    self.uri = d["uri"]
    self.method = d["method"]
    self.version = d["version"]

class HTTPResponse(HTTPMessage):
  STATUS_LINE = re.compile(r"^HTTP/(?P<version>\d+\.\d+) +(?P<code>\d+) +(?P<reason>.+)$")
  
  def __init__(self):
    HTTPMessage.__init__(self)
    
    self.code = None
    self.text = None
    self.version = None
  
  def parse_first_line(self, line):
    m = HTTPResponse.STATUS_LINE.match(line)
    if m is None:
      raise ValueError("Cannot parse HTTP response")
    
    d = m.groupdict()
    self.code = int(d["code"])
    self.version = d["version"]
    self.reason = d["reason"]
  
  def render_first_line(self):
    return "HTTP/%s %d %s" % (self.version, self.code, self.reason)
  
  def decoded_body(self):
    # Is Transfer-Encoding "chunked" ?
    if self.headers.get("Transfer-Encoding", None) == "chunked":
      # Unchunk...
      return self.body
    else:
      return self.body
