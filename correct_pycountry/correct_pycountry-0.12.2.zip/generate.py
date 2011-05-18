# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Generate the necessary data files and directory structures from the Debian
project's data."""

from __future__ import with_statement 
 
import glob
import os.path
import shutil
import subprocess

import polib


def replaceWrongCountryName(fileName):
    """Replace wrong country name 'Taiwan, Province of China' as 
    'Taiwan, Republic of China'
    
    @param fileName: file to replace
    """
    with open(fileName, 'rt') as file:
        content = file.read()
        content = content.replace('Taiwan, Province of China', 
                                  'Taiwan, Republic of China')
    with open(fileName, 'wt') as file:
        file.write(content)        
 
data_dir = os.path.join('parts', 'data')
base_dir = os.path.join('src', 'pycountry')
 
assert os.path.exists(base_dir), 'pycountry src directory not found'
#assert os.path.exists(data_dir), 'pkg-isocodes data directory not found'
 
database_dir = os.path.join(base_dir, 'databases')
locales_dir = os.path.join(base_dir, 'locales')
 
 
STANDARDS = {'639': os.path.join(data_dir, 'iso_639'),
             '3166': os.path.join(data_dir, 'iso_3166'),
             '3166_2': os.path.join(data_dir, 'iso_3166_2'),
             '4217': os.path.join(data_dir, 'iso_4217'),
             '15924': os.path.join(data_dir, 'iso_15924')}
 
 
# Put the database files in place
if not os.path.exists(database_dir):
    os.mkdir(database_dir)
 
for standard, standard_dir in STANDARDS.items():
    src = os.path.join(standard_dir, 'iso_%s.xml' % standard)
    dst = os.path.join(database_dir, 'iso%s.xml' % standard)
    shutil.copyfile(src, dst)
    replaceWrongCountryName(dst)
    print 'Replace wrong country name in %s' % dst
 
 
# Put the PO files in place and compile them
for standard, standard_dir in STANDARDS.items():
    for src in glob.glob(os.path.join(standard_dir, '*.po')):
        print 'Replace wrong country name in %s' % src
        replaceWrongCountryName(src)
        
        print src
        dir, locale = os.path.split(src)
        locale = locale.replace('.po', '')
 
        dst_dir = os.path.join(locales_dir, locale, 'LC_MESSAGES')
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
 
        dst = os.path.join(dst_dir, 'iso%s.po' % standard)
        dst_mo = dst.replace('.po', '.mo')
 
        shutil.copyfile(src, dst)
        print src, " -> ", dst
 
        po = polib.pofile(src)
        po.save_as_mofile(dst_mo)
 
# Generate the MO files.
