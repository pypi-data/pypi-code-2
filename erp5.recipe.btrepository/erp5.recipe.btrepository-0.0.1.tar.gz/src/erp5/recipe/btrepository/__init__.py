##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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

import os
import logging
import zc.buildout
import zc.buildout.easy_install
import zc.recipe.egg

class Recipe(object):
  def __init__(self, buildout, name, options):
    self.buildout, self.options, self.name = buildout, options, name
    self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
    self.logger = logging.getLogger(self.name)

    options.setdefault('location',
                   os.path.join(
                     buildout['buildout']['parts-directory'],
                     self.name))
    options.setdefault("download-command", 
                   "svn co --trust-server-cert --non-interactive --quiet")
    options.setdefault("download-command-extra",
                       "")
    options.setdefault("download_folder", 
                   "%s__download__" % options.get('location'))
    options.setdefault("preserve-download", "1")
    options.setdefault("auto-build", "0")

  def _get_download_command(self):
    """ Build appropriate download command"""
    options = self.options
    return " ".join([options.get("download-command"),
              options.get("download-command-extra")])

  def install_script(self):
    """ Create default scripts
    """
    options = self.options
    url = options.get("url")
    requirements, ws = self.egg.working_set(['erp5.recipe.btrepository'])
    script_name = "%s_update" % self.name
    scripts = zc.buildout.easy_install.scripts(
        [(script_name,'erp5.recipe.btrepository', 'builder')],
        ws, options['executable'], "bin",
        arguments = ("\n        url_list = %s ,     "
                     "\n        destination = '%s' ,"
                     "\n        download_dir = '%s',"
                     "\n        download_cmd = '%s'," 
                     "\n        preserve_download = %s " % (
                                      url.split(),
                                      options.get('location'),
                                      options.get("download_folder"),
                                      self._get_download_command(),
                                      int(options.get("preserve-download")))))

  def install(self):
    options = self.options
    if not os.path.exists(options.get("location")):
      os.mkdir(options.get("location"))
    self.install_script()
    if int(options.get("auto-build")):
      builder(options.get("url").split(), 
              options.get('location'), 
              options.get("download_folder"), 
              self._get_download_command(), 
              int(options.get("preserve-download")))
    return []

  update = install

def builder(url_list, destination, download_dir, download_cmd, preserve_download):
  """ Wrapper to use erp5.utils.dists API from a script
      created by buildout.
  """
  from erp5.utils.dists import repository
  return repository.build(
          url_list,
          destination,
          download_dir,
          download_cmd,
          preserve_download)

