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

import os
import shutil
import urllib2
import urlparse

from hurry.resource import generate_code, ResourceInclusion, Library

BASEURL = "http://code.jquery.com/"
VERSION = '1.4.3'
MINIFIED = "jquery-%s.min.js" % VERSION
FULL = "jquery-%s.js" % VERSION


def prepare_jquery(package_dir):
    jquery_dest_path = os.path.join(package_dir, 'jquery-build')

    # remove previous jquery library build
    print 'recursively removing "%s"' % jquery_dest_path
    shutil.rmtree(jquery_dest_path, ignore_errors=True)
    print 'create new "%s"' % jquery_dest_path
    os.mkdir(jquery_dest_path)

    for filename in [MINIFIED, FULL]:
        url = urlparse.urljoin(BASEURL, filename)
        print 'downloading "%s"' % url
        f = urllib2.urlopen(url)
        file_data = f.read()
        f.close()
        dest_filename = os.path.join(jquery_dest_path, filename)
        dest = open(dest_filename, 'wb')
        print 'writing data to "%s"' % dest_filename
        dest.write(file_data)
        dest.close()

    py_path = os.path.join(package_dir, '_lib.py')
    print 'Generating inclusion module "%s"' % py_path

    library = Library('jquery_lib', 'jquery-build')
    inclusion_map = {}
    inclusion = inclusion_map['jquery'] = ResourceInclusion(library, FULL)
    inclusion.modes['minified'] = ResourceInclusion(library, MINIFIED)
    code = generate_code(**inclusion_map)
    module = open(py_path, 'w')
    module.write(code)
    module.close()


def main():
    # Commandline tool
    prepare_jquery(os.path.dirname(__file__))

def working_entrypoint(data):
    if data['name'] != 'hurry.jquery':
        return
    prepare_jquery(os.path.dirname(__file__))

def tag_entrypoint(data):
    if data['name'] != 'hurry.jquery':
        return
    prepare_jquery(data['tagdir'] + '/src/hurry/jquery')
    
