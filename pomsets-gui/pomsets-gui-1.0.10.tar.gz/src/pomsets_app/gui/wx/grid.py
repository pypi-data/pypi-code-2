import wx
import wx.grid

import pypatterns.relational as RelationalModule
import pomsets.resource as ResourceModule

class Table(wx.grid.PyGridTableBase, ResourceModule.Struct):
    
    ATTRIBUTES = ['dataModel', 'columns', 'columnIndices']
    
    def __init__(self, dataModel, columns=None):
        wx.grid.PyGridTableBase.__init__(self)
        
        self.dataModel(dataModel)
        if columns is None:
            columns = dataModel.columns().keys()

        # at this point, columns is a list of column names
        self.columns(columns)
        self.columnIndices(dict(enumerate(columns)))

        return
    
    def GetNumberRows(self):
        """Return the number of rows in the grid"""
        return len(self.dataModel().rows())

    def GetNumberCols(self):
        """Return the number of columns in the grid"""
        return len(self.columns())

    def IsEmptyCell(self, rowIndex, col):
        """Return True if the cell is empty"""
        try:
            dataRow = self.dataModel().rows()[rowIndex]
        except IndexError:
            return True
        return False

    def getIndexForColumn(self, columnName):
        return self.columns().index(columnName)
    
    def getObjectAt(self, rowIndex, colIndex):
        try:
            dataRow = self.dataModel().rows()[rowIndex]
            columnName = self.columnIndices()[colIndex]
            obj = dataRow.getColumn(columnName)
            return obj
        except IndexError:
            # need to catch this because of a bug with PyGridTableBase
            pass
        return ''
    
    def GetTypeName(self, row, col):
        """Return the name of the data type of the value in the cell"""
        obj = self.getObjectAt(row, col)
        
        if type(obj) is str:
            return None
        
        return obj.__class__.__name__

    def GetValueAsCustom(self, row, col, typeName):
        
        if self.GetTypeName(row, col) == typeName:
            obj = self.getObjectAt(row, col)
            return obj
        
        return self.GetValue(row, col)
    
    
    def GetValue(self, row, col):
        """Return the value of a cell"""
        
        obj = self.getObjectAt(row, col)
        
        # TODO:
        # there needs to be something that converts
        # the object in the data model into the value to be displayed
        
        return obj
    

    def SetValue(self, row, col, value):
        """Set the value of a cell"""
        dataRow = self.dataModel().rows()[row]
        columnName = self.columnIndices()[col]
        
        # TODO:
        # there needs to be something that converts 
        # the value displayed into the object in the data model
        
        dataRow.setColumn(columnName, value)
        pass


    def GetColLabelValue(self, col):
        return self.columnIndices()[col]
    
    
    # END class Table
    pass

