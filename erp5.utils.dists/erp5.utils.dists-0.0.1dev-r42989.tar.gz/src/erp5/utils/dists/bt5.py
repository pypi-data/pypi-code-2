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
import tarfile
import os

def compress_business_template(destination, source):
  t = tarfile.open(destination, "w:gz")
  def exclude_svn(filemane):
    return ".svn" in filemane
  t.add(source, exclude=exclude_svn)
  t.close()

def compress_business_template_list(destination, source):
  """ Compress all business templates from source directory 
      into destination directory
  """
  current_dir = os.getcwd()
  os.chdir(source)
  for bt in os.listdir("."):
    if not bt.startswith(".") and os.path.isdir(bt):
      compress_business_template("%s/%s.bt5" % (destination,bt), bt)

def main():
  import sys
  if len(sys.argv) == 2:
    destination = sys.argv[1]
  source = "."

  if len(sys.argv) == 3:
    source = sys.argv[2]

  if len(sys.argv) not in [2, 3]:
    print """ ERROR wrong arguments, USAGE:
  $ bt5_build_from_folder DESTINATION SOURCE"""
    sys.exit(1)

  compress_business_template_list()

if __name__ == "__main__":
  main()
