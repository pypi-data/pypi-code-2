# Copyright (C) 2002-2006 gocept gmbh & co.kg, 06112 Halle(Saale), Germany
# Christian Zagrodnick, cz@gocept.com
# Michael Howitz, mh@gocept.com
# $Id: Render.py 31512 2010-12-14 10:13:34Z mac $
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

import copy

class Render:

    def __init__(self, new, old=None):
        self.new=new
        self.old=old
    
    def generateLayout(self):
        if self.old is None:
            return self._layoutFull()
        else:
            return self._layoutDiff()

    def _layoutFull(self):
        raise NotImplementedError, "Implemented in sub classes" 

    def _layoutDiff(self):
        raise NotImplementedError, "Implemented in sub classes" 

    def _oldTables(self):
        return self.old.tables.values()

    def _newTables(self):
        return  self.new.tables.values()

    def _removedTables(self):
        return [t
            for t in self._oldTables()
            if t not in self._newTables()
            ]

    def _addedTables(self):
        return [t
            for t in self._newTables()
            if t not in self._oldTables()
            ]
            
    def _remainingTables(self):
        return [t
            for t in self._oldTables() + self._newTables()
            if t not in self._removedTables()
            if t not in self._addedTables()
            ]


    def _dropedFields(self):
        return [(table,field)
            for table in self._oldTables()
            for table2 in self._newTables()
            if table.name==table2.name
            for (field,attr) in table.attrlist
            if field not in map(lambda (x,y): x, table2.attrlist)
            ]

    def _addedFields(self):
        return [(table,(field,attr))
            for table2 in self._oldTables()
            for table in self._newTables()
            if table.name==table2.name
            for (field,attr) in table.attrlist
            if field not in map(lambda (x,y): x, table2.attrlist)
            ]
            
    def _dropedConstraints(self):
        return [(table,constraint)
            for table in self._oldTables()
            for table2 in self._newTables()
            if table.name==table2.name
            for constraint in table.clist
            if constraint not in table2.clist
            ]

    def _addedConstraints(self):
        return [(table,constraint)
            for table in self._newTables()
            for table2 in self._oldTables()
            if table.name==table2.name
            for constraint in table.clist
            if constraint not in table2.clist
            ]

    def _oldRelations(self):
        return self.old.relations

    def _newRelations(self):
        return self.new.relations
    

    def _removedRelations(self):
        return [r
            for r in self._oldRelations()
            if r not in self._newRelations()
        ]
    
    def _addedRelations(self):
        return [r
            for r in self._newRelations()
            if r not in self._oldRelations()
        ]

    def _getOrder(self, state):
        TABLES = state.tables
        PARENT = state.parent
        k = TABLES.keys()
        dim = len(TABLES.keys())
        matrix = dim*[dim*[0]]
        
        # adjazenzmatrix aufbauen und reflexive huelle bilden
        for i in xrange(0, len(matrix)):
            matrix[i] = copy.deepcopy(matrix[i])
            for j in xrange (0, len(matrix)):
                if (PARENT.get(k[i], 0) == k[j]) or i == j:
                    matrix[i][j] = 1

        # transitive Huelle bilden
        # Algorithmus nach Warshall 
        # http://www.informatik.uni-frankfurt.de/~zinndorf/haskell/mathe.htm
        for k in xrange(0, len(matrix)): 
            for zeile in xrange(0, len(matrix)):
                for spalte in xrange(0, len(matrix)): 
                    if not matrix[zeile][spalte]:
                        matrix[zeile][spalte] = (matrix[zeile][k] and
                                                 matrix[k][spalte])
        
        # Die Antisymetrie zu ueberpruefen spar ich mir; wenn der user nicht
        # ganz doof ist passt das schon mit der halbordnungsrelation
        
        # sortierung
        sorted = []
        
        for k in xrange(0, len(matrix)):
            max = 0
            maxid = 0

            for i in xrange(0, len(matrix)):
                sum = 0
                for j in xrange(0, len(matrix)):
                    sum = sum + matrix[j][i]
                if sum > max:
                    max = sum
                    maxid = i

            sorted = sorted + [TABLES.keys()[maxid]]
            for j in xrange(0, len(matrix)):
                matrix[j][maxid] = 0

        return sorted
