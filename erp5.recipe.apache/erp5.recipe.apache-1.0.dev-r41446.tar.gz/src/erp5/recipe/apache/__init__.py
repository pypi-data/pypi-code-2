# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import pkg_resources
import subprocess
import zc.buildout

class Apache:
  def _checkSsl(self):
    if 'ssl_certificate' in self.options and 'ssl_key' in self.options:
      # nothing to do, static configuration
      return
    key_directory = os.path.join(self.options['var_directory'],
      self.name+'-ssl')
    if not os.path.exists(key_directory):
      os.makedirs(key_directory, 0700)
    openssl_configuration = os.path.join(key_directory, 'openssl.cnf')
    request_file = os.path.join(key_directory, 'request.pem')
    self.options['ssl_key'] = os.path.join(key_directory, 'key.pem')
    self.options['ssl_certificate'] = os.path.join(key_directory, 'cert.pem')
    if not(os.path.exists(self.options['ssl_key']) and os.path.exists(
        self.options['ssl_certificate'])):
      # certificate does not exists yet, generate
      openssl_binary = self.options.get('openssl_binary', 'openssl')
      open(openssl_configuration, 'w').write(pkg_resources.resource_string(
        __name__, 'templates/openssl.cnf.in') % self.options)
      try:
        assert subprocess.call([openssl_binary, 'genrsa', '-out',
          self.options['ssl_key'], '1024']) == 0
        assert subprocess.call([openssl_binary, 'req', '-batch', '-new',
          '-key', self.options['ssl_key'], '-out', request_file, '-config',
          openssl_configuration]) == 0
        assert subprocess.call([openssl_binary, 'x509', '-req', '-days',
          '365', '-in', request_file, '-signkey', self.options['ssl_key'],
          '-out', self.options['ssl_certificate']]) == 0
      except AssertionError:
        for path in [openssl_configuration, request_file,
            self.options['ssl_key'], self.options['ssl_certificate']]:
          if os.path.exists(path):
            os.unlink(path)
          raise zc.buildout.UserError("Error during generating self signed "
            "certificate.")

  def __init__(self, buildout, name, options):
    self.buildout, self.name, self.options = buildout, name, options
    self.options['location'] = self.options.get('location',
      os.path.join(self.buildout['buildout']['parts-directory'], name)
        ).strip()

    self.options['httpd_binary'] = self.options.get('httpd_binary', 'httpd'\
      ).strip()
    self.options['conf_directory'] = self.options.get('conf_directory',
      os.path.join(self.options['location'], 'etc')).strip()
    self.options['config_file'] = os.path.join(self.options['conf_directory'],
      self.name + '.conf')
    self.options['running_wrapper'] = self.options.get('running_wrapper',
      os.path.join(self.buildout['buildout']['bin-directory'], name))

    self.options['var_directory'] = self.options.get('var_directory',
      os.path.join(self.buildout['buildout']['directory'], 'var')).strip()
    self.options['log_directory'] = self.options.get('log_directory',
      os.path.join(self.options['var_directory'], 'log')).strip()
    self.options['error_log'] = os.path.join(self.options['log_directory'],
      name + '_error.log')
    self.options['access_log'] = os.path.join(self.options['log_directory'],
      name + '_access.log')

    self.options['run_directory'] = self.options.get('run_directory',
      os.path.join(self.options['var_directory'], 'run')).strip()
    self.options['pid_file'] = os.path.join(self.options['run_directory'],
      name + '.pid')
    self.options['lock_file'] = os.path.join(self.options['run_directory'],
      name + '.lock')

    self.options['path'] = self.options.get('path', '').strip()
    self.options['server_admin'] = self.options.get('server_admin',
      'unknown').strip()
    self.options['server_name'] = self.options.get('server_name',
      'localhost').strip()
    self.options['regex_server_name'] = '^' + self.options[
      'server_name'].replace('.', '\\.') + '$'

    for k in 'ip', 'port':
      self.options[k] = self.options[k].strip()

  def install(self):
    for d in [self.options['conf_directory'], self.options['var_directory'],
        self.options['log_directory'], self.options['run_directory']]:
      if not os.path.exists(d):
        os.makedirs(d, 0750)
    self._checkSsl()

  # by default update is same as install
  update = install

class Zope(Apache):
  """Apache instance to serve Zope backend"""
  rewrite_rule = "RewriteRule %(path)s($|/.*) http://%(backend_ip)s:%(backend_port)s/VirtualHostBase/https/%%{SERVER_NAME}:%(port)s/%(backend_path)s/VirtualHostRoot/_vh_%(vhname)s$1 [L,P]"
  top_rewrite_rule = "RewriteRule (.*) http://%(backend_ip)s:%(backend_port)s/VirtualHostBase/https/%%{SERVER_NAME}:%(port)s$1 [L,P]"

  def __init__(self, buildout, name, options):
    Apache.__init__(self, buildout, name, options)

  def install(self):
    Apache.install(self)
    path_template = pkg_resources.resource_string(__name__,
      'templates/zope.conf.path.in')
    path_list = []
    rewrite_list = []
    last_rewrite = None
    for line in self.options['backend_mapping'].split('\n'):
      line = line.strip()
      if len(line) == 0:
        continue
      backend, path = line.split()
      path_list.append(path_template % dict(path=path))
      backend_ip, backend_port_path = backend.split(':')
      backend_port, backend_path = backend_port_path.split('/',1)
      d = dict(
          path=path,
          backend_ip=backend_ip,
          backend_port=backend_port,
          backend_path=backend_path,
          port=self.options['port'],
          vhname=path.replace('/',''),
        )
      if path == '/':
        last_rewrite = self.top_rewrite_rule % d
      else:
        rewrite_list.append(self.rewrite_rule % d)
    if last_rewrite is not None:
      rewrite_list.append(last_rewrite)
    self.options.update(**dict(
      path_enable='\n'.join(path_list),
      rewrite_rule='\n'.join(rewrite_list)
    ))
    open(self.options['config_file'], 'w').write(pkg_resources.resource_string(
      __name__, 'templates/zope.conf.in') % self.options)
    open(self.options['running_wrapper'], 'w').write("""#!/bin/sh
exec %(httpd_binary)s -f %(config_file)s -DFOREGROUND $*""" % self.options)
    os.chmod(self.options['running_wrapper'], 0750)
    return [self.options['location']]
