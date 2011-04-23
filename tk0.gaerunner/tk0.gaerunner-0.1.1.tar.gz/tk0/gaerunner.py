#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
# Copyright 2010 tk0miya <i.tk0miya at gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""A python script launcher for Google App Engine.
gaerunner is wrapping some APIs using remote API calls.

Usage:
  gaerunner.py [-s HOSTNAME] APPID [PATH] SCRIPT_PATH
"""
from google.appengine.tools import os_compat

import getpass
import optparse
import os
import sys
import re

import google.appengine
DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(google.appengine.__file__)))

sys.path[0:0] = [
  os.path.join(DIR_PATH, 'lib', 'antlr3'),
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'fancy_urllib'),
  os.path.join(DIR_PATH, 'lib', 'ipaddr'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
]

from google.appengine.ext.remote_api import remote_api_stub

from google.appengine.api import datastore
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import search


DEFAULT_PATH = '/remote_api'


def auth_func():
  return (raw_input('Email: '), getpass.getpass('Password: '))


def main():
  parser = optparse.OptionParser()
  parser.add_option('-s', '--server', dest='server',
                    help='The hostname your app is deployed on. '
                         'Defaults to <app_id>.appspot.com.')
  parser.add_option('--secure', dest='secure', action="store_true",
                    default=False, help='Use HTTPS when communicating '
                                        'with the server.')
  (options, args) = parser.parse_args()

  if not args or len(args) > 3:
    print >> sys.stderr, __doc__
    if len(args) > 3:
      print >> sys.stderr, 'Unexpected arguments: %s' % args[2:]
    sys.exit(1)

  script_path = args.pop()
  if not os.path.isfile(script_path):
    print >> sys.stderr, "Script was not found: %s" % script_path
    sys.exit(1)

  appid = args[0]
  if len(args) == 2:
    path = args[1]
  else:
    path = DEFAULT_PATH

  remote_api_stub.ConfigureRemoteApi(appid, path, auth_func,
                                     servername=options.server,
                                     save_cookies=True, secure=options.secure)
  remote_api_stub.MaybeInvokeAuthentication()

  execfile(script_path, globals())


if __name__ == '__main__':
  main()
