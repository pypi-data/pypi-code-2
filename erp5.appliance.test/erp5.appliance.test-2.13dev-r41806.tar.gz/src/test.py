# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import os
import sys
import shutil
import subprocess
import time
import signal
import logging
import ConfigParser
import pexpect
import urlparse
import uuid
import urllib
import tempfile
import httplib
import mimetools
import mimetypes
import stat
import zipfile
import datetime
from random import randint
from logging import StreamHandler, FileHandler
from optparse import OptionParser, Option


CONFIG_SECTION = "appliancetest"

TB_SEP = "============================================================="\
    "========="


def get_content_type(f):
  return mimetypes.guess_type(f.name)[0] or 'application/octet-stream'


class DummyConn:
  pass


class ConnectionHelper:
  def _simulateConn(self):
    # older python, time to simulate
    conn = DummyConn()
    conn.scheme = self.conn[0]
    if '@' in self.conn[1]:
      user_pass, host_port = self.conn[1].split('@')
      if ':' in user_pass:
        conn.username, conn.password = user_pass.split(':')
      else:
        conn.username = user_pass, None
    else:
      conn.username = None
      conn.password = None
      host_port = self.conn[1]
    if ':' in host_port:
      conn.hostname, conn.port = host_port.split(':')
    else:
      conn.hostname, conn.port = host_port, None
    conn.path = self.conn[2]
    self.conn = conn

  def __init__(self, url):
    self.conn = urlparse.urlparse(url)
    if getattr(self.conn, 'scheme', None) is None \
      and type(self.conn) in (tuple, list, set):
      self._simulateConn()
    if self.conn.scheme == 'http':
      connection_type = httplib.HTTPConnection
      if self.conn.port is None:
        self.port = 80
    else:
      connection_type = httplib.HTTPSConnection
      if self.conn.port is None:
        self.port = 443
    self.connection_type = connection_type

  def _connect(self):
    self.connection = self.connection_type(self.conn.hostname + ':' +
        str(self.conn.port or self.port))

  def POST(self, path, parameter_dict, file_list=None):
    self._connect()
    parameter_dict.update(__ac_name=self.conn.username,
                          __ac_password=self.conn.password)
    header_dict = {'Content-type': "application/x-www-form-urlencoded"}
    if file_list is None:
      body = urllib.urlencode(parameter_dict)
    else:
      boundary = mimetools.choose_boundary()
      header_dict['Content-type'] = 'multipart/form-data; boundary=%s' % (
          boundary,)
      body = ''
      for k, v in parameter_dict.iteritems():
        body += '--%s\r\n' % boundary
        body += 'Content-Disposition: form-data; name="%s"\r\n' % k
        body += '\r\n'
        body += '%s\r\n' % v
      for name, filename in file_list:
        f = open(filename, 'r')
        body += '--%s\r\n' % boundary
        body += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'\
                % (name, name)
        body += 'Content-Type: %s\r\n' % get_content_type(f)
        body += 'Content-Length: %d\r\n' % os.fstat(f.fileno())[stat.ST_SIZE]
        body += '\r\n'
        body += f.read()
        f.close()
        body += '\r\n'

    self.connection.request("POST", self.conn.path + '/' + path,
          body, header_dict)
    self.response = self.connection.getresponse()


def getMachineIdString(config):
  """Returns machine identification string"""
  kw = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  idstr = subprocess.Popen(["uname", "-m"], **kw).communicate()[0].strip()

  # try to detect gcc version
  try:
    gcc_list = subprocess.Popen(["gcc", "-v"], **kw).communicate()[0].split(
        '\n')
    for gcc in gcc_list:
      if gcc.startswith('gcc version'):
        idstr += ' gcc:' + gcc.split()[2]
        break
  except IndexError:
    pass

  # try to detect python version
  try:
    python = subprocess.Popen([config.python, '-V'], **kw).communicate(0)[0]
    idstr += ' py:' + python.split()[1].strip()
  except IndexError:
    pass

  # try to detect libc version
  try:
    libdir = os.path.sep + 'lib'
    for libso in os.listdir(libdir):
      if libso.startswith('libc.') and os.path.islink(os.path.join(libdir,
        libso)):
        libc = os.readlink(os.path.join(libdir, libso))
        if libc.endswith('.so'):
          idstr += ' libc:' + libc.split('-')[1][:-3]
        else:
          idstr += ' ' + libc
        break
  except IndexError:
    pass

  return idstr


def getDistributionList():
  """Returns list of all detected distribution flavours"""
  detected_list = []
  a = detected_list.append
  for distro_file in [
      '/etc/SuSE-release',
      '/etc/debian_version',
      '/etc/lsb-release',
      '/etc/mandrake-release',
      '/etc/mandrakelinux-release',
      '/etc/mandriva-release',
      '/etc/redhat-lsb',
      '/etc/redhat-release',
      ]:
    if os.path.exists(distro_file) and not os.path.isdir(distro_file):
      for line in open(distro_file).readlines():
        line = line.strip()
        if line not in detected_list:
          a(line)

  return detected_list


class ERP5TestReportHandler(FileHandler):

  def __init__(self, url, machine_id, suite_name):
    # random test id
    self.test_id = "%s-%X" % (
       ("%s" % datetime.date.today()).replace("-", ""),
       randint(1, 10000000000000000),
     )
    self.connection_helper = ConnectionHelper(url)
    # register real handler to store logfile
    self.logfilename = tempfile.mkstemp()[1]
    self.machine_id = machine_id
    FileHandler.__init__(self, self.logfilename)
    # report that test is running
    self.suite_name = suite_name
    self.connection_helper.POST('TestResultModule_reportRunning', dict(
      test_suite=self.suite_name,
      test_report_id=self.test_id,
      ))

  def close(self):
    FileHandler.close(self)
    if getattr(self, 'ran_trick', None) is None:
      # closed too early, nothing to report
      return
    # make file parsable by erp5_test_results
    tempcmd = tempfile.mkstemp()[1]
    tempcmd2 = tempfile.mkstemp()[1]
    tempout = tempfile.mkstemp()[1]
    templog = tempfile.mkstemp()[1]
    log_lines = open(self.logfilename, 'r').readlines()
    distribution_info = '\n'.join(getDistributionList())
    tl = open(templog, 'w')
    tl.write(TB_SEP + '\n')
    tl.write('%s\n' % self.machine_id)
    tl.write(distribution_info + '\n\n')
    if len(log_lines) > 900:
      tl.write('...[truncated]... \n\n')
    for log_line in log_lines[-900:]:
      starts = log_line.startswith
      if starts('Ran') or starts('FAILED') or starts('OK') or starts(TB_SEP):
        continue
      if starts('ERROR: ') or starts('FAIL: '):
        tl.write('internal-test: ' + log_line)
        continue
      tl.write(log_line)

    tl.write(TB_SEP + '\n')
    tl.write('\n' + self.ran_trick)
    tl.close()
    open(tempcmd, 'w').write("""svn info dummy""")
    open(tempcmd2, 'w').write(self.suite_name)
    open(tempout, 'w').write("""Detected distribution:
%s
Revision: %s""" % (distribution_info, self.revision))
    # create nice zip archive
    tempzip = tempfile.mkstemp()[1]
    zip = zipfile.ZipFile(tempzip, 'w')
    zip.write(tempcmd, 'dummy/001/cmdline')
    zip.write(tempout, 'dummy/001/stdout')
    zip.write(templog, 'dummy/001/stderr')
    zip.write(tempout, '%s/002/stdout' % self.suite_name)
    zip.write(templog, '%s/002/stderr' % self.suite_name)
    zip.write(tempcmd2, '%s/002/cmdline' % self.suite_name)
    zip.close()
    os.unlink(self.logfilename)
    os.unlink(templog)
    os.unlink(tempcmd)
    os.unlink(tempout)
    os.unlink(tempcmd2)

    # post it to ERP5
    self.connection_helper.POST('TestResultModule_reportCompleted', dict(
      test_report_id=self.test_id),
      file_list=[('filepath', tempzip)]
      )
    os.unlink(tempzip)


class SubFailed(Exception):
  pass


class TimeoutException(Exception):
  pass

software_buildout = """
[buildout]
extends = %(software_profile_url)s
extends-cache = extends-cache

"""

instance_buildout = """[buildout]
extends-cache = %(extends_cache)s
offline = true
extends =
  %(instance_profile_url)s
  %(instance_template_file)s

parts =
  mysql-instance
  cloudooo-instance
  supervisor-instance
  runUnitTest

"""

def detectRevision(config):
  revision = 'UNKNOWN'
  etag = urllib.urlopen(config.revision_detect_url).headers.get('etag')
  if etag is not None:
    etag = etag.lstrip('W').lstrip('/').strip("'\"")
    try:
      revision = etag.split('/')[0]
    except IndexError:
      pass
  return revision

def callWithTimeout(command_list, config, timeout=60, cwd=None,
    input_list=None):

  def timeout_handler(signum, frame):
    raise TimeoutException()

  old_handler = signal.signal(signal.SIGALRM, timeout_handler)
  signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(timeout)
  command = None
  try:
    try:
      returncode = None
      config.logger.info(
          'Calling %r with timeout %s\n' % (command_list, timeout))
      command = pexpect.spawn(" ".join(command_list), timeout=timeout, cwd=cwd)
      isalive = True
      while isalive:
        if input_list is not None:
          for input in input_list:
            command.expect(input[0])
            command.sendline(input[1])
            time.sleep(1)
        line = command.readline()
        if line:
          line = line[:-1]
          config.logger.info("%s", line.rstrip('\n').rstrip('\r'))
        isalive = command.isalive()
      for line in command.readlines():
        config.logger.info("%s", line.rstrip('\n').rstrip('\r'))
      command.close()
      returncode = command.exitstatus
    except TimeoutException:
      config.logger.error('Command %r run exceeded timeout %s, killed\n' % \
                                                      (command_list, timeout))
      returncode = 1
      command.close()
  finally:
    if command is not None:
      command.kill(signal.SIGKILL)
    signal.signal(signal.SIGALRM, old_handler)
    signal.alarm(0)
  if returncode != 0:
    raise SubFailed
  return returncode


def run_once(config, software_path,
                     instance_path,
                     software_profile_url,
                     instance_profile_url,
                     binary_bootstrap_file_name,
                     suite_name,
                     previous_software_revision=-1):

  status = False
  begin = time.time()

  if config.instance_tail:
    instance_tail = file(config.instance_tail, 'r').read()
  else:
    instance_tail = ''

  # Configure ERP5 test reporting handler
  revision = detectRevision(config)
  erp5_handler = None
  if config.erp5_log is not None:
    config.logger.debug('Configuring external logging system.')
    erp5_handler = ERP5TestReportHandler(config.erp5_log,
        getMachineIdString(config), suite_name)
    erp5_handler.revision = revision
    config.logger.addHandler(erp5_handler)
  exc_info = None

  extends_cache = os.path.join(software_path, 'extends-cache')
  # XXX: extends_cache shall not be created manually
  #      buildout might be extended to provide such functionality
  for d in [software_path, extends_cache]:
    if not os.path.isdir(d):
      os.mkdir(d)
  try:
    try:
      # Create buildout.cfg profile
      file(os.path.join(software_path, 'buildout.cfg'), 'w').write(
         software_buildout % dict(software_profile_url = software_profile_url))
      # Download bootstrap file
      download_command = ["""python -S -c "import urllib;f=open("""
        """'bootstrap.py','w');f.write(urllib.urlopen('http://svn.zope.org"""
        """/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py').read())"""]
      callWithTimeout(download_command, config, cwd=software_path)

      # Bootstrap buildout
      bootstrap_command = [config.python, '-S', 'bootstrap.py']
      callWithTimeout(bootstrap_command, config, timeout=600, cwd=software_path)

      # Install software
      buildout_command = ['%s/bin/buildout' % software_path]
      if config.verbose is True:
        buildout_command.append('-v')
      callWithTimeout(buildout_command, config, timeout=config.buildout_timeout, cwd=software_path)
      svn = os.path.join(software_path, 'parts', 'subversion', 'bin', 'svn')

      # Assert software
      callWithTimeout([svn, 'export', '--non-interactive',
        '--trust-server-cert',
        'https://svn.erp5.org/repos/public/erp5/trunk/buildout/tests/assertSoftware.py'],
        config, timeout=600, cwd=software_path)
      assert_command = [config.python, 'assertSoftware.py']
      callWithTimeout(assert_command, config, timeout=1800, cwd=software_path)

      ##############################################
      # Start to build the instance
      ##############################################
      # Create instance place
      if not os.path.exists(instance_path):
        mkdir = ['mkdir', instance_path]
        callWithTimeout(mkdir, config)

      # Create buildout profile
      instance_kw = dict(
        instance_profile_url = instance_profile_url,
        extends_cache = extends_cache,
        instance_template_file = os.path.join(software_path, 'instance.inc')
      )
      file(os.path.join(instance_path, 'buildout.cfg'), 'w').write(
          instance_buildout % instance_kw + instance_tail)

      # Bootstrap instance
      instance_bootstrap = [os.path.join(software_path, 'bin',
                                                  binary_bootstrap_file_name)]
      callWithTimeout(instance_bootstrap, config, cwd=instance_path)

      # Run instance buildout
      callWithTimeout([os.path.join(instance_path, 'bin', 'buildout')],
          config, cwd=instance_path)

      # Start supervisor in foreground mode and have control over its process
      # as in the end it have to be cleanly shutdown
      supervisord_command = [os.path.join(instance_path, 'bin', 'supervisord'),
          '-n']
      supervisord_popen = subprocess.Popen(supervisord_command, cwd=instance_path)
      supervisord_popen.poll()
      # Wait 10 seconds, to give supervisord chance to start required services
      time.sleep(10)
      try:
        # Populate mysql database
        mysql_command = [os.path.join(instance_path, 'var', 'bin', 'mysql'),
            '-h', '127.0.0.1', '-u', 'root']
        callWithTimeout(mysql_command,
            config, cwd=instance_path, input_list=[
              ("mysql> ", "create database development_site;"),
              ("mysql> ", "grant all privileges on development_site.* to "
                "'development_user'@'localhost' identified by "
                "'development_password';"),
              ("mysql> ", "grant all privileges on development_site.* to "
                "'development_user'@'127.0.0.1' identified by "
                "'development_password';"),
              ("mysql> ", "create database test212;"),
              ("mysql> ", "grant all privileges on test212.* to "
                "'test'@'localhost';"),
              ("mysql> ", "grant all privileges on test212.* to "
                "'test'@'127.0.0.1';"),
              ("mysql> ", "exit")])
        # Run a test from readme
        test_run_command = [os.path.join(instance_path, 'bin', 'runUnitTest'),
            'testClassTool']
        callWithTimeout(test_run_command, config, timeout=1200, cwd=instance_path)
        # check basic functionality of test -- catalog and dms
        bt5_directory = os.path.join(instance_path, 'bt5')
        try:
          if not os.path.exists(bt5_directory):
            os.mkdir(bt5_directory)
          # Get needed business template
          for bt5 in ['erp5_base', 'erp5_ingestion', 'erp5_ingestion_mysql_'
              'innodb_catalog', 'erp5_web', 'erp5_dms']:
            callWithTimeout([svn, 'export', '--non-interactive',
              '--trust-server-cert',
              'https://svn.erp5.org/repos/public/erp5/trunk/bt5/' + bt5,
              os.path.join(bt5_directory, bt5)], config, timeout=600)
          # Check that catalog is working
          for test in ['testERP5Catalog.TestERP5Catalog.'
              'test_04_SearchFolderWithDeletedObjects', 'testDms.TestDocument.'
              'testOOoDocument_get_size']:
            test_run_command = [os.path.join(instance_path, 'bin', 'runUnitTest'),
              '--bt5_path=%s/bt5' % instance_path, test]
            callWithTimeout(test_run_command, config, timeout=1200,
                cwd=instance_path)
        finally:
          if os.path.exists(bt5_directory):
            shutil.rmtree(bt5_directory)
      finally:
        # Stop supervisor
        while supervisord_popen.poll() is None:
          # send SIGKILL
          supervisord_popen.terminate()
          # give some time to terminate services
          time.sleep(5)
    except SubFailed:
      pass
    except (SystemExit, KeyboardInterrupt, SyntaxError):
      exc_info = sys.exc_info()
      # re raise really important exepctions
      raise
    except Exception:
      # anything else shall not stop the flow
      exc_info = sys.exc_info()
    else:
      status = True
  finally:
    if exc_info is not None:
      config.logger.warning('Test stopped with exception:\n', exc_info=exc_info)
    ran_trick_list = ["------------------------------------------------------"
        "----------------"]
    a = ran_trick_list.append
    a('Ran 1 test in %.2fs' % (time.time() - begin,))
    if status:
      a('OK')
    else:
      a('FAILED (failures=1)')
    if erp5_handler is not None:
      erp5_handler.ran_trick = '\n'.join(ran_trick_list)
      erp5_handler.close()
      config.logger.removeHandler(erp5_handler)


def run(config,
                software_profile_url,
                instance_profile_url,
                binary_bootstrap_file_name, suite_name):
  software_path = os.path.abspath(os.path.join(config.run_directory_path,
                                               'software'))
  instance_path = os.path.abspath(os.path.join(config.run_directory_path,
                                               'instance'))
  sleep_period = 600

  # Define loglevel
  if config.verbose:
    log_level = logging.DEBUG
  else:
    log_level = logging.INFO
  config.logger.setLevel(log_level)

  # Configure file logging functionnality
  if config.log_file is not None:
    file_handler = FileHandler(config.log_file)
    config.logger.addHandler(file_handler)

  # Configure stdout logging functionnality
  if config.stdout:
    stream_handler = StreamHandler()
    config.logger.addHandler(stream_handler)

  # If software_path exists, it means that a previous run fails.
  # Clean up by deleting previous run
  if not config.update:
    for path in software_path, instance_path:
      if os.path.exists(path):
        config.logger.info('Deleting existing directory %s' % path)
        shutil.rmtree(path)

  while 1:
    # Run buildout once
    run_once(config, software_path, instance_path, software_profile_url,
                   instance_profile_url, binary_bootstrap_file_name,
                   suite_name)
    # Clean directory
    if not config.update:
      for path in software_path, instance_path:
        if os.path.exists(path):
          config.logger.info('Deleting existing directory %s' % path)
          shutil.rmtree(path)

    if config.runonce:
      config.logger.info('Run finished')
      break

    # Sleep some time
    config.logger.info('Sleeping for %s seconds' % sleep_period)
    time.sleep(sleep_period)


class Parser(OptionParser):
  """
  Parse all arguments.
  """
  def __init__(self, usage=None, version=None):
    """
    Initialize all options possibles.
    """
    OptionParser.__init__(self, usage=usage, version=version,
                          option_list=[
      Option("-l", "--log_file",
             help="The path of the log file",
             type=str),
      Option("-v", "--verbose",
             help="Display more logs",
             action="store_true",
             default=False,
             dest="verbose"),
      Option("-u", "--update",
             help="Do not clean work environnment",
             action="store_true",
             default=False,
             dest="update"),
      Option("-o", "--runonce",
             help="Quit after first run",
             action="store_true",
             default=False),
      Option("-s", "--stdout",
             help="Display logs on stdout",
             action="store_true",
             default=False),
      Option("-e", "--erp5_log",
             help="URI of ERP5 site where log shall be pushed, "
             "in form http[s]://user:password@host/path/to/module",
             type=str),
      Option("-p", "--python",
             help="Python binary to use to run buildout.",
             type=str,
             default="python"),
      Option("-t", "--buildout_timeout",
             help="Timeout, in seconds, of buildout run, defaults to 14400.",
             type=long,
             default=14400),
      Option("-c", "--config",
             help="Configuration file. Command line arguments will override.",
             type=str),
      Option("-i", "--instance_tail",
             help="File with local additions to instance buildout.",
             type=str),
      Option("-r", "--revision_detect_url",
             help="URL used to detect revision of running test.",
             type=str,
             default="https://svn.erp5.org/repos/public/"),
    ])

  def check_args(self):
    """
    Check arguments
    """
    (options, args) = self.parse_args()
    if len(args) != 1:
      self.error("Incorrect number of arguments")
    run_directory_path, = args

    if not os.path.exists(run_directory_path):
      self.error("Run directory %s shall exist" % run_directory_path)

    return options, run_directory_path


class Config:
  def setConfig(self, option_dict, run_directory_path):
    """
    Set options given by parameters.
    """
    # Set options parameters
    for option, value in option_dict.__dict__.items():
      setattr(self, option, value)
    self.run_directory_path = run_directory_path
    self.logger = logging.getLogger("erp5app212test")


def parserConfig():
  # Parse arguments
  usage = "usage: %s [options] RUN_DIRECTORY" % sys.argv[0]
  config = Config()
  config.setConfig(*Parser(usage=usage).check_args())
  if config.config is not None:
    if not os.path.exists(config.config):
      raise ValueError("Configuration file %r cannot be found." %
          config.config)
    else:
      file_config = ConfigParser.SafeConfigParser()
      file_config.read(config.config)
      file_config = dict(file_config.items(CONFIG_SECTION))
      for k, v in file_config.iteritems():
        if getattr(config, k) is None:
          setattr(config, k, v)
  return config


def main212():
  """Test ERP5 Appliance for 2.12."""
  try:
    config = parserConfig()
    run(config,
        'https://svn.erp5.org/repos/public/erp5/trunk/buildout/buildout-2.12.cfg',
        'https://svn.erp5.org/repos/public/erp5/trunk/buildout/profiles/development-2.12.cfg',
        'bootstrap2.6', 'ERP5Appliance212')
    return_code = 0
  except SystemExit, err:
    # Catch exception raise by optparse
    return_code = err

  sys.exit(return_code)


def main28():
  """Test ERP5 Appliance 2.8."""
  try:
    config = parserConfig()
    run(config,
        'https://svn.erp5.org/repos/public/erp5/trunk/buildout/buildout.cfg',
        'https://svn.erp5.org/repos/public/erp5/trunk/buildout/profiles/development.cfg',
        'bootstrap2.4',
        'ERP5Appliance28')
    return_code = 0
  except SystemExit, err:
    # Catch exception raise by optparse
    return_code = err

  sys.exit(return_code)
