# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: stefaan.himpe@gmail.com

class IncludeFile(object):
    """
    Class to hold an include file.
    It can distinguish between different types of include files, like
    ("Angular" or "Quoted")
    Angular: #include <blahblah.h>
    Quoted:  #include "blahblah.h"
    """
    def __init__(self, name, include_type):
        """
        initialize this class with a
        * name: the name of the include file
        * type: whether it's an <angular> or "quoted" include 
        """
        self.name = name
        self.include_type = include_type
    
    def __repr__(self):
        """
        generate a representation of this file for using in 
        debug messages
        """
        return "IncludeFile('"+self.name+"','"+self.include_type+"')"

