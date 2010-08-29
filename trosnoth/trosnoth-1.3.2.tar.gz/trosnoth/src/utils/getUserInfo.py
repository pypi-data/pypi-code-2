# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trosnoth.data import getPath, user, makeDirs
from trosnoth.src.trosnothgui.defines import *
import os

def getName():
    nameFilename = getPath(user, 'name')
    try:
        nameFile = open(nameFilename, 'r')
        name = nameFile.read()[:maxNameLength]
        nameFile.close()
        return name
    except IOError:
        return None

def writeName(name):
    nameFilename = getPath(user, 'name')
    nameFile = open(nameFilename , 'w')
    nameFile.write(name)
    nameFile.close()

def isFirstTime():
    firstTimeFilename = getPath(user, 'first')
    return not os.path.exists(firstTimeFilename)
      
def notFirstTime():
    firstTimeFilename = getPath(user, 'first')
    open(firstTimeFilename, 'w').close()
