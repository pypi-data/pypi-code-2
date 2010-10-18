##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import py
import os
import shutil
import urllib2
import urlparse
import zipfile

VERSION = '1.2.5'
BASEURL = "http://cdn.jquerytools.org/%s/all/jquery.tools.min.js" %VERSION
FILENAME = "jquery.tools.min.js"

def prepare_jquerytools(package_path):
    library_path = package_path.join("jquerytools-build")

    # remove previous slimbox library
    print 'recursivly removing "%s"' % library_path
    if library_path.check():
        library_path.remove()
    print 'create new "%s"' % library_path 
    library_path.ensure(dir=True)

    url = BASEURL
    print 'downloading "%s"' % url
    f = urllib2.urlopen(url)
    file_data = f.read()
    f.close()
    dest_filename = library_path.join(FILENAME)
    print 'writing data to "%s"' % dest_filename
    dest_filename.write(file_data)

def main():
    prepare_jquerytools(py.path.local(os.path.dirname(__file__)))

def working_entrypoint(data):
    if data['name'] != 'hurry.jquerytools':
        return
    prepare_jquerytools(py.path.local(os.path.dirname(__file__)))

def tag_entrypoint(data):
    if data['name'] != 'hurry.jquertools':
        return
    prepare_jquerytools(py.path.local(data['tagdir'] + '/src/hurry/jquerytools'))
