#!/usr/bin/python

##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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

from flask import Flask, request
from threading import Lock
# from zipfile import ZipFile
from logging import Formatter
from socket import gethostname

import sys
import os
import bz2
import urllib
import urllib2
import logging
import argparse
import signal

class NoSQLTester(object):
  """
  NoSQLTester class.
  """
  def __init__(self):
    """
    :func:`__init__` method of the NoSQLTester.
      
    .. note::
    
      You may need to override this method in an inheritance class.
      
    """
    self.argument_namespace = self._parse_arguments(argparse.ArgumentParser(
        description='Run scalability tester.',
        # When adding arguments in the subclass having the same name, just
        # override it
        conflict_handler='resolve'))

    if self.argument_namespace.compress_method:
      self._filename_extension = '.' + self.argument_namespace.compress_method
    else:
      self._filename_extension = ''

    self.childpid = -1
    self.lock = Lock()

    # Logger initialization
    self.logger = logging.getLogger("slap.tool.nosqltester")
    if self.argument_namespace.enable_debug:
      self.logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(self.argument_namespace.log_directory,
                                                    "nosqltester.log"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    self.logger.addHandler(file_handler)

  def _add_parser_arguments(self, parser):
    parser.add_argument('--tester-address', '-a',
                        default='127.0.0.1',
                        help='Tester IP address')

    parser.add_argument('--tester-port', '-p',
                        type=int,
                        default=5000,
                        help='Tester TCP port')

    parser.add_argument('--manager-address', '-m',
                        required=True,
                        help='Tester manager IP address')

    parser.add_argument('--manager-port', '-q',
                        default=5000,
                        help='Tester manager TCP port')

    parser.add_argument('--enable-debug', '-d',
                        type=bool,
                        default=True,
                        help='Enable debug messages')

    parser.add_argument('--report-directory', '-r',
                        default='/var/log',
                        help='Report directory')

    parser.add_argument('--report-filename', '-o',
                        default='report.log',
                        help='Report filename (when executing a command)')

    parser.add_argument('--compress-method', '-c',
                        help='Compress method to use for the reports')

    parser.add_argument('--log-directory', '-l',
                        default='/var/log',
                        help='Log directory to use')

    parser.add_argument('--execute-command', '-b',
                        help='Command to execute (when executing a command)')

  def _parse_arguments(self, parser):
    self._add_parser_arguments(parser)
    namespace = parser.parse_args()

    if namespace.tester_address == namespace.manager_address and \
          namespace.tester_port == namespace.manager_port:
      raise argparse.ArgumentTypeError(
        "Tester and tester manager must not have the same address and port")

    return namespace

  def run(self):
    """
    Defines and starts the HTTP server.
    """
    app = Flask(__name__)

    @app.route('/result/<report>')
    def download(report):
      """
      Sends the requested *report* file.
      
      :param report: Name of the file to send.
      :type report: unicode.

      :returns: data to send.
      
      """
      try:
        if 'size' in request.args:
          size = int(request.args['size'])
        else:
          size = -1

        if os.path.exists(os.path.join(self.argument_namespace.report_directory,
                                       report.rstrip(self._filename_extension))):
          data = None
          f = open(os.path.join(self.argument_namespace.report_directory,
                                report.rstrip(self._filename_extension)), "rb")
          if not self.argument_namespace.compress_method:
            data = f.read(size)
          elif self.argument_namespace.compress_method == "bz2":
            data = bz2.compress(f.read(size), 9)
          elif self.argument_namespace.compress_method == "zip":
            # z = ZipFile(os.path.join(os.getcwd(),
            #                          self.argument_namespace.report_filename + '.zip'),
            #             'w')
            # z.write(os.path.join(os.getcwd(), self.argument_namespace.report_filename),
            #         self.argument_namespace.report_filename)
            # z.close()
            raise NotImplementedError
          f.close()
          return data
        else:
          return None
      except:
        self.logger.debug(Formatter().formatException(sys.exc_info()))
        return str(sys.exc_info())

    @app.route('/action', methods=['POST'])
    def action():
      """
      Starts or stops the testing process.
      
      :returns: empty string.
      """
      if request.method == 'POST' and 'action' in request.form:
        if request.form['action'] == 'START':
          for attribute, value in request.form.iteritems():
            if attribute == 'action':
              continue

            setattr(self.argument_namespace, attribute, value)

          pid = os.fork()
          
          if pid == 0:
            try:
              self.run_tester()
            except:
              self.logger.error(Formatter().formatException(sys.exc_info()))
              os._exit(os.EX_SOFTWARE)
            else:
              os._exit(os.EX_OK)
          else:
            self.lock.acquire()
            self.childpid = pid
            self.lock.release()
        
        elif request.form['action'] == 'STOP':
          if self.childpid != -1:
            os.kill(self.childpid, signal.SIGTERM)
            os.waitpid(self.childpid)
            # os.kill(self.childpid, signal.SIGKILL)
            self.lock.acquire()
            self.childpid = -1
            self.lock.release()
      return ""

    app.run(host=self.argument_namespace.tester_address,
            port=self.argument_namespace.tester_port,
            threaded=True)

  def send_result_availability_notification(self, filename=None, size=-1, partial=False):
    """
    Sends result availabilty notification to the manager.
    
    :param filename: name of the result file.
    :type filename: str.
    :param partial: is it a partial result ?
    :type partial: bool.
    
    """
    
    if not filename:
      filename = self.argument_namespace.report_filename
    
    values = {}
    values['filename'] = "%s-%d-%s" % (gethostname(), os.getpid(), filename)
    values['url'] = "http://[%s]:%d/result/%s?size=%d" % (self.argument_namespace.tester_address,
                                                          self.argument_namespace.tester_port,
                                                          filename + self._filename_extension,
                                                          size)
    if self.argument_namespace.compress_method:
      values['compress_method'] = self.argument_namespace.compress_method

    values['partial'] = partial
    
    data = urllib.urlencode(values)
    try:
      f = urllib2.urlopen("http://[%s]:%d/report" % (self.argument_namespace.manager_address,
                                                     self.argument_namespace.manager_port),
                          data)
      f.close()
    except:
      self.logger.debug(Formatter().formatException(sys.exc_info()))

  def run_tester(self):
    """
    Runs the testing process.
    
    :returns: int -- the subprocess execution result code.
    
    .. note::
      You may need to override this method in an inheritance class.
    
    """
    command = "%s > %s" % (self.argument_namespace.execute_command,
                           os.path.join(self.argument_namespace.report_directory,
                                        self.argument_namespace.report_filename))

    result = os.WEXITSTATUS(os.system(command))
    if result == 127:
      raise ValueError, 'Command not found: %r' % command
    elif result == 0:
      self.send_result_availability_notification()

    return result

def main():
  """
  Main function. It's the entry point for this program.
  """
  return NoSQLTester().run()

if __name__ == "__main__":
  main()
