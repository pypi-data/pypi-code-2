# Copyright (C) 2002 gocept gmbh & co.kg, 06366 Koethen/Anahlt, Germany
# Christian Zagrodnick, cz@gocept.com
# $Id: Constraint.py 31512 2010-12-14 10:13:34Z mac $
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA





class Constraint:
    name=""
    rule=""
    
    def __init__(self,name,rule):
        self.name=name
        self.rule=rule

        

    def __eq__(self,other):
        if(self.name==other.name) and (self.rule==other.rule):
            return 1
        return 0    

