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
import sys, os, getopt
import urllib, urllib2

app = Flask(__name__)

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
          'binary':"memstrike"}

@app.route('/result/<report>')
def download(report):
  if os.path.exists(os.path.join(params['report_path'],report)):
    f = open(os.path.join(params['report_path'], report), "rb")
    data = f.read()
    f.close()
    return data
  else:
    return None

@app.route('/start', methods=['POST'])
def start():
  if request.method == 'POST' and \
     'action' in request.form and \
     request.form['action'] == 'GO':
    pid = os.fork()
    if pid ==0:
      result = launch_tester()
      if result ==0:
        send_result_availability_notification()
      os._exit(os.EX_OK)
  return ""

def send_result_availability_notification():
  values = {}
  values['filename'] = str(os.getpid())+".log"
  values['url'] = "http://"+params['address']+":"+str(params['port'])+"/result/report.log" #+values['filename']
  data = urllib.urlencode(values)
  try:
    f = urllib2.urlopen("http://"+params['host_address']+":"+str(params['host_port'])+"/report", data)
    f.close()
  except:
    # print sys.exc_info()
    pass

def execute(command):
  result = os.WEXITSTATUS(os.system(command))
  if result == 127:
    raise ValueError, 'Command not found: %r' % (command, )
  return result

def launch_tester():
  command = params['binary']
  command += " > " + os.path.join(params['report_path'],"report.log")
  return execute(command)

def usage():
  pass

def main(argv=None):

  if argv == None:
    argv = sys.argv[1:]

  try:
    opts, args = getopt.getopt(argv, "h:q:a:p:n:r:b:", \
                                    ["host=", "host-port=", "address=", "port=", "request-number=", "report-path=","binary="])
  except getopt.GetoptError:
    usage()
    sys.exit()

  for opt, arg in opts:
    if opt in ("-h", "--host"):
      params['host_address'] = arg
    elif opt in ("-q", "--host-port"):
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

  if params['host_address'] == params['address'] and \
     params['host_port'] == params['port']:
    print "Host and client could not have the same address and the same port"
    sys.exit()
  elif params['host_address'] == "":
    print "You must at least give the host address"
    sys.exit()

  app.run(host=params['address'], port=params['port'])

if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))

