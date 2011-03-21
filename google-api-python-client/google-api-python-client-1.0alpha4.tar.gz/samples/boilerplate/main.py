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

LANGUAGES = [
    {
      'name': 'python',
      'description': 'Python',
    },
    {
      'name': 'java',
      'description': 'Java',
    }
    ]

class Step0Handler(webapp.RequestHandler):

  def get(self):
    logging.info(DIR)
    path = os.path.join(os.path.dirname(__file__), 'templates', 'step0.html')
    self.response.out.write(
        template.render(
            path, {'languages': LANGUAGES}))

INSTALL = {
      'python': """
<p>If you already have <code>setuptools</code> installed then you
only need to run:</p>

<pre>$ easy_install google-api-python-client</pre>

<p>If you don't have <code>setuptools</code> installed, or if you want
the samples and documentation you can download the release package from
<a
href="http://code.google.com/p/google-api-python-client/downloads/">http://code.google.com/p/google-api-python-client/downloads/</a>.
After downloading and extracting all the files you can install by running:

<pre>$ python setup.py install</pre>

<p>See the project documentation for <a
href="http://code.google.com/p/google-api-python-client/wiki/Installation">more details on installation</a>.</p>

      """,
      'java': """
TBD
        """
    }

class Step05Handler(webapp.RequestHandler):

  def get(self, language):
    logging.info(DIR)
    path = os.path.join(os.path.dirname(__file__), 'templates', 'step0.5.html')
    self.response.out.write(
        template.render(
            path, {'install_instructions': INSTALL[language]}))

class Step1Handler(webapp.RequestHandler):

  def get(self, language):
    logging.info(DIR)
    path = os.path.join(os.path.dirname(__file__), 'templates', 'step1.html')
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

class Step2Handler(webapp.RequestHandler):

  def get(self, language, service_name):
    logging.info(PLATFORMS)
    path = os.path.join(os.path.dirname(__file__), 'templates', 'step2.html')
    self.response.out.write(
        template.render(
            path, {'platforms': PLATFORMS}))
    pass

class Step3Handler(webapp.RequestHandler):

  def get(self, language, service_name, platform):
    logging.info(PLATFORMS)
    path = os.path.join(os.path.dirname(__file__), 'templates', 'step3.html')
    self.response.out.write(
        template.render(
            path, {'platforms': PLATFORMS}))

VALID_PLATFORMS = ['cmdline']

class Step4Handler(webapp.RequestHandler):

  def get(self, language, service_name, platform):
    logging.info(PLATFORMS)
    if platform in VALID_PLATFORMS:
      path = os.path.join(os.path.dirname(__file__), 'templates', platform + '.html')
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
      (r'/', Step0Handler),
      (r'/([^\/]+)/installation/', Step05Handler),
      (r'/([^\/]+)/', Step1Handler),
      (r'/([^\/]+)/([^\/]+)/', Step2Handler),
      (r'/([^\/]+)/([^\/]+)/([^\/]+)/', Step3Handler),
      (r'/([^\/]+)/([^\/]+)/([^\/]+)/final', Step4Handler),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
