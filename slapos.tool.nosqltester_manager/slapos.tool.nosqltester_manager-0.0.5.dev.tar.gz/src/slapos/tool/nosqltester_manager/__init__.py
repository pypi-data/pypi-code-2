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
import sys, os, getopt, tarfile, tempfile
import urllib, urllib2
import time, csv, re
from slapos import slap

params = {
          # Address and port of the tester
          'address':"127.0.0.1",
          'port':5000,
          'report_path':"/var/log",
          'server_url':None,
          'key_file':None,
          'cert_file':None,
          'computer_id':None,
          'computer_partition_id':None}

class TesterScheduler:

  def __init__(self, log_directory):
    self.work_directory = os.path.split(os.path.split(log_directory)[0])[0]
    self.tmp_directory = os.path.join(self.work_directory, 'tmp')
    self.log_directory = log_directory
    self.tester_urls = []
    self.todo = 0
    self.reports = []
    self.max_server = 3

    self.software_release_url = params['software_release_url']
    self.server_url = params['server_url']
    self.key_file = params['key_file']
    self.cert_file = params['cert_file']
    self.computer_id = params['computer_id']
    self.computer_partition_id = params['computer_partition_id']

    self.slap = slap.slap()
    self.slap.initializeConnection(self.server_url, self.key_file, self.cert_file)
    self.computer_partition = self.slap.registerComputerPartition(self.computer_id, self.computer_partition_id)
    self.server_count = 1
    self.manager_computer_partition = None
    self.write_pipe = -1
    self.software_release_type = None

  def default_init(self):
    if self.software_release_type == None:
      pass
    elif "_%s_init" % self.software_release_type in dir(self) and \
      callable(getattr(self, "_%s_init" % self.software_release_type)):
      while not getattr(self, "_%s_init" % self.software_release_type)():
        time.sleep(1)

  def add_server_node(self):
    if self.software_release_type == None:
      pass
    elif "_add_%s_server_node" % self.software_release_type in dir(self) and \
      callable(getattr(self, "_add_%s_server_node" % self.software_release_type)):
      while not getattr(self, "_add_%s_server_node" % self.software_release_type)():
        time.sleep(1)

  def setWritePipe(self, write_pipe):
    self.write_pipe = write_pipe

  def get(self, url):
    f = urllib2.urlopen(url)
    f.close()

  def post(self, url, **values):
    try:
      data = urllib.urlencode(values)
      f = urllib2.urlopen(url, data)
      f.close()
    except:
      return False
    return True

  def do_scheduling(self):
    for url in self.tester_urls:
      while not self.post(url, action='GO'):
        time.sleep(1)

  def waitForReports(self, **host_parameter_kw):
    if 'host' not in host_parameter_kw or \
       'port' not in host_parameter_kw:
      pass

    app = Flask(__name__)

    @app.route('/')
    def ui():
      web_page = None
      url_all = 'http://'+"[%s]" % host_parameter_kw['host']+':5000/result/all.tar.bz2'
      try:
        results = []
        
        for f in sorted(os.listdir(self.log_directory)):
          s = os.path.split(f)[1]
          if s.find("report") == 0:
            item = {}
            item['name'] = s
            item['href'] = 'http://'+"[%s]" % host_parameter_kw['host']+':5000/result/'+item['name']
            results.append(item)
        
        web_page = render_template('ui.html', url_all = url_all, done  = self.server_count-1, total = self.max_server, results=results)
      except:
        web_page = str(sys.exc_info())
      
      return web_page

    @app.route('/result/<report>')
    def getResult(report):
      try:
        if report == "all.tar.bz2":
          tmp = tempfile.NamedTemporaryFile(dir=self.tmp_directory)
          tar = tarfile.open(None, "w:bz2", tmp)
          for f in sorted(os.listdir(self.log_directory)):
            s = os.path.split(f)[1]
            if s.find("report") == 0:
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
      if request.method == 'POST' and \
         'url' in request.form and \
         'filename' in request.form:
        try:
          f = urllib2.urlopen(request.form['url'])
          data = f.read()
          f.close()
        except:
          print sys.exc_info()
        if data is not None:
          filepathname = os.path.join(self.log_directory, request.form['filename'])
          self.reports.append(filepathname)
          f = open(filepathname, "w")
          f.write(data)
          f.close()
          self.todo -= 1
          if self.todo == 0:
            self.writeCSV(self.reports, os.path.join(self.log_directory, 'report'+str(self.server_count)+'.csv'))
            self.reports = []
            self.server_count += 1
            
            if self.server_count <= self.max_server:
              self.add_server_node()
              self.todo = self.tester_urls.__len__()
              os.write(self.write_pipe, "GO")
            else:
              os.write(self.write_pipe, "END")
              os.close(self.write_pipe)
              self.write_pipe = -1
      return ""

    app.run(host=host_parameter_kw['host'], port=host_parameter_kw['port'])

  def writeCSV(self, inputnames, outputname):
    pass

class KumoTesterScheduler(TesterScheduler):

  def __init__(self, log_directory):
    TesterScheduler.__init__(self, log_directory)
    self.software_release_type = 'kumo'

  def _kumo_init(self):
    try:
      manager_computer_partition = self.computer_partition.request(self.software_release_url, 'kumo_manager', 'kumo_manager')

      self.computer_partition.request(self.software_release_url, 'kumo_server', 'kumo_server'+str(self.server_count),
                   partition_parameter_kw={'manager_address':manager_computer_partition.getConnectionParameter('manager_address'),
                                           'manager_port':manager_computer_partition.getConnectionParameter('manager_port')})

      gateway_computer_partition = self.computer_partition.request(self.software_release_url, 'kumo_gateway', 'kumo_gateway',
                   partition_parameter_kw={'manager_address':manager_computer_partition.getConnectionParameter('manager_address'),
                                           'manager_port':manager_computer_partition.getConnectionParameter('manager_port')})

      tester_computer_partition = []
      for i in range(0, 3):
        """
        tester_computer_partition.append(self.computer_partition.request(self.software_release_url, 'nosqltester', 'nosqltester'+str(i),
                   partition_parameter_kw={'gateway_address':gateway_computer_partition.getConnectionParameter('gateway_address'),
                                           'gateway_port':gateway_computer_partition.getConnectionParameter('gateway_port'),
                                           'host_address':params['address']}))
        """
        binary = gateway_computer_partition.getConnectionParameter('memstrike_binary') + \
                 " -l " + \
                 gateway_computer_partition.getConnectionParameter('gateway_address').strip("[]") + \
                 " -p " + \
                 gateway_computer_partition.getConnectionParameter('gateway_port') + \
                 " 1000" #" -t 32 1024000"
        tester_computer_partition.append(self.computer_partition.request(self.software_release_url, 'nosqltester', 'nosqltester'+str(i),
                   partition_parameter_kw={'host_address':params['address'],
                                           'binary':binary}))
      for partition in tester_computer_partition:
        self.tester_urls.append(partition.getConnectionParameter('start_url'))
      self.tester_urls = list(set(self.tester_urls)) # remove duplicates
      self.todo = self.tester_urls.__len__()
      self.manager_computer_partition = manager_computer_partition
      return True
    except:
      return False

  def _add_kumo_server_node(self):
    try:
      partition = self.computer_partition.request(self.software_release_url, 'kumo_server', 'kumo_server'+str(self.server_count),
                   partition_parameter_kw={'manager_address':self.manager_computer_partition.getConnectionParameter('manager_address'),
                                           'manager_port':self.manager_computer_partition.getConnectionParameter('manager_port')})
      # line made to crash the function call until we call slapgrid
      partition.getConnectionParameter('server_address')
      return True
    except:
      return False

  def writeCSV(self, inputnames, outputname):
    output = csv.writer(open(outputname, 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # Header
    output.writerow(['set sec', 'set MB', 'set Mbps', 'set req/sec', 'set usec/req',
                     'get sec', 'get MB', 'get Mbps', 'get req/sec', 'get usec/req'])
    for inputname in inputnames:
      l = []
      f = open(inputname, "r")
      lines = f.readlines()
      f.close()
      for i in range(8, lines.__len__()):
        if i != 13 and i != 14:
          l.append(re.findall(r'\d+\.\d+|\d+',lines[i])[0].replace('.', ','))
      output.writerow(l)

def go():
  scheduler = KumoTesterScheduler(params['report_path'])

  scheduler.default_init()

  r, w = os.pipe()
  pid = os.fork()
  if pid == 0:
    s = ""
    while s != "END":
      time.sleep(1)
      scheduler.do_scheduling()
      s = os.read(r, 255)
      time.sleep(1)
    os.close(r)
    os._exit(os.EX_OK)
  else:
    scheduler.setWritePipe(w)
    scheduler.waitForReports(host=params['address'], port=params['port'])

def usage():
  pass

def main(argv=None):

  if argv == None:
    argv = sys.argv[1:]

  try:
    opts, args = getopt.getopt(argv, "a:p:r:", \
                                    ["address=", "port=", "report-path="])
  except getopt.GetoptError:
    usage()
    sys.exit()

  for opt, arg in opts:
    if opt in ("-a", "--address"):
      params['address'] = arg
    elif opt in ("-p", "--port"):
      params['port'] = int(arg)
    elif opt in ("-r", "--report-path"):
      params['report_path'] = arg

  if args.__len__() != 6:
    usage()
    sys.exit()

  params['software_release_url'] = args[0]
  params['server_url'] = args[1]
  params['key_file'] = args[2]
  params['cert_file'] = args[3]
  params['computer_id'] = args[4]
  params['computer_partition_id'] = args[5]

  go()

if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))

