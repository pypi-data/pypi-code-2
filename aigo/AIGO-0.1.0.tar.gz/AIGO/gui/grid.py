"""
grid.py

AIGO is a python library for
the Analysis and Inter-comparison of Gene Ontology functional annotations.
see (http://code.google.com/p/aigo).
        
Created by Michael Defoin-Platel on 21/02/2010.
Copyright (c) 2010. All rights reserved.

AIGO is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx
import wx.grid

from pylab import *

class StatisticsTable(wx.grid.PyGridTableBase):
    def __init__(self, data=[[]], rowLabels=[], colLabels=[]):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.rowLabels = rowLabels
        self.colLabels = colLabels


    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        try:
            return len(self.data[0])
        except IndexError:
            return 0

    def GetRowLabelValue(self, row):
        if row < len(self.rowLabels):
            return self.rowLabels[row]
        else:
            return None

    def GetColLabelValue(self, col):
        if col < len(self.colLabels):
            return self.colLabels[col]
        else:
            return None
        
    def IsEmptyCell(self, row, col):
        return self.data[row][col]==None

    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return None

    def SetValue(self, row, col, value):
        data[row][col]=value
    

class StatisticsGrid(wx.grid.Grid):

    def __init__(self, parent, *args, **kwargs):
        wx.grid.Grid.__init__(self, parent, *args, **kwargs)
        table = StatisticsTable()
        self.SetTable(table)

    def UpdateData(self, aspect, allFA, allStatistics, colLabels, rowLabels):

        t=self.GetTable()
        t.data=[]
        for statistics in allStatistics:
            row=[]
            for FA in allFA:
                if FA.has_key(statistics):
                    d=FA[statistics][aspect]
                    if type(d)==list:
                        d=mean(d)
                    row.append("%.2f" %d)
                else:
                    row.append(None)
                    
            t.data.append(row)
                
        t.colLabels=colLabels
        t.rowLabels=rowLabels
        self.SetTable(t)
        self.ForceRefresh()

    class _PropertyGrid( wx.grid.Grid ):
        def SetTable( self, object, *attributes ):
                self.tableRef = weakref.ref( object )
                return wxGrid.SetTable( self, object, *attributes )
        def GetTable( self ):
                return self.tableRef()

#----------------------------------------------------------------------------------------

