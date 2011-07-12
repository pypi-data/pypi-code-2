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

from flask import Flask, request, render_template, send_file
from pkg_resources import iter_entry_points, get_distribution
from logging import Formatter
from threading import Thread
from slapos import slap

import sys
import os
import tarfile
import tempfile
import bz2
import logging
import urllib
import urllib2
import time
import argparse

class NoSQLTesterManager(object):
  """
  NoSQLTesterManager class.
  """
  
  def __init__(self):
    """
    :func:`__init__` method of the NoSQLTester.
    
    :param args: The name to use.
    :type args: tuple.
    
    .. note::
    
      The args tuple should be the program's argument.
      
    .. note::
    
      You may need to override this method in an inheritance class.
      
    """
    self.software_release_type = sys.argv.pop(1)
    parameter_dict = vars(self._parse_arguments(argparse.ArgumentParser(
          description='Manage scalability tester(s).',
          # When adding arguments  in the subclass having the  same name, just
          # override it
          conflict_handler='resolve')))
    
    for attribut, value in parameter_dict.iteritems():
      setattr(self, attribut, value)
    
    self.work_directory = os.path.split(os.path.split(self.log_directory)[0])[0]
    self.tmp_directory = os.path.join(self.work_directory, 'tmp')
    self.tester_urls = []
    self.testers_status = []
    self.todo = 0
    self.reports = []
    
    self.erp5_publish_url = parameter_dict['erp5_publish_url']
    self.erp5_publish_project = parameter_dict['erp5_publish_project']

    self.slap = slap.slap()
    self.slap.initializeConnection(self.server_url, self.key_file, self.cert_file)
    self.computer_partition = self.slap.registerComputerPartition(self.computer_id, self.computer_partition_id)
    self.node_count = 0
    self.manager_computer_partition = None
    self.write_pipe = -1

    self.node_type = ""

    # Needed for ERP5BenchmarkResult
    self.repeat = 1
    self.error_message_set = set()
    self.user_tuple = ("user0")
    self.benchmark_suite_name_list = []

    # Logger initialization
    self.logger = logging.getLogger("slap.tool.nosqltester_manager")
    if self.enable_debug:
      self.logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(self.log_directory, "nosqltester_manager.log"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    self.logger.addHandler(file_handler)

  def _add_parser_arguments(self, parser):
    parser.add_argument('--address', '-a', default='127.0.0.1',
                        help='Manager IP address')

    parser.add_argument('--port', '-p', type=int, default=5000,
                        help='Manager port')

    parser.add_argument('--enable-debug', '-d', type=bool, default=True,
                        help='Enable debug messages')

    parser.add_argument('--log-directory', '-r', default='/var/log',
                        help='Log/Report directory')

    parser.add_argument('--max-server', '-s', type=int, default=3,
                        help='Maximum number of servers')

    parser.add_argument('--max-tester', '-t', type=int, default=3,
                        help='Maximum number of testers')

    parser.add_argument('--nb-init-server', '-n', type=int, default=1,
                        help='Number of servers to start with')

    parser.add_argument('--nb-init-tester', '-m', type=int, default=3,
                        help='Number of testers to start with')

    parser.add_argument('--node-increment', '-i', type=int, default=1,
                        help='Number of nodes to add at the end of an iteration')

    parser.add_argument('--erp5-publish-url',
                        help='ERP5 URL to publish the results to '
                             '(default: disabled, thus writing to CSV files)')

    parser.add_argument('--erp5-publish-project', help='ERP5 publish project')

    parser.add_argument('software_release_url', help='Software Release URL')
    parser.add_argument('server_url', help='Server URL')
    parser.add_argument('key_file', help='SSL key file')
    parser.add_argument('cert_file', help='SSL certificate file')
    parser.add_argument('computer_id', help='Computer ID')
    parser.add_argument('computer_partition_id', help='Computer Partition ID')

  def _parse_arguments(self, parser):
    self._add_parser_arguments(parser)
    return parser.parse_args()

  def default_init(self):
    """
    Initialize a default server and tester configuration by
    calling the *_<plugin_name>_init* function if it exists.
    
    .. note::
      The *_<plugin_name>_init* must be defined the plugin
      named *<plugin_name>*.
    """
    if self.software_release_type == None:
      pass
    elif "_%s_init" % self.software_release_type in dir(self) and \
      callable(getattr(self, "_%s_init" % self.software_release_type)):
      while not getattr(self, "_%s_init" % self.software_release_type)():
        time.sleep(1)
      self.testers_status = ['STOPPED' for url in self.tester_urls]
      self.todo = self.tester_urls.__len__()
      self.node_count = getattr(self, 'nb_init_%s' % self.node_type)

  def add_node(self):
    """
    Adds a new node by calling the *_add_<plugin_name>_<node_type>_node*
    function if it exists.
    
    .. note::
      The *_add_<plugin_name>_<node_type>_node* should be defined the plugin
      named *<plugin_name>*.
    """
    function_name = "_add_%s_%s_node" % (self.software_release_type,  self.node_type)
    
    if self.software_release_type == None:
      pass
    elif function_name in dir(self) and \
      callable(getattr(self, function_name)):
      while not getattr(self, function_name)():
        time.sleep(1)

  def setWritePipe(self, write_pipe):
    """
    Set a pipe to make the HTTP server
    """
    self.write_pipe = write_pipe

  def get(self, url):
    """
    Gets the contents of an url.
    """
    f = urllib2.urlopen(url)
    f.close()

  def post(self, url, **values):
    """
    Post values to an URL.
    
    :param url: URL
    :type url: str.
    :param values: values to post
    :type values: dict.
    
    """
    try:
      data = urllib.urlencode(values)
      f = urllib2.urlopen(url, data)
      f.close()
    except:
      return False
    return True

  def preRun(self):
    try:
      start_value_dict = {}

      if self.erp5_publish_url and self.erp5_publish_project:
        if self.nb_init_tester != self.max_tester:
          nb_users = (self.nb_init_tester, self.max_tester)
        else:
          nb_users = self.max_tester

        from erp5.utils.benchmark.benchmark import ERP5BenchmarkResult
        new_document_id = ERP5BenchmarkResult.createResultDocument(
          self.erp5_publish_url,
          self.erp5_publish_project,
          self.repeat,
          nb_users)

        self.erp5_publish_url = '/'.join((self.erp5_publish_url, new_document_id))
        start_value_dict['erp5_publish_url'] = self.erp5_publish_url
        start_value_dict['erp5_publish_project'] = self.erp5_publish_project
    except:
      self.logger.debug(Formatter().formatException(sys.exc_info()))

    return start_value_dict

  def push_to_erp5(self):
    try:
      if self.erp5_publish_url and self.erp5_publish_project:
        from erp5.utils.benchmark.benchmark import ERP5BenchmarkResult
        result_instance = ERP5BenchmarkResult(self, 1, 0)
        
        with result_instance as result:
          for filename in self.benchmark_suite_name_list:
            current_suite = result.enterSuite(filename)
            f = open(os.path.join(self.log_directory, filename))
            i = 0
            for line in f:
              result(line.rstrip(), 0)
            f.close()
            result.exitSuite()

          result_instance.iterationFinished()
    except:
      self.logger.debug(Formatter().formatException(sys.exc_info()))

  def do_scheduling(self, action):
    """
    Sends an action to all the testers know by the manager.
    
    :param action: action to send (either *'START'* or *'STOP'*).
    :type action: str.
    
    """
    start_value_dict = {'action': action}
    start_value_dict.update(self.preRun())
        
    for i in range(0, self.tester_urls.__len__()):
      self.logger.debug("send %s to %s" % (action, self.tester_urls[i]))
      while not self.post(self.tester_urls[i]+'/action', **start_value_dict):
        self.logger.debug("sleep")
        time.sleep(1)
      self.testers_status[i] = action.upper()+('P' if action == 'stop' else '')+'ED'

  def uncompress(self, cdata, format):
    """
    Uncompress data from a specific compression format.
    
    :param cdata: data to uncompress.
    :param format: compression format. (with a leading *'.'*)
    :type format: str.
    """
    if format == "bz2":
      return bz2.decompress(cdata)
    elif format == "zip":
      raise NotImplementedError
    else:
      raise ValueError, "Unknown format: %s" % str(format)

  def waitForReports(self, **host_parameter_kw):
    """
    Defines and starts a web server using *Flask*.
    
    :param host_parameter_kw: A dictionnary containing the *'host'* and *'port'*
                              on which the web server will run.
    :type host_parameter_kw: dict.
    
    """
    
    if 'host' not in host_parameter_kw or \
       'port' not in host_parameter_kw:
      pass

    app = Flask(__name__)

    @app.route('/')
    def ui():
      """
      Displays the Web UI.
      
      :returns: the UI's webpage.
      """
      web_page = None
      manager_url = 'http://'+"[%s]" % host_parameter_kw['host']+':5000/'
      try:
        results = []
        
        for f in sorted(os.listdir(self.log_directory)):
          s = os.path.split(f)[1]
          # if s.find("report") == 0:
          item = {}
          item['name'] = s
          item['href'] = 'http://'+"[%s]" % host_parameter_kw['host']+':5000/result/'+item['name']
          results.append(item)
        
        web_page = render_template('ui.html', tester_urls = self.tester_urls, manager_url = manager_url, \
                                   done  = self.node_count-1, total = self.max_server, results=results, \
                                   testers_status = self.testers_status)
      except:
        web_page = str(sys.exc_info())
      
      return web_page

    @app.route('/stop/<tester>')
    def stop(tester):
      """
      Stops a desired tester.
      
      :returns: the UI's webpage.
      """
      try:
        if tester == "all":
          self.do_scheduling('STOP')
        else:
          while not self.post(self.tester_urls[int(tester)]+'/action', action='STOP'):
            time.sleep(1)
      except:
        # self.logger.debug(Formatter().formatException(sys.exc_info()))
        return Formatter().formatException(sys.exc_info())
      return ui()

    @app.route('/result/<report>')
    def getResult(report):
      """
      Sends a *report* file to the user.
      
      :params report: Name of the file to send.
      :type report: unicode.
      :returns: the *report* file.
      
      """
      try:
        if report == "all.tar.bz2":
          tmp = tempfile.NamedTemporaryFile(dir=self.tmp_directory)
          tar = tarfile.open(None, "w:bz2", tmp)
          for f in sorted(os.listdir(self.log_directory)):
            s = os.path.split(f)[1]
            tar.add(os.path.join(self.log_directory, s), s, False)
          tar.close()
          tar_file = send_file(tmp.name)
          tmp.close()
          return tar_file
        elif os.path.exists(os.path.join(self.log_directory, report)):
          return send_file(os.path.join(self.log_directory, report))
        else:
          return None
      except:
        return sys.exc_info()

    def _allCurrentTesterExecuted(*args, **kwargs):
      if self.node_count < getattr(self, "max_%s" % self.node_type):
        self.logger.debug("Adding %d nodes" % self.node_increment)
        self.add_node()
        self.todo = self.tester_urls.__len__()
        os.write(self.write_pipe, "GO")
        self.node_count += self.node_increment
      else:
        self.logger.debug("Pushing results to ERP5")
        self.push_to_erp5()
        self.benchmark_suite_name_list = []
        self.logger.debug("Stopping")
        os.write(self.write_pipe, "END")
        os.close(self.write_pipe)
        self.write_pipe = -1
        self.postRun()

    @app.route('/report', methods=['POST'])
    def receiveReport():
      """
      Gets a report from a tester.
      
      :returns: empty string.
      """
      if request.method == 'POST' and \
         'url' in request.form and \
         'filename' in request.form:
        try:
          data = None
          f = urllib2.urlopen(request.form['url'])
          data = f.read()
          f.close()

          compress_method = request.form.get('compress_method', None)
          if compress_method:
            data = self.uncompress(data, compress_method)
          
          if data is not None:
            filepathname = os.path.join(self.log_directory, request.form['filename'])
            self.reports.append(filepathname)
            f = open(filepathname, "w")
            f.write(data)
            f.close()
            
            if not ('partial' in request.form and request.form['partial'] == unicode(True)):
              self.todo -= 1

            if self.todo == 0:
              self.benchmark_suite_name_list.append(self.process_report(self.reports))
              self.reports = []
              _allCurrentTesterExecuted()

          else:
            self.logger.debug("No data: url='%s', filename='%s', "
                              "compress_method='%s'" % (request.form['url'],
                                                        request.form['filename'],
                                                        request.form.get('compress_method', None)))
        except:
          self.logger.debug(str(sys.exc_info()))
          self.logger.debug(Formatter().formatException(sys.exc_info()))

      elif request.method == 'POST' and 'error_message_set' in request.form and \
           self.erp5_publish_url and self.erp5_publish_project:
        self.todo -= 1

        error_message_set = \
            set([message for message in request.form['error_message_set'].split('|') if message])

        try:
          self.error_message_set.update(error_message_set)
        except AttributeError:
          self.error_message_set = error_message_set

        if self.todo == 0:
          _allCurrentTesterExecuted()

      else:
        self.logger.debug("Invalid request: method='%s' (expected: 'POST'), "
                          "url='%s', filename='%s'" % \
                            (request.method, request.form.get('url', ''),
                             request.form.get('filename', '')))
      return ""

    app.run(host=host_parameter_kw['host'], port=host_parameter_kw['port'])

  def process_report(self, inputnames):
    """
    Writes a CSV file.
    The :class:`NoSQLTesterManager`'s method does nothing.
    This method should be overridden by an inheritance plugin.
    """
    pass

  def postRun(self):
    try:
      if self.erp5_publish_url and self.erp5_publish_project:
        from erp5.utils.benchmark.benchmark import ERP5BenchmarkResult
        ERP5BenchmarkResult.closeResultDocument(self.erp5_publish_url,
                                                tuple(self.error_message_set))
    except:
      self.logger.debug(Formatter().formatException(sys.exc_info()))

def scheduler_thread(scheduler, read):
  s = ""
  while s != "END":
    time.sleep(1)
    scheduler.do_scheduling(action='START')
    s = os.read(read, 255)
    time.sleep(1)
  os.close(read)

def main():
  """
  Main function. It's the entry point for this program.
  """
  # FIXME: Hack to make the  flask's render_template method work with packages
  # plugins
  sys.modules[__name__].__file__ = get_distribution(__name__).location + \
                        '/slapos/tool/nosqltester_manager/__init__.pyc'

  try:
    plugin_name = sys.argv[1]
  except IndexError:
    raise RuntimeError, "ERROR: Plugin name required"

  entry_point = iter_entry_points(group='slapos.tool.nosqltester_manager.plugin',
                                  name=plugin_name).next()
  plugin_class = entry_point.load()

  scheduler = plugin_class()
  scheduler.default_init()

  r, w = os.pipe()
  scheduler.setWritePipe(w)
  
  t = Thread(target=scheduler_thread, args=(scheduler, r,))
  t.start()
  
  scheduler.waitForReports(host=scheduler.address, port=scheduler.port)


if __name__ == "__main__":
  main()
