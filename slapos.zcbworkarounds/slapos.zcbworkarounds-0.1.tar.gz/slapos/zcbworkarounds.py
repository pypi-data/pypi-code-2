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
import logging
import os

def extension(buildout):
  Workaround(buildout)()

class Workaround:
  def __init__(self, buildout):
    self.buildout = buildout
    self.logger = logging.getLogger(__name__)

  def __call__(self):
    self.workaround_openoffice_bin_zc163776()

  def workaround_openoffice_bin_zc163776(self):
    """Workaround for: https://bugs.launchpad.net/zc.buildout/+bug/163776"""
    installed_path = self.buildout['buildout']['installed']
    if not os.path.exists(installed_path):
      return
    installed = open(installed_path).read()
    if 'z3c.recipe.openoffice==0.3.1dev' in installed:
      self.logger.warn('Fixing issue #163776 for z3c.recipe.openoffice')
      open(installed_path, 'w').write(installed.replace(
        'z3c.recipe.openoffice==0.3.1dev', 'z3c.recipe.openoffice'))
