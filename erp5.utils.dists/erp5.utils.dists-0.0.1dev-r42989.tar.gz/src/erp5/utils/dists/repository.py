#! /usr/bin/python
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
from optparse import OptionParser
try:
  from hashlib import md5
except ImportError:
  from md5 import new as md5
import os
import shutil
import genbt5list
from bt5 import compress_business_template_list

DOWNLOAD_COMMAND = "svn co --trust-server-cert --non-interactive -q"

def load_options():
  parser = OptionParser()
  parser.add_option("-u", "--url", dest="url",
                    help="URL where the business templates will be downloaded from", 
                    metavar="URL", 
                    default="https://svn.erp5.org/repos/public/erp5/trunk/bt5,"\
                            "https://svn.erp5.org/repos/public/erp5/trunk/products/ERP5/bootstrap")
  
  parser.add_option("-r", "--repository",
                    dest="repository", default=os.getcwd(),
                    help="where the .bt5 will be placed")

  parser.add_option("-d", "--download-dir",
                     dest="downloaddir", 
                     default=None,
                     help="Custom folder where download/checkout will be placed.")

  parser.add_option("-c", "--download-cmd",
                     dest="downloadcmd", 
                     default=DOWNLOAD_COMMAND,
                     help="Command used to download bt5 from URL")

  parser.add_option("-p", "--preserve-download",
                     dest="preserve_download", 
                     action="store_true",
                     default=False,
                     help="Do not erase download after build.")

  return parser.parse_args()

def build(url_list, destination,
         download_dir=None, 
         download_cmd=DOWNLOAD_COMMAND, 
         preserve_download=True):

  lock_path = os.path.join(destination, ".lock")
  workdir = os.path.join(destination, ".workdir")
  if download_dir is None:
    download_dir = os.path.join(destination, ".download")
  if os.path.exists(lock_path):
      raise ValueError("Lock file %s exists" % lock_path)

  try: 
    f = open(lock_path, "w+"); f.close()
    if not os.path.exists(download_dir):
      os.mkdir(download_dir)
    os.mkdir(workdir)
    for url in url_list:
      if url != "":
        os.chdir(download_dir)
        repos = md5(url).hexdigest()
        os.system("%s %s %s" % (download_cmd, url, repos))
        compress_business_template_list(workdir, repos)

    ### # Publish the repository
    for bt in os.listdir(workdir):
      bt_path = os.path.join(destination,bt)
      if os.path.exists(bt_path):
        os.remove(bt_path)
      shutil.move('%s/%s' % (workdir, bt), destination)
    
    os.chdir(destination)
    genbt5list._main()
  finally:
    if os.path.exists(lock_path):
      os.remove(lock_path)
    shutil.rmtree(workdir)
    if not preserve_download:
      shutil.rmtree(download_dir)
  return True

def main():
  (options, args) = load_options()
  build(url_list = options.url.split(","), 
        destination = options.repository, 
        download_dir=options.downloaddir,
        download_cmd=options.downloadcmd,
        preserve_download=options.preserve_download
       )

if __name__ == "__main__":
  main()
