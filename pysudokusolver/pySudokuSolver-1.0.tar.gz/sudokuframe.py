# sudokuframe.py    [Sudoku Solver 1.0]
# -*- coding: UTF-8 -*-

__author__ = "Pushpak Dagade (पुष्पक दगड़े)"
__date__   = "$May 21, 2011 7:40:09 PM$"

import os.path
import wx
from sudokupanel import SudokuPanel
from sidepanel import SidePanel

class SudokuFrame(wx.Frame):
    """Instance of this class will act as container for
    instances of classes SudokuPanel and SidePanel. It 
    also will be the top window."""
    
    def __init__(self, parent):
        super(SudokuFrame, self).__init__(parent, -1, 'Sudoku Solver')

        # Create children widgets.
        menubar = wx.MenuBar()
        menufile = wx.Menu()
        menufile.Append(0, 'E&xit\tCtrl+W')
        menuview = wx.Menu()
        menuview.Append(1,'&Full Screen\tF11', kind=wx.ITEM_CHECK)
        menuhelp = wx.Menu()
        menuhelp.Append(2,'&How To Use?')
        menuhelp.Append(3,'&About')
        menubar.Append(menufile, '&File')
        menubar.Append(menuview, '&View')
        menubar.Append(menuhelp, '&Help')
        self.SetMenuBar(menubar)

        self.panel1 = SudokuPanel(self)
        self.panel2 = SidePanel(self, self.panel1)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.panel1, proportion=3, border=10,
          flag=wx.SHAPED|wx.ALIGN_CENTER_HORIZONTAL|\
          wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        sizer.Add(self.panel2, flag=wx.EXPAND|wx.ALL,
          proportion=1, border=10)
        self.SetSizer(sizer)

        # Set size of frame according to screen size.
        displayrect = wx.Display().GetClientArea()
        sizey = (displayrect[3]-displayrect[0])*4/5
        sizex = sizey + self.panel2.GetClientSize()[0]
        size = (sizex, sizey)
        self.SetSize(size)

        # Set an icon (should work on both Windows and Linux platforms).
        path = os.path.join(os.path.dirname(__file__), "pics",
          "Sudoku Solver.ico")
        icon = wx.Icon(path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # Bind events.
        self.Bind(wx.EVT_MENU, self.OnExit, id=0)
        self.Bind(wx.EVT_MENU, self.OnFullscreen, id=1)
        self.Bind(wx.EVT_MENU, self.OnHowToUse, id=2)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=3)

    def OnExit(self, *args):
        """Safely exit the app."""
        self.Close(True)            # this triggers the window close event.

    def OnFullscreen(self, *args):
        """Span the entire screen, hiding even taskbars."""
        if args[0].IsChecked():
            self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        else:
            self.ShowFullScreen(False)

    def OnHowToUse(self, *args):
        """Show the How To Use dialog box."""
        strhowtouse = "How to enter numbers in the grid?\n"\
        "==================================\n"\
        "Scroll over cells to rotate through their permissible numbers.\n"\
        "\n"\
        "Buttons -\n"\
        "============\n"\
        "Save   - Saves the current puzzle.\n"\
        "Clear  - Clears the grid and the Solution Box.\n"\
        "Revert - Loads a saved puzzle.\n"\
        "Solve  - Solves the Sudoku puzzle in the grid.\n"\
        "\n"\
        "Solution Box -\n"\
        "============\n"\
        "It is more or less like a log box.\n" \
        "1. When a puzzle is solved (on clicking the Solve button),\n"\
        "it logs the steps taken to solve the puzzle.\n"\
        "2. Additionally, it also logs actions of the\n"\
        "buttons Save, Revert and Clear.\n"
        howtousebox = wx.MessageDialog(self, strhowtouse,
          caption='How To Use?', style=wx.OK)
        howtousebox.ShowModal()
        howtousebox.Destroy()

    def OnAbout(self, *args):
        """Show the About dialog box."""
        strabout = "Made by Pushpak Dagade\n(May-June 2011)\n"\
        "http://guanidene.blogspot.com"
        aboutbox = wx.MessageDialog(self, strabout,
          caption='About', style=wx.OK)
        aboutbox.ShowModal()
        aboutbox.Destroy()
