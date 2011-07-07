# sidepanel.py    [Sudoku Solver 1.0]
# -*- coding: UTF-8 -*-

__author__ = "Pushpak Dagade (पुष्पक दगड़े)"
__date__   = "$May 22, 2011 5:15:52 PM$"

import time
import wx
from logic import SolveSudokuPuzzle
from solutionbox import SolutionBox

class SidePanel(wx.Panel):
    """Creates a Panel widget which contains a solutionbox.SolutionBox
    widget and 4 buttons widgets - Save, Revert, Clear and Solve."""
    
    def __init__(self, parent, sudokupanel):
        super(SidePanel, self).__init__(parent, -1,
          style = wx.NO_BORDER|wx.TAB_TRAVERSAL)

        # Attributes.
        self.sudokupanel = sudokupanel
        self.SavedPuzzle = None

        # Create children widgets.
        self.solutionbox = SolutionBox(self)
        self.buttonSave = wx.Button(self, -1, 'Save')
        self.buttonRevert = wx.Button(self, -1, 'Revert')
        self.buttonClear = wx.Button(self, -1, 'Clear')
        self.buttonSolve = wx.Button(self, -1, 'Solve')
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.GridSizer(2,2)
        sizer.Add(self.solutionbox, proportion=1,
          flag=wx.EXPAND|wx.ALL, border=3)
        sizer.Add(sizer2, flag=wx.EXPAND, proportion=0)
        sizer2.Add(self.buttonSave,
          flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, border=2.5)
        sizer2.Add(self.buttonRevert,
          flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, border=2.5)
        sizer2.Add(self.buttonClear,
          flag=wx.EXPAND|wx.RIGHT|wx.TOP, border=2.5)
        sizer2.Add(self.buttonSolve,
          flag=wx.EXPAND|wx.LEFT|wx.TOP, border=2.5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        # Bind events.
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.buttonSave)
        self.Bind(wx.EVT_BUTTON, self.OnRevert, self.buttonRevert)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.buttonClear)
        self.Bind(wx.EVT_BUTTON, self.OnSolve, self.buttonSolve)

    def OnSave(self, *args):
        """Save the current state of the Sudoku puzzle.
        Overwrite, if any, previously saved puzzle."""
        self.SavedPuzzle = self.sudokupanel.GetPuzzle()
        print '[Sudoku puzzle Saved]'

    def OnRevert(self, *args):
        """Clear the grid and load a perviously saved puzzle, if any.
        If there is no previously saved puzzle, just clear off the grid."""
        self.sudokupanel.SetPuzzle(self.SavedPuzzle)
        print '[Saved Sudoku puzzle restored]'

    def OnClear(self, *args):
        """Clear off the grid for a fresh start."""
        self.sudokupanel.ClearPuzzle()
        self.solutionbox.Clear()

    def OnSolve(self, *args):
        """Try to solve the Sudoku puzzle.
        Also print the time taken in this process."""

        # Check if the grid is not empty before proceeding.
        if self.sudokupanel.IsGridEmpty():
            print '[Nothing to solve]'
            return

        # Record the start and end time before and after solving
        # the puzzle respectively.
        t0 = time.time()
        SolveSudokuPuzzle(self.sudokupanel)
        t1 = time.time()
        print "[Solve process took %.2f sec.]" %(t1-t0)

        # If the sudoku puzzle is not complete and is incorrect, then it
        # means that the puzzle provided initially was incorrect because of
        # which it could not be solved.
        if not self.sudokupanel.IsPuzzleCorrect():
            messagebox = wx.MessageDialog(self, "The puzzle you provided was"
              " incorrect and hence it could not be solved." ,
              caption='Incorrect puzzle provided',
              style=wx.OK|wx.ICON_ERROR)
            messagebox.ShowModal()
            messagebox.Destroy()
        elif not self.sudokupanel.IsPuzzleComplete():
            messagebox = wx.MessageDialog(self, "The puzzle you provided" 
              " had insufficient data and hence was not solved. (This "
              "puzzle will have many distinct solutions.)",
              caption='Insufficient puzzle data provided',
              style=wx.OK|wx.ICON_EXCLAMATION)
            messagebox.ShowModal()
            messagebox.Destroy()
