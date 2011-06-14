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

from flask import Flask, abort, request, render_template
from threading import Lock
# from zipfile import ZipFile
from logging import Formatter
import sys, os, getopt, bz2
import urllib, urllib2
import logging, logging.handlers

class NoSQLTester:

  def __init__(self, params):
    self.params = params
    self.childpid = -1
    self.lock = Lock()

    # Logger initialization
    self.logger = logging.getLogger("slap.tool.nosqltester")
    if self.params['debug']:
      self.logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(self.params['log_directory'], "nosqltester.log"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    self.logger.addHandler(file_handler)

  def run(self):
    app = Flask(__name__)

    @app.route('/result/<report>')
    def download(report):
      try:
        if os.path.exists(os.path.join(self.params['report_path'], report.rstrip(self.params['compress_method']))):
          data = None
          f = open(os.path.join(self.params['report_path'], report.rstrip(self.params['compress_method'])), "rb")
          if self.params['compress_method'] == "":
            data = f.read()
          elif self.params['compress_method'] == ".bz2":
            data = bz2.compress(f.read(), 9)
          elif self.params['compress_method'] == ".zip":
            # Zip compress
            # z = ZipFile(os.path.join(os.getcwd(), self.params['report_filename']+compress_method), 'w')
            # z.write(os.path.join(os.getcwd(), self.params['report_filename']), self.params['report_filename'])
            # z.close()
            pass
          f.close()
          return data
        else:
          return None
      except:
        self.logger.debug(Formatter().formatException(sys.exc_info()))
        return str(sys.exc_info())

    @app.route('/action', methods=['POST'])
    def action():
      if request.method == 'POST' and \
         'action' in request.form:
        
        if request.form['action'] == 'START':
          pid = os.fork()
          
          if pid == 0:
            result = self.launch_tester()
            if result == 0:
              self.send_result_availability_notification()
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

    app.run(host=self.params['address'], port=self.params['port'], threaded=True)


  def send_result_availability_notification(self):
    values = {}
    values['filename'] = str(os.getpid())+".log"
    values['url'] = "http://"+self.params['address']+":"+str(self.params['port'])+"/result/"+self.params['report_filename']
    values['compress_method'] = self.params['compress_method']
    
    if self.params['compress_method'] != None:
      values['url'] += self.params['compress_method']
    
    data = urllib.urlencode(values)
    try:
      f = urllib2.urlopen("http://"+self.params['host_address']+":"+str(self.params['host_port'])+"/report", data)
      f.close()
    except:
      self.logger.debug(Formatter().formatException(sys.exc_info()))

  def execute(self, command):
    result = os.WEXITSTATUS(os.system(command))
    if result == 127:
      raise ValueError, 'Command not found: %r' % (command, )
    return result

  def launch_tester(self):
    command = self.params['binary']
    command += " > " + os.path.join(self.params['report_path'],self.params['report_filename'])
    return self.execute(command)

def usage():
  pass

def main(argv=None):

  params = {
            # Address and port of the tester
            'address':"127.0.0.1",
            'port':5000,
            # Address and port of the program
            # who wants to download the report
            'host_address':"",
            'host_port':5000,
            'num':1000,
            'report_path':"/var/log",
            'binary':"echo lol",
            'report_filename':"report.log",
            # 'debug':False,
            'debug':True,
            'compress_method':"",
            'log_directory':"/var/log",
            'plugin_name':None}

  if argv == None:
    argv = sys.argv[1:]

  try:
    opts, args = getopt.getopt(argv, "m:q:a:p:n:r:b:o:dc:l:", \
                                    ["manager=", "manager-port=", "address=", "port=", \
                                     "request-number=", "report-path=","binary=","output=", \
                                     "debug", "compress-method=", "log-directory="])
  except getopt.GetoptError:
    usage()
    sys.exit()

  for opt, arg in opts:
    if opt in ("-m", "--manager"):
      params['host_address'] = arg
    elif opt in ("-q", "--manager-port"):
      params['host_port'] = int(arg)
    elif opt in ("-a", "--address"):
      params['address'] = arg
    elif opt in ("-p", "--port"):
      params['port'] = int(arg)
    elif opt in ("-n", "--request-number"):
      params['num'] = int(arg)
    elif opt in ("-r", "--report-path"):
      params['report_path'] = arg
    elif opt in ("-b", "--binary"):
      params['binary'] = arg
    elif opt in ("-o", "--output"):
      params['report_filename'] = arg
    elif opt in ("-d", "--debug"):
      params['debug'] = True
    elif opt in ("-c", "compress-method") and arg != "":
      params['compress_method'] = "." + arg
    elif opt in ("-l", "log-directory"):
      params['log_directory'] = arg

  if params['host_address'] == params['address'] and \
     params['host_port'] == params['port']:
    print "Host and client could not have the same address and the same port"
    sys.exit()
  elif params['host_address'] == "":
    print "You must at least give the host address"
    sys.exit()

  if args.__len__() == 1:
    params['plugin_name'] = args[0]
  else:
    params['plugin_name'] = ""

  if params['plugin_name'] != "":
    entry_point = iter_entry_points(group='slapos.tool.nosqltester.plugin', name=params['plugin_name']).next()
    plugin_class = entry_point.load()
    tester = plugin_class(params)
  else:
    tester = NoSQLTester(params)
  
  tester.run()

if __name__ == "__main__":
  main(sys.argv[1:])

