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

import sys, csv, re
from logging import Formatter
from slapos.tool.nosqltester_manager import NoSQLTesterManager

class KumoTesterManager(NoSQLTesterManager):

  def __init__(self, params):
    NoSQLTesterManager.__init__(self, params)
    
    self.node_type = "server"
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

    self.max_manager = 1
    self.computer_guid_list = self.computer_partition.getConnectionParameter('computer_guid_list').split(':')

  def _kumo_init(self):
    try:
      self.logger.debug("Kumo manager")
      manager_partition = self.computer_partition.request(self.software_release_url, 'kumo_manager', 'kumo_manager',
                   filter_kw={'computer_guid':self.computer_guid_list[0]})
      self.logger.debug("Kumo manager guid: "+self.computer_guid_list[0])

      partition_parameter_kw = {
        'manager_address':manager_partition.getConnectionParameter('address'),
        'manager_port':manager_partition.getConnectionParameter('port')}

      self.logger.debug("Kumo server 1")
      self.computer_partition.request(
        self.software_release_url,
        'kumo_server',
        'kumo_server'+str(self.node_count),
        partition_parameter_kw=partition_parameter_kw,
        filter_kw={'computer_guid':self.computer_guid_list[self.max_manager+self.node_count-1]})
      self.logger.debug("Kumo server 1 guid: "+self.computer_guid_list[self.max_manager+self.node_count-1])

      partition_parameter_kw = {'manager_address':manager_partition.getConnectionParameter('address'),
                                'manager_port':manager_partition.getConnectionParameter('port')}

      self.logger.debug("Memstrike set gateway")
      gateway_partition = self.computer_partition.request(
        self.software_release_url,
        'kumo_gateway',
        'memstrike_gateway',
        partition_parameter_kw=partition_parameter_kw,
        filter_kw={'computer_guid':self.computer_guid_list[self.max_manager+self.node_count-1]})
      self.logger.debug("Memstrike set gateway guid: "+self.computer_guid_list[self.max_manager+self.node_count-1])


      partition_parameter_kw = {
        'gateway_address':gateway_partition.getConnectionParameter('address'),
        'gateway_port':gateway_partition.getConnectionParameter('port'),
        'nb_thread':self.nb_thread,
        'nb_request':self.nb_request}

      self.logger.debug("Memstrike setter")
      memstrike_partition = self.computer_partition.request(
        self.software_release_url,
        'memstrike_set',
        'memstrike_set',
        partition_parameter_kw=partition_parameter_kw,
        filter_kw={'computer_guid':self.computer_guid_list[self.max_manager+self.node_count-1]})
      self.logger.debug("Memstrike setter guid: "+self.computer_guid_list[self.max_manager+self.node_count-1])

      # line made to crash the function call until we call slapgrid
      memstrike_partition.getConnectionParameter('status')

      tester_partition_list = []
      for i in range(0, self.max_tester):
      
        partition_parameter_kw = {'manager_address':manager_partition.getConnectionParameter('address'),
                                  'manager_port':manager_partition.getConnectionParameter('port')}
      
        self.logger.debug("Kumo gateway "+str(i))
        gateway_partition = self.computer_partition.request(
          self.software_release_url,
          'kumo_gateway',
          'kumo_gateway'+str(i),
          partition_parameter_kw=partition_parameter_kw,
          filter_kw={'computer_guid':self.computer_guid_list[self.max_manager+self.max_server+i]})
        self.logger.debug("Kumo gateway "+str(i)+" guid: "+self.computer_guid_list[self.max_manager+self.max_server+i])

        partition_parameter_kw = {
          'gateway_address':gateway_partition.getConnectionParameter('address'),
          'gateway_port':gateway_partition.getConnectionParameter('port'),
          'host_address':self.host_address,
          'nb_thread':self.nb_thread,
          'nb_request':self.nb_request}

        self.logger.debug("Kumo tester "+str(i))
        partition = self.computer_partition.request(
          self.software_release_url,
          'kumo_tester',
          'kumo_tester'+str(i),
          partition_parameter_kw=partition_parameter_kw,
          filter_kw={'computer_guid':self.computer_guid_list[self.max_manager+self.max_server+i]})
      
        tester_partition_list.append(partition)
      
      for partition in tester_partition_list:
        self.logger.debug("Appending Kumo testers' url")
        self.tester_urls.append(partition.getConnectionParameter('url'))
      
      self.logger.debug("Before remove duplicates: %s" % str(self.tester_urls))
      self.tester_urls = list(set(self.tester_urls)) # remove duplicates
      self.logger.debug("After remove duplicates: %s" % str(self.tester_urls))
      self.manager_partition = manager_partition
      
      return True
      
    except:
      self.logger.debug(str(sys.exc_info()))
      self.logger.debug(Formatter().formatException(sys.exc_info()))
      return False

  def _add_kumo_server_node(self):
    try:
      partition_parameter_kw = {
        'manager_address':self.manager_partition.getConnectionParameter('address'),
        'manager_port':self.manager_partition.getConnectionParameter('port')}

      self.logger.debug("Adding a Kumo server node")
      partition = self.computer_partition.request(
        self.software_release_url,
        'kumo_server',
        'kumo_server'+str(self.node_count),
        partition_parameter_kw=partition_parameter_kw,
        filter_kw={'computer_guid':self.computer_guid_list[self.max_manager+self.node_count-1]})
      self.logger.debug("Kumo server "+str(self.node_count)+" guid: "+self.computer_guid_list[self.max_manager+self.node_count-1])
      
      # line made to crash the function call until we call slapgrid
      partition.getConnectionParameter('address')
      
      return True
      
    except:
      self.logger.debug(str(sys.exc_info()))
      self.logger.debug(Formatter().formatException(sys.exc_info()))
      return False

  def writeCSV(self, inputnames, outputname):
    output = csv.writer(open(outputname, 'wb'), delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    # Header
    output.writerow(['get sec', 'get MB', 'get Mbps', 'get req/sec', 'get usec/req'])
    
    for inputname in inputnames:
      l = []
      f = open(inputname, "r")
      lines = f.readlines()
      f.close()
      
      for i in range(8, lines.__len__()):
        if lines[i][0] != '[' and lines[i][0] != '-':
          l.append(re.findall(r'\d+\.\d+|\d+',lines[i])[0].replace('.', ','))
      
      output.writerow(l)

