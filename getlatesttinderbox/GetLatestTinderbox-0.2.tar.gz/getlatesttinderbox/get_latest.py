#!/usr/bin/env python

# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
# 
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
# 
# The Original Code is mozilla.org code.
# 
# The Initial Developer of the Original Code is
# Mozilla.org.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
# 
# Contributor(s):
#     Jeff Hammel <jhammel@mozilla.com>     (Original author)
# 
# Alternatively, the contents of this file may be used under the terms of
# either of the GNU General Public License Version 2 or later (the "GPL"),
# or the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
# 
# ***** END LICENSE BLOCK *****

import lxml.html
import re
import sys

def platform():
  """returns string of platform, as displayed for buildbot builds"""
  # XXX this should use the same code as buildbot

  if sys.platform == 'linux2':
    return 'linux'
  elif sys.platform == 'win32':
    return 'win32'
  elif sys.platform == 'darwin':
    return 'macosx'
  raise NotImplementedError

class GetLatestTinderbox(object):

  # class data
  BASE_URL = 'http://stage.mozilla.org/pub/mozilla.org/firefox/tinderbox-builds/'
  BASE_REGEX = r'firefox-.*\.%(LOCALE)s\.%(PLATFORM)s'

  def __init__(self, branch='mozilla-central',
               platform=platform(),
               debug=False, locale='en-US'):
    # build the base URL
    self.branch = branch
    self.platform = platform
    self.base_url = self.BASE_URL
    self.base_url += branch + '-' + platform
    if debug:
      self.base_url += '-debug'
    self.base_url += '/'
    regex = self.BASE_REGEX % { 'LOCALE': locale,
                                'PLATFORM': self.platform_regex()}
    self.regex = regex

  ### regular expressions

  def platform_regex(self):
    """return the platform part of the regex"""
    regex = {'linux': 'linux-i686',
             'win32': 'win32',
             'macosx': 'mac'}
    return regex[self.platform]

  def build_regex(self):
    """the full regex for a build"""
    regex = {'linux': r'\.tar\.bz',
             'win32': r'\.zip',
             'macosx': r'\.dmg'}
    return self.regex + regex[self.platform]

  def tests_regex(self):
    return self.regex + r'\.tests\.zip'

  def symbols_regex(self):
    return self.regex + r'\.crashreporter-symbols\.zip'

  def log_regex(self):
    """regular expression for all logs"""
    return r'%s_.*_test-(.*)-build[0-9]+.txt.gz' % self.branch

  ### methods to obtain URLs

  def builds(self, url=None):
    url = url or self.base_url
    element = lxml.html.parse(url)
    links = element.xpath('//a[@href]')
    builds = {}
    url = url.rstrip('/')
    for link in links:
      target = link.get('href').strip('/')
      name = link.text.strip('/')
      if name != target:
        continue
      try:
        builds[int(name)] = '%s/%s/' % (url, name)
      except ValueError:
        pass
    return builds

  def latest_url(self, regex, url=None):
    if isinstance(regex, basestring):
      regex = re.compile(regex)
    _builds = self.builds(url)
    for latest in sorted(_builds.keys(), reverse=True):
      build_info = _builds[latest]
      element = lxml.html.parse(build_info)
      links = element.xpath('//a[@href]')
      for link in links:
        href = link.get('href')
        if regex.match(href):
          return '%s/%s' % (build_info.rstrip('/'), href)    

  def latest_build_url(self, url=None):
    return self.latest_url(self.build_regex(), url)

  def latest_tests_url(self, url=None):
    return self.latest_url(self.tests_regex(), url)

  def latest_symbols_url(self, url=None):
    return self.latest_url(self.symbols_regex(), url)    

  ### functions to return logs

  def logs(self, url=None):
    if url is None:
      _builds = self.builds(url)
      url = _builds[sorted(_builds.keys(), reverse=True)[0]]
    element = lxml.html.parse(url)
    links = element.xpath('//a[@href]')
    logs = {}
    regex = re.compile(self.log_regex())
    for link in links:
      href = link.get('href')
      match = regex.match(href)
      if match:
        logs[match.group(1)] = '%s/%s' % (url.rstrip('/'), match.group(0))
    return logs or None # None == failure

def main(args=sys.argv[1:]):

  # parse options
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option('-d', '--debug', dest='debug', 
                    action='store_true', default=False,
                    help="get a debug build")
  try:
    client_platform = platform()
  except NotImplementedError:
    client_platform = None
  platform_help = 'platform (linux, linux64, win32, macosx, macosx64, etc)'
  if client_platform:
    platform_help += ' [DEFAULT: %s]' % client_platform
  parser.add_option('-p', '--platform', dest='platform',
                    default=client_platform, help=platform_help)
  parser.add_option('--product', dest='product', default='mozilla-central',
                    help="product [DEFAULT: mozilla-central]")
  parser.add_option('--tests', dest='tests', action='store_true', default=False,
                    help='output URL to tests')
  parser.add_option('--symbols', dest='symbols', action='store_true', default=False,
                    help='output URL to symbols')
  parser.add_option('--logs', dest='logs', action='store_true', default=False,
                    help='list test logs')
  parser.add_option('--log', '-l', dest='log',
                    help='print the URL of a specific log file')
  options, args = parser.parse_args(args)

  # check parsed options
  if not options.platform:
    parser.error('Specify your platform')
  if options.symbols and options.tests:
    parser.error("Can't specify --tests and --symbols")

  latest_tinderbox = GetLatestTinderbox(options.product, options.platform, options.debug)

  if options.logs:
    logs = latest_tinderbox.logs()
    for key in sorted(logs.keys()):
      print '%s: %s' % (key, logs[key])
    return

  if options.log:
    logs = latest_tinderbox.logs()
    return logs[options.log]

  if options.tests:
    latest = latest_tinderbox.latest_tests_url()
  elif options.symbols:
    latest = latest_tinderbox.latest_symbols_url()
  else:
    latest = latest_tinderbox.latest_build_url()
  return latest

def setuptools_main(args=sys.argv[1:]):
  print main(args)

if __name__ == '__main__':
  print main()

