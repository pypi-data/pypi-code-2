##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Leonardo Rochael Almeida <leonardo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
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

import time

class Sleeper(object):
    """This class exists solely to inflate the stack trace, and to be in a
    file where the stack trace won't be affected editing of the test file that
    uses it
    """

    def __init__(self, interval):
      self.interval = interval

    def sleep(self):
        self._sleep1()

    def _sleep1(self):
        self._sleep2()

    def _sleep2(self):
        time.sleep(self.interval)

class App(object):

    def __call__(self, interval):
        Sleeper(interval).sleep()
        return "OK"

# Enable this module to be published with ZPublisher.Publish.publish_module()
bobo_application = App()
