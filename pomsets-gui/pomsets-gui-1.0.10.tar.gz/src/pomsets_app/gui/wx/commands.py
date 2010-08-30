import wx
import wx.grid

import pypatterns.command as CommandModule

import pypatterns.filter as FilterModule

import pypatterns.relational as RelationalModule
import pypatterns.relational.commands as RelationalCommandModule

# possible notification messages
#['GRIDTABLE_NOTIFY_COLS_APPENDED', 'GRIDTABLE_NOTIFY_COLS_DELETED',
#'GRIDTABLE_NOTIFY_COLS_INSERTED', 'GRIDTABLE_NOTIFY_ROWS_APPENDED',
#'GRIDTABLE_NOTIFY_ROWS_DELETED', 'GRIDTABLE_NOTIFY_ROWS_INSERTED',
#'GRIDTABLE_REQUEST_VIEW_GET_VALUES', 'GRIDTABLE_REQUEST_VIEW_SEND_VALUES']


class NotifyGridCommand(CommandModule.Command):
    
    def __init__(self, grid, executeIfUndo=False):
        CommandModule.Command.__init__(self)
        self._grid = grid
        self._executeIfUndo = executeIfUndo
        return

    
        
    def execute(self):
        if self._executeIfUndo:
            return

        msg = self.buildMessageForExecute()

        self._grid.ProcessTableMessage(msg)
        
        return
    
    def unexecute(self):
        if not self._executeIfUndo:
            return
        
        msg = self.buildMessageForUnexecute()
        
        self._grid.ProcessTableMessage(msg)
        
        return
    
    # END class NotifyGridCommand
    pass


class NotifyValueChangedCommand(NotifyGridCommand):

    def buildMessageForExecute(self):
        msg = wx.grid.GridTableMessage(
            self._grid.GetTable(),
            wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES
        )
        return msg

    def buildMessageForUnexecute(self):
        
        # it's the same thing to notify a value changed
        # because of an undo
        return self.buildMessageForExecute()
    
    pass
    
    
class NotifyRowAddedCommand(NotifyGridCommand):

    
    def buildMessageForExecute(self):
        # tell the grid we've added a row
        msg = wx.grid.GridTableMessage(
            self._grid.GetTable(),
            wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
            1
        )
        return msg
    
    def buildMessageForUnexecute(self):
        # tell the grid we've added a row
        msg = wx.grid.GridTableMessage(
            self._grid.GetTable(),
            wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
            1
        )
        return msg
    

    # END class NotifyRowAddedCommand
    pass


class NotifyGridCommandBuilder(CommandModule.CommandBuilder):
    """
    command builder for the notify grid command classes
    """
    
    def __init__(self, command, notifyCommandClass, grid):
        CommandModule.CommandBuilder.__init__(self, command)
        self._notifyCommandClass = notifyCommandClass
        self._grid = grid
        return
    
    def addCommandsPreExecute(self, commands):

        commands.append(
            self._notifyCommandClass(self._grid, executeIfUndo=True)
        )
        
        return

    def addCommandsPostExecute(self, commands):
        commands.append(
            self._notifyCommandClass(self._grid, executeIfUndo=False)
        )
        return

    # END class NotifyGridCommandBuilder
    pass

    
class UpdateGridCellValueCommandBuilder(CommandModule.CommandBuilder):

    def __init__(self, command, grid, rowFilter, column, value):
        """
        @param grid the wx.Grid
        """
        CommandModule.CommandBuilder.__init__(self, command)
        self._grid = grid
        self._column = column
        self._rowFilter = rowFilter
        self._value = value
        return

    def getValueToSet(self):
        return self._value
    
    def addCommandsPostExecute(self, commands):
        
        dataModel = self._grid.GetTable().dataModel()
        for row in dataModel.retrieveForModification(self._rowFilter):
            command = CommandModule.CompositeCommand()
            setValueCommand = RelationalCommandModule.SetColumnValueCommand(
                row, self._column, self.getValueToSet()
            )
            
            command.addCommand(setValueCommand)
            command.addCommandBuilder(
                setValueCommand,
                NotifyGridCommandBuilder(
                    setValueCommand, NotifyValueChangedCommand, self._grid
                )
            )
            
            commands.append(command)
            pass
        
        return

    # END class UpdateGridCellValueCommandBuilder
    pass

class SetVmThreadCommandBuilder(UpdateGridCellValueCommandBuilder):
    def __init__(self, command, grid, vmInstance):
        UpdateGridCellValueCommandBuilder.__init__(
            self, command, grid, 
            RelationalModule.ColumnValueFilter(
                'Instance ID',
                FilterModule.EquivalenceFilter(vmInstance)
            ),
            'Thread',
            None
        )
        return
    
    def getValueToSet(self):
        return self._command._worker
    
    # END class SetVmThreadCommandBuilder
    pass


class UnsetVmThreadCommandBuilder(UpdateGridCellValueCommandBuilder):
    def __init__(self, command, grid):
        UpdateGridCellValueCommandBuilder.__init__(
            self, command, grid, 
            RelationalModule.ColumnValueFilter(
                'Instance ID',
                FilterModule.EquivalenceFilter(command._vmInstance)
            ),
            'Thread',
            None
        )
        return
    
    def getValueToSet(self):
        return RelationalModule.Table.NULL
    
    # END class UnsetVmThreadCommandBuilder
    pass
