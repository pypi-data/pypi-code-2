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

from flask import Flask, abort, request, render_template, send_file
from pkg_resources import iter_entry_points, get_distribution
from logging import Formatter
from threading import Thread
import sys, os, getopt, tarfile, tempfile, bz2
import logging, logging.handlers
import urllib, urllib2
import time
from slapos import slap

class NoSQLTesterManager(object):
  """
  NoSQLTesterManager class.
  """
  
  def __init__(self, params):
    """
    :func:`__init__` method of the NoSQLTester.
    
    :param params: The name to use.
    :type params: dict.
    
    .. note::
    
      The params dictionnary should contains the following values:
      address, port, report_path, server_url, nb_server_max,
      nb_tester_max, key_file, cert_file, computer_id,
      computer_partition_id, plugin_name, debug
      
    .. note::
    
      You may need to override this method in an inheritance class.
      
    """
    
    self.log_directory = params['report_path']
    self.work_directory = os.path.split(os.path.split(self.log_directory)[0])[0]
    self.tmp_directory = os.path.join(self.work_directory, 'tmp')
    self.tester_urls = []
    self.testers_status = []
    self.todo = 0
    self.reports = []
    self.nb_init_server = int(params['nb_server_init'])
    self.nb_init_tester = int(params['nb_tester_init'])
    self.max_server = int(params['nb_server_max'])
    self.max_tester = int(params['nb_tester_max'])
    self.node_increment = int(params['node_increment'])

    self.software_release_url = params['software_release_url']
    self.server_url = params['server_url']
    self.key_file = params['key_file']
    self.cert_file = params['cert_file']
    self.computer_id = params['computer_id']
    self.computer_partition_id = params['computer_partition_id']

    self.slap = slap.slap()
    self.slap.initializeConnection(self.server_url, self.key_file, self.cert_file)
    self.computer_partition = self.slap.registerComputerPartition(self.computer_id, self.computer_partition_id)
    self.node_count = 1
    self.manager_computer_partition = None
    self.write_pipe = -1
    self.software_release_type = params['plugin_name']

    self.node_type = ""

    # Logger initialization
    self.logger = logging.getLogger("slap.tool.nosqltester_manager")
    if params['debug']:
      self.logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(self.log_directory, "nosqltester_manager.log"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    self.logger.addHandler(file_handler)

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

  def do_scheduling(self, action):
    """
    Sends an action to all the testers know by the manager.
    
    :param action: action to send (either *'START'* or *'STOP'*).
    :type action: str.
    
    """
    
    for i in range(0, self.tester_urls.__len__()):
      while not self.post(self.tester_urls[i]+'/action', action=action):
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
            
            if 'partial' in request.form and request.form['partial'] == unicode(True):
              pass
            else:
              self.todo -= 1
            
            if self.todo == 0:
              self.writeCSV(self.reports, os.path.join(self.log_directory, 'report'+str(self.node_count)+'.csv'))
              self.reports = []
              self.node_count += 1
              
              if self.node_count <= getattr(self, "max_%s" % self.node_type):
                self.add_node()
                self.todo = self.tester_urls.__len__()
                os.write(self.write_pipe, "GO")
              else:
                os.write(self.write_pipe, "END")
                os.close(self.write_pipe)
                self.write_pipe = -1
          else:
            self.logger.debug("No data: url='%s', filename='%s', "
                              "compress_method='%s'" % (request.form['url'],
                                                        request.form['filename'],
                                                        request.form.get('compress_method', None)))
        except:
          self.logger.debug(str(sys.exc_info()))
          self.logger.debug(Formatter().formatException(sys.exc_info()))
      else:
        self.logger.debug("Invalid request: method='%s' (expected: 'POST'), "
                          "url='%s', filename='%s'" % \
                            (request.method, request.form.get('url', ''),
                             request.form.get('filename', '')))
      return ""

    app.run(host=host_parameter_kw['host'], port=host_parameter_kw['port'])

  def writeCSV(self, inputnames, outputname):
    """
    Writes a CSV file.
    The :class:`NoSQLTesterManager`'s method does nothing.
    This method should be overridden by an inheritance plugin.
    """
    
    pass

def scheduler_thread(scheduler, read):
  s = ""
  while s != "END":
    time.sleep(1)
    scheduler.do_scheduling(action='START')
    s = os.read(read, 255)
    time.sleep(1)
  os.close(read)


def go(params):
  """
  Actually starts the program.
  """
  
  entry_point = iter_entry_points(group='slapos.tool.nosqltester_manager.plugin', name=params['plugin_name']).next()
  plugin_class = entry_point.load()
  scheduler = plugin_class(params)

  scheduler.default_init()

  r, w = os.pipe()
  scheduler.setWritePipe(w)
  
  t = Thread(target=scheduler_thread, args=(scheduler, r,))
  t.start()
  
  scheduler.waitForReports(host=params['address'], port=params['port'])

def usage():
  """
  Print usage.
  """
  
  pass

def main(argv=None):
  """
  Main function. It's the entry point for this program.
  
  :params argv: command line arguments.
  :type argv: list.
  
  """
  
  # Default values
  params = {
    'address':"127.0.0.1",
    'port':5000,
    'report_path':"/var/log",
    'server_url':None,
    'nb_server_max':3,
    'nb_tester_max':3,
    'nb_server_init':1,
    'nb_tester_init':3,
    'node_increment':1,
    'key_file':None,
    'cert_file':None,
    'computer_id':None,
    'computer_partition_id':None,
    'plugin_name':'kumo',
    # 'debug':False}
    'debug':True}

  # FIXME: Hack to make the flask's render_template method work with packages plugins
  sys.modules[__name__].__file__ = get_distribution(__name__).location + '/slapos/tool/nosqltester_manager/__init__.pyc'

  if argv == None:
    argv = sys.argv[1:]

  try:
    opts, args = getopt.getopt(argv, "a:dp:r:s:t:i:n:m:", \
                                    ["address=", "debug", "port=", "report-path=", \
                                     "nb-server-max=", "nb-tester-max=", "node-increment=", \
                                     "nb-server-init=", "nb-tester-init="])
  except getopt.GetoptError:
    usage()
    sys.exit()

  for opt, arg in opts:
    if opt in ("-a", "--address"):
      params['address'] = arg
    elif opt in ("-d", "--debug"):
      params['debug'] = True
    elif opt in ("-p", "--port"):
      params['port'] = int(arg)
    elif opt in ("-r", "--report-path"):
      params['report_path'] = arg
    elif opt in ("-s", "--nb-server-max"):
      params['nb_server_max'] = arg
    elif opt in ("-t", "--nb-tester-max"):
      params['nb_tester_max'] = arg
    elif opt in ("-n", "--nb-server-init"):
      params['nb_server_init'] = arg
    elif opt in ("-m", "--nb-tester-init"):
      params['nb_tester_init'] = arg
    elif opt in ("-i", "--node-increment"):
      params['node_increment'] = arg

  if args.__len__() < 7:
    usage()
    sys.exit()

  params['software_release_url'] = args[0]
  params['server_url'] = args[1]
  params['key_file'] = args[2]
  params['cert_file'] = args[3]
  params['computer_id'] = args[4]
  params['computer_partition_id'] = args[5]
  params['plugin_name'] = args[6]

  go(params)

if __name__ == "__main__":
  main(sys.argv[1:])

