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

import sys, logging, csv, re
from slapos.tool.nosqltester_manager import NoSQLTesterManager

class SheepdogTesterManager(NoSQLTesterManager):

  def __init__(self, params):
    NoSQLTesterManager.__init__(self, params)
    self.host_address = params['address']
    
    argv = sys.argv[16:]
    
    if argv.__len__() < 1:
      self.nb_thread = 1
    else:
      self.nb_thread = argv[0]
      
    if argv.__len__() < 2:
      self.nb_request = 1000
    else:
      self.nb_request = argv[1]

  def _sheepdog_init(self):
    try:
      tester_computer_partition = []
      for i in range(0, self.max_tester):
        self.logger.debug("Sheepdog tester "+str(i))
        tester_computer_partition.append(self.computer_partition.request(self.software_release_url, 'sheepdog_tester', 'sheepdog_tester'+str(i),
                   partition_parameter_kw={'host_address':self.host_address,
                                           'nb_thread':self.nb_thread,
                                           'nb_request':self.nb_request}))
      for partition in tester_computer_partition:
        self.logger.debug("Appending Sheepdog testers' start url")
        self.tester_urls.append(partition.getConnectionParameter('start_url'))
      self.logger.debug("Before remove duplicates: %s" % str(self.tester_urls))
      self.tester_urls = list(set(self.tester_urls)) # remove duplicates
      self.logger.debug("After remove duplicates: %s" % str(self.tester_urls))
      self.todo = self.tester_urls.__len__()
      return True
    except:
      self.logger.debug(str(sys.exc_info()))
      return False

  def _add_sheepdog_server_node(self):
      return True

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
      for i in range(6, lines.__len__()):
        if i != 11 and i != 12:
          l.append(re.findall(r'\d+\.\d+|\d+',lines[i])[0].replace('.', ','))
      output.writerow(l)

