## -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
$Id: utils.py 226111 2010-11-05 12:41:16Z mborch $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

import os

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

# Archetypes imports
from Products.Archetypes.Field import ImageField
#from FileSystemStorage import FileSystemStorage

import config

def getFieldValue(self, name):
    """Returns field value of an object

    @param name: Name of the field
    """

    field = self.getField(name)
    if not field:
        # Get Image fields
        # Check for scales
        found = False
        fields = [x for x in self.Schema().fields() if isinstance(x, ImageField)]
        for field in fields:
            field_name = field.getName()
            names = ['%s_%s' % (field_name, x) for x in field.getAvailableSizes(self).keys()]
            if name in names:
                obj = field.getStorage(self).get(name, self)
                found = True
                break
        if not found:
            raise AttributeError(name)
        return obj.__of__(self)

    # Standard field
    accessor = field.getAccessor(self)

    if accessor is None:
        return None

    return accessor()


FSSMessageFactory = MessageFactory(config.I18N_DOMAIN)
ModuleSecurityInfo('iw.fss.utils').declarePublic('FSSMessageFactory')

###
## File management utilities
###

def rm_file(path):
    """
    Delete file from a path
    """

    os.remove(path)

def move_file(infile, outfile):
    """
    Move file to another place
    """

    if infile == outfile:
        # SiteStorageStrategy can send equals infile and outfile
        return

    if os.path.exists(outfile) and infile != outfile:
        os.remove(outfile)

    os.rename(infile, outfile)


def copy_file(infile, outfile):
    """

    Read binary data from infile and write it to outfile. infile and
    outfile my be strings, in which case a file with that name is
    opened, or filehandles, in which case they are accessed directly.

    """

    if isinstance(infile, basestring):
        instream = open(infile, 'rb')
        close_in = 1
    else:
        close_in = 0
        instream = infile

    if isinstance(outfile, basestring):
        outstream = open(outfile, 'wb')
        close_out = 1
    else:
        close_out = 0
        outstream = outfile
    try:
        blocksize = 2<<16
        instream.seek(0, 0)
        block = instream.read(blocksize)
        outstream.write(block)
        while len(block)==blocksize:
            block = instream.read(blocksize)
            outstream.write(block)
        instream.seek(0,0)
    finally:
        if close_in: instream.close()
        if close_out: outstream.close()

def create_file(contents_file, target_filepath):
    """
    Creates a physical file on the filesystem at target_filepath.  If
    contents_file is not None, it points to a file whose contents will
    be copied into the target file.  Otherwise, a zero length file
    will be created.  This method will raise an exception if there are
    any problems writing to the target file (or reading
    contents_file).
    """

    if contents_file:
        copy_file(contents_file, target_filepath)
    else:
        touchfile = open(target_filepath, 'wb') # create zero-length file
        touchfile.close()


###
## Upgrade steps decorator
###

# Background: GenericSetup shows upgrade steps for components that are
# *not* installed in the site, and let the Manager execute these
# upgrade steps. This is somehow harmful. While this bug is not fixed,
# this safety belt will prevent managers executing the exposed upgrade
# steps.
# See https://dev.plone.org/plone/ticket/8507
# Usage:
#
#  @IfInstalled('Collage')
#  def someUpgradeScript(setuptool):
#      # Usual upgrade script

from zope.app.component.hooks import getSite

class NotInstalledComponent(LookupError):
    def __init__(self, cpt_name):
        self.cpt_name = cpt_name
        return

    def __str__(self):
        msg = ("Component '%s' is not installed in this site."
               " You can't run its upgrade steps."
               % self.cpt_name)
        return msg

class IfInstalled(object):
    def __init__(self, prod_name=config.PROJECTNAME):
        """@param prod_name: as shown in quick installer"""
        self.prod_name = prod_name

    def __call__(self, func):
        """@param func: the decorated function"""
        def wrapper(setuptool):
            qi = getSite().portal_quickinstaller
            installed_ids = [p['id'] for p in qi.listInstalledProducts()]
            if self.prod_name not in installed_ids:
                raise NotInstalledComponent(self.prod_name)
            return func(setuptool)
        wrapper.__name__ = func.__name__
        wrapper.__dict__.update(func.__dict__)
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        return wrapper

###
## Zope2 vs Zope3 interfaces
###

# Since Plone 4, Archetypes provides only Zope3 style interfaces, since the
# (deprecated) Interface package has gone with Zope 2.12
# Then we must add this to support both Zope 2 and Zope 3 interfaces transparently.
# In addition, we can't use Zope version API because buildout breaks the
# App/version.txt file (known but not yet fixed bug)


from zope.interface import Interface as Z3Interface
from zope.interface.interface import InterfaceClass as Z3InterfaceClass
def objectImplements(interf, obj):
    if isinstance(interf, Z3Interface) or isinstance(interf, Z3InterfaceClass):
        return interf.providedBy(obj)
    else:
        return interf.isImplementedBy(obj)
