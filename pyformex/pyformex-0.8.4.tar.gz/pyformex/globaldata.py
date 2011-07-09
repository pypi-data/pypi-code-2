#!/usr/bin/env python pyformex
# $Id$
##
##  This file is part of pyFormex 0.8.4 Release Sat Jul  9 14:43:11 2011
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Homepage: http://pyformex.org   (http://pyformex.berlios.de)
##  Copyright (C) Benedict Verhegghe (benedict.verhegghe@ugent.be) 
##  Distributed under the GNU General Public License version 3 or later.
##
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see http://www.gnu.org/licenses/.
##

"""A class to hold the pyFormex global data.. 

This module defines the :class:`GlobalData`, which is the structure used by
pyFormex to store the global data exported from the scripts.
This allows for data persistence between different invocations of
the same script or to transfer data from one script to another. 
The data are kept in memory until they are removed or overwritten by the user,
or until pyFormex shuts down.

The :module:`project` provides further functionality to create
persistence of data over different sessions of pyFormex. 
"""

class Database(dict):
    """A dictionary with Freeze capability.

    """
    def __init__(self,data={}):
        dict.__init__(self,data)
        self._frozen_ = True

    def freeze(self):
        self._frozen_ = True

    def thaw(self):
        self._frozen_ = False

    def frozen(self):
        return self._frozen_

    def __setitem__(self,key,value):
        """Allows items to be set using self[key] = value."""
        self._frozen_ = False
        dict.__setitem__(self,key,value)
        

class SubDict(object):
    """A selection from a Database.

    A SubDict is a dictionary with items from a parent dictionary
    that fullfill certain requirements.

    - clas: a class name: if specified, only instances of this class will be
      returned
    - like: a string: if given, only object names starting with this string
      will be returned
    - filter: a function taking an object name as parameter and returning True
      or False. If specified, only objects passing the test will be returned.
    """
    def __init__(self,parent,clas=None,like=None,filter=None): 
        """Create a new ssubdict of a parent dict."""
        self.parent = parent
        self.clas = clas
        self.like = like
        self.filter = filter
        self.names = []
        self.freeze()


    def filter(self,names):
        """Run the specified names through the filters.

        names is a list of keys to be run through the current filters
        of the parent.
        """
        parent.freeze()
        if names is None:
            names = dic.keys()
            
        if clas is not None:
            names = [ n for n in names if isinstance(dic[n],clas) ]
        if like is not None:
            names = [ n for n in names if n.startswith(like) ]
        if filter is not None:
            names = [ n for n in names if filter(n) ]
        return names


    def freeze(self):
        """Run the names through the filters.

        names is a list of names, or if not specified, the list of names
        of the parent.
        """
        parent.freeze()
        if names is None:
            names = dic.keys()
            
        if clas is not None:
            names = [ n for n in names if isinstance(dic[n],clas) ]
        if like is not None:
            names = [ n for n in names if n.startswith(like) ]
        if filter is not None:
            names = [ n for n in names if filter(n) ]
        return names


    def __getitem__(self, key):
        """Allows items to be addressed as self[key].

        """
        if not self.parent.frozen():
            self.filternames()

        if key in self.names:
            return parent[key]
        else:
            return None

    def keys():
        """Return all the current keys."""
        
    return dict([ (k,d[k]) for k in keys if k in d ])

    def __str__(self):
        if not self.parent.frozen():
            self.filternames()
        


if __name__ == '__main__':

    D = Database(dict(
        a = 'hallo',
        b = 'HELLO',
        c = 10,
        d = 25.4,
        e = (4,3),
        extra = 'MORE',
        ))
    print D
    E = SubDict(D)
    print E
    print  E['a']
    
 
# End

