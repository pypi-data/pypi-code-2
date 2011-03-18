#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os

from apiclient.anyjson import simplejson
from apiclient.discovery import build
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import login_required

DIR = simplejson.loads(file(os.path.join(os.path.dirname(__file__), 'directory.json'), 'r').read())['items']
DIR = [ item for item in DIR if item['name'] != 'latitude' ]

class MainHandler(webapp.RequestHandler):

  def get(self):
    logging.info(DIR)
    path = os.path.join(os.path.dirname(__file__), 'welcome.html')
    self.response.out.write(
        template.render(
            path, {'directory': DIR}))

PLATFORMS = [
    {
      'name': 'cmdline',
      'description': 'Command-line',
    },
    {
      'name': 'appengine',
      'description': 'Google App Engine',
    },
    {
      'name': 'django',
      'description': 'Django',
    },
    ]

class ApiHandler(webapp.RequestHandler):

  def get(self, service_name):
    logging.info(PLATFORMS)
    path = os.path.join(os.path.dirname(__file__), 'service.html')
    self.response.out.write(
        template.render(
            path, {'platforms': PLATFORMS}))
    pass

class DevKeyHandler(webapp.RequestHandler):

  def get(self, service_name, platform):
    logging.info(PLATFORMS)
    path = os.path.join(os.path.dirname(__file__), 'devkey.html')
    self.response.out.write(
        template.render(
            path, {'platforms': PLATFORMS}))

VALID_PLATFORMS = ['cmdline']

class CodeHandler(webapp.RequestHandler):

  def get(self, service_name, platform):
    logging.info(PLATFORMS)
    if platform in VALID_PLATFORMS:
      path = os.path.join(os.path.dirname(__file__), platform + '.html')
      name, version = service_name.rsplit("-", 1)
      self.response.out.write(
          template.render(
              path, {
                'platform': platform,
                'service_name': name,
                'service_version': version,
                'developerKey': self.request.get('developerKey'),
                'client_id': self.request.get('client_id'),
                'client_secret': self.request.get('client_secret'),
                }))

def main():
  application = webapp.WSGIApplication(
      [
      (r'/', MainHandler),
      (r'/([^\/]+)/', ApiHandler),
      (r'/([^\/]+)/([^\/]+)/', DevKeyHandler),
      (r'/([^\/]+)/([^\/]+)/final', CodeHandler),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
