#!/usr/bin/env python

###################################################################
##
##   http_file_server.py - This script allows to export via an HTTP
##   server created on the fly, the content of any local file.
##
##
##   Copyright (C) 2010  INAF-IASF Milano
##
##   This program is free software; you can redistribute it and/or
##   modify it under the terms of the GNU General Public License
##   as published by the Free Software Foundation; either version 2
##   of the License, or (at your option) any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.
##
##   You should have received a copy of the GNU General Public License
##   along with this program; if not, write to the Free Software
##   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##   MA 02110-1301, USA.
##
##   Authors:
##
##   Luigi Paioro
##   INAF - Istituto Nazionale di Astrofisica
##
##   IASF Milano
##   Via Bassini 15, I-20133 Milano, Italy
##   E-mail: luigi at iasf-milano.inaf.it
##   Site  : http://www.iasf-milano.inaf.it/
##
################################################################################
##
##   Automatic keywords:
##   $Date: 2011-03-04 10:09:03 +0100 (Fri, 04 Mar 2011) $
##   $Revision: 665 $
##   $Author: luigi $
##   $HeadURL: http://cosmos.iasf-milano.inaf.it/svn/fase/trunk/framework/samp/python/utils/http_file_server.py $
##   $Id: http_file_server.py 665 2011-03-04 09:09:03Z luigi $
##
################################################################################


import os
import sys
import time

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

class HttpFileServerRequestHandler(BaseHTTPRequestHandler):
  
  def do_GET(self):
    self.send_response(200, 'OK')
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    f = None
    try:
      f = open(server.file_to_serve, "r")
      self.wfile.write(f.read())
    except:
      pass
    finally:
      try:
        f.close()
      except:
        pass

class HttpFileServer(ThreadingMixIn, HTTPServer):
  
  def __init__(self, server_address, file_to_serve=None, bind_and_activate=True):
    HTTPServer.__init__(self, server_address, HttpFileServerRequestHandler, \
                        bind_and_activate)
    self.file_to_serve = file_to_serve
    
if __name__ == "__main__":
  
  import signal
  from optparse import OptionParser, OptionGroup
  
  parser = OptionParser(usage="%prog file [options]")

  parser.disable_interspersed_args()
  
  parser.add_option("-d", "--addr", dest="addr", metavar="ADDR",
                    help="listening address (or IP).")

  parser.add_option("-p", "--port", dest="port", metavar="PORT", type="int",
                    help="listening port number.")
  
  parser.set_defaults(addr="")
  parser.set_defaults(port=8080)
  
  (options, args) = parser.parse_args()
  
  if not args:
    print "Please provide a file to be served."
    sys.exit(1)
  
  try:
    
    keep_alive = True
  
    def handler(signum, frame):
      keep_alive = False
  
    signal.signal(signal.SIGINT, handler)
    
    server = HttpFileServer((options.addr, options.port), \
                            args[0])
    
    while keep_alive:
      server.handle_request()
      time.sleep(0.001)
    
  except:
    
    keep_alive = False
