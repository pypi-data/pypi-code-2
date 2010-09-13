# -*- coding:latin-1 -*-
#-----------------------------------------------------------------------------
# Name:        wxFrame1.py
# Purpose:
#
# Author:      <Flavio Codeco Coelho>
#
# Created:     2003/02/04
# RCS-ID:      $Id: wxFrame1.py,v 1.11 2004/01/13 10:51:43 fccoelho Exp $
# Copyright:   (c) 2003 Flavio Codeco Coelho <fccoelho@fiocruz.br>
# Licence:     This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#-----------------------------------------------------------------------------
#Boa:Frame:wxFrame1
from __future__ import division
#import wxversion

import wx
import wx.stc
#from Numeric import *
from threading import *
from scipy import integrate
#from RandomArray import *
from numpy.random import *

import pickle
#from MLab import *
import matplotlib
matplotlib.use('WXAgg')
from pylab import *
from matplotlib.cbook import *
#from wxPython.tools import helpviewer
#from xml.dom import Node

import os,sys
import wxFrame2, about


from odexml import Model
import PlotFigure as PF
#from BIP.Bayes import Melding as meld
from time import *
import icones
import MBicon
import quivVarFrame as QF
from BIP.Bayes import lhs


os.chdir(os.getcwd())

def create(parent):
    return wxFrame1(parent)

[wxID_WXFRAME1, wxID_WXFRAME1CONVCHECKBOX, wxID_WXFRAME1CRITTIMETEXT,
 wxID_WXFRAME1ENDTEXT, wxID_WXFRAME1EQNEDIT, wxID_WXFRAME1EQTEXT,
 wxID_WXFRAME1FIRSTSTEPTEXT, wxID_WXFRAME1FOCHECKBOX, wxID_WXFRAME1GAUGE1,
 wxID_WXFRAME1INITVALINPUT, wxID_WXFRAME1INITVALTEXT,
 wxID_WXFRAME1MAXSTEPTEXT, wxID_WXFRAME1MINSTEPTEXT, wxID_WXFRAME1PANEL1,
 wxID_WXFRAME1PARAMTEXT, wxID_WXFRAME1PAREDIT, wxID_WXFRAME1PROGRESSTEXT,
 wxID_WXFRAME1SEPARALINE, wxID_WXFRAME1STARTTEXT, wxID_WXFRAME1STATUSBAR1,
 wxID_WXFRAME1TEXTCTRL2, wxID_WXFRAME1TEXTCTRL3, wxID_WXFRAME1TEXTCTRL4,
 wxID_WXFRAME1TEXTCTRL5, wxID_WXFRAME1TEXTCTRL6, wxID_WXFRAME1TEXTCTRL7,
 wxID_WXFRAME1TEXTCTRL8, wxID_WXFRAME1TIMESTEPTEXT, wxID_WXFRAME1TOOLBAR1,
] = [wx.NewId() for _init_ctrls in xrange(29)]

[wxID_WXFRAME1MENU1ITEMS0, wxID_WXFRAME1MENU1ITEMS1, wxID_WXFRAME1MENU1ITEMS2,
 wxID_WXFRAME1MENU1ITEMS3, wxID_WXFRAME1MENU1ITEMS4,
] = [wx.NewId() for _init_coll_menu1_Items in xrange(5)]

[wxID_WXFRAME1TOOLBAR1TOOLS0, wxID_WXFRAME1TOOLBAR1TOOLS1,
 wxID_WXFRAME1TOOLBAR1TOOLS2,
] = [wx.NewId() for _init_coll_toolBar1_Tools in xrange(3)]

[wxID_WXFRAME1MENU2ITEMS0, wxID_WXFRAME1MENU2QUIVERPL,
] = [wx.NewId() for _init_coll_menu2_Items in xrange(2)]

[wxID_WXFRAME1MENU3ITEMS0] = [wx.NewId() for _init_coll_menu3_Items in xrange(1)]

[wxID_WXFRAME1TOOLBAR1OPENTOOL, wxID_WXFRAME1TOOLBAR1SAVETOOL,
 wxID_WXFRAME1TOOLBAR1TOOLS0, wxID_WXFRAME1TOOLBAR1TOOLS1,
 wxID_WXFRAME1TOOLBAR1TOOLS2,
] = [wx.NewId() for _init_coll_toolBar1_Tools in range(5)]

[wxID_WXFRAME1, wxID_WXFRAME1CONVCHECKBOX, wxID_WXFRAME1CRITTIMETEXT,
 wxID_WXFRAME1ENDTEXT, wxID_WXFRAME1EQNEDIT, wxID_WXFRAME1EQTEXT,
 wxID_WXFRAME1FIRSTSTEPTEXT, wxID_WXFRAME1FOCHECKBOX, wxID_WXFRAME1GAUGE1,
 wxID_WXFRAME1INITVALINPUT, wxID_WXFRAME1INITVALTEXT,
 wxID_WXFRAME1MAXSTEPTEXT, wxID_WXFRAME1MINSTEPTEXT, wxID_WXFRAME1PANEL1,
 wxID_WXFRAME1PARAMTEXT, wxID_WXFRAME1PAREDIT, wxID_WXFRAME1PROGRESSTEXT,
 wxID_WXFRAME1SEPARALINE, wxID_WXFRAME1STARTTEXT, wxID_WXFRAME1STATUSBAR1,
 wxID_WXFRAME1TEXTCTRL2, wxID_WXFRAME1TEXTCTRL3, wxID_WXFRAME1TEXTCTRL4,
 wxID_WXFRAME1TEXTCTRL5, wxID_WXFRAME1TEXTCTRL6, wxID_WXFRAME1TEXTCTRL7,
 wxID_WXFRAME1TEXTCTRL8, wxID_WXFRAME1TIMESTEPTEXT, wxID_WXFRAME1TOOLBAR1,
] = [wx.NewId() for _init_ctrls in range(29)]

[wxID_WXFRAME1MENU2ITEMS0, wxID_WXFRAME1MENU2QUIVERPL,
] = [wx.NewId() for _init_coll_menu2_Items in range(2)]

[wxID_WXFRAME1MENU1ITEMS0, wxID_WXFRAME1MENU1ITEMS1, wxID_WXFRAME1MENU1ITEMS2,
 wxID_WXFRAME1MENU1ITEMS3, wxID_WXFRAME1MENU1ITEMS4,
] = [wx.NewId() for _init_coll_menu1_Items in range(5)]

[wxID_WXFRAME1MENU3ITEMS0, wxID_WXFRAME1MENU3MBHELP,
] = [wx.NewId() for _init_coll_menu3_Items in range(2)]

class wxFrame1(wx.Frame):

    def _init_coll_boxSizerH_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.gridBagSizer1, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.separaLine, 0, border=0, flag=0)
        parent.AddSizer(self.boxSizerV2, 0, border=0, flag=wx.EXPAND)

    def _init_coll_bsPanel_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panel1, 1, border=0, flag=wx.EXPAND)

    def _init_coll_gridBagSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.eqText, (0, 0), border=0, flag=0, span=(1,3))
        parent.AddWindow(self.eqnEdit, (1, 0), border=0, flag=wx.EXPAND,
              span=(1, 3))
        parent.AddWindow(self.initValText, (2, 0), border=0, flag=0, span=(1,3))
        parent.AddWindow(self.initValInput, (3, 0), border=0, flag=0, span=(1,
              3))
        parent.AddWindow(self.startText, (4, 0), border=0, flag=0, span=(1,1))
        parent.AddWindow(self.endText, (4, 1), border=0, flag=0, span=(1,1))
        parent.AddWindow(self.timeStepText, (4, 2), border=0, flag=0, span=(1,
              1))
        parent.AddWindow(self.textCtrl2, (5, 0), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.textCtrl3, (5, 1), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.textCtrl4, (5, 2), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.critTimeText, (6, 0), border=0, flag=0, span=(1,
              1))
        parent.AddWindow(self.firstStepText, (6, 2), border=0, flag=0, span=(1,
              1))
        parent.AddWindow(self.textCtrl5, (7, 0), border=0, flag=0, span=(1, 2))
        parent.AddWindow(self.textCtrl6, (7, 2), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.minStepText, (8, 0), border=0, flag=0, span=(1,1))
        parent.AddWindow(self.maxStepText, (8, 1), border=0, flag=0, span=(1,1))
        parent.AddWindow(self.progressText, (8, 2), border=0, flag=0, span=(1,
              1))
        parent.AddWindow(self.textCtrl7, (9, 0), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.textCtrl8, (9, 1), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.gauge1, (9, 2), border=0, flag=0, span=(1, 1))

    def _init_coll_boxSizerV2_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.paramText, 1, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.parEdit, 7, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.focheckBox, 1, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.convcheckBox, 1, border=0, flag=wx.EXPAND)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menu1, title='File')
        parent.Append(menu=self.menu2, title='Analysis')
        parent.Append(menu=self.menu3, title='Help')

    def _init_coll_menu3_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Open the main help file',
              id=wxID_WXFRAME1MENU3MBHELP, kind=wx.ITEM_NORMAL,
              text='Model Builder Help')
        parent.AppendSeparator()
        parent.Append(help='General Information about PyMM',
              id=wxID_WXFRAME1MENU3ITEMS0, kind=wx.ITEM_NORMAL, text='About')
        self.Bind(wx.EVT_MENU, self.OnMenu3items0Menu,
              id=wxID_WXFRAME1MENU3ITEMS0)
        self.Bind(wx.EVT_MENU, self.OnMenu3MbhelpMenu,
              id=wxID_WXFRAME1MENU3MBHELP)

    def _init_coll_menu1_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Open a saved model.', id=wxID_WXFRAME1MENU1ITEMS0,
              kind=wx.ITEM_NORMAL, text='Open')
        parent.Append(help='Save your model.', id=wxID_WXFRAME1MENU1ITEMS1,
              kind=wx.ITEM_NORMAL, text='Save')
        parent.Append(help='Save your model on another file.',
              id=wxID_WXFRAME1MENU1ITEMS2, kind=wx.ITEM_NORMAL, text='Save As')
        parent.Append(help='Close your model.', id=wxID_WXFRAME1MENU1ITEMS3,
              kind=wx.ITEM_NORMAL, text='Close')
        parent.Append(help='Exit PyMM.', id=wxID_WXFRAME1MENU1ITEMS4,
              kind=wx.ITEM_NORMAL, text='Exit')
        self.Bind(wx.EVT_MENU, self.OnMenu1items0Menu,
              id=wxID_WXFRAME1MENU1ITEMS0)
        self.Bind(wx.EVT_MENU, self.OnMenu1items1Menu,
              id=wxID_WXFRAME1MENU1ITEMS1)
        self.Bind(wx.EVT_MENU, self.OnMenu1items2Menu,
              id=wxID_WXFRAME1MENU1ITEMS2)
        self.Bind(wx.EVT_MENU, self.OnMenu1items3Menu,
              id=wxID_WXFRAME1MENU1ITEMS3)
        self.Bind(wx.EVT_MENU, self.OnMenu1items4Menu,
              id=wxID_WXFRAME1MENU1ITEMS4)

    def _init_coll_menu2_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Enter uncertainty analysis mode',
              id=wxID_WXFRAME1MENU2ITEMS0, kind=wx.ITEM_CHECK,
              text='Uncertainty analysis')
        parent.Append(help='Generates a State Space quiver plot.',
              id=wxID_WXFRAME1MENU2QUIVERPL, kind=wx.ITEM_NORMAL,
              text='State Diagram...')
        self.Bind(wx.EVT_MENU, self.OnMenu2items0Menu,
              id=wxID_WXFRAME1MENU2ITEMS0)
        self.Bind(wx.EVT_MENU, self.OnMenu2Items1Menu,
              id=wxID_WXFRAME1MENU2QUIVERPL)

    def _init_coll_toolBar1_Tools(self, parent):
        # generated method, don't edit

        parent.DoAddTool(bitmap=icones.getOpenBitmap(),
              bmpDisabled=wx.NullBitmap, id=wxID_WXFRAME1TOOLBAR1OPENTOOL,
              kind=wx.ITEM_NORMAL, label='Open',
              longHelp='Click Here to open a new model.',
              shortHelp='Open Model')
        parent.DoAddTool(bitmap=icones.getSaveBitmap(),
              bmpDisabled=wx.NullBitmap, id=wxID_WXFRAME1TOOLBAR1SAVETOOL,
              kind=wx.ITEM_NORMAL, label='Save', longHelp='Click here to save.',
              shortHelp='Save Model')
        parent.AddSeparator()
        parent.AddTool(bitmap=icones.getrunBitmap(),
              id=wxID_WXFRAME1TOOLBAR1TOOLS0, isToggle=False,
              longHelpString='Start your simulation.',
              pushedBitmap=wx.NullBitmap, shortHelpString='Start')
        parent.AddTool(bitmap=icones.getequationsBitmap(),
              id=wxID_WXFRAME1TOOLBAR1TOOLS1, isToggle=False,
              longHelpString='Show typeset Equations',
              pushedBitmap=wx.NullBitmap, shortHelpString='Show equations')
        parent.AddTool(bitmap=icones.getspreadsheetBitmap(),
              id=wxID_WXFRAME1TOOLBAR1TOOLS2, isToggle=False,
              longHelpString='Show table with results',
              pushedBitmap=wx.NullBitmap, shortHelpString='Results')
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools0Tool,
              id=wxID_WXFRAME1TOOLBAR1TOOLS0)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolbar1tools0ToolRclicked,
              id=wxID_WXFRAME1TOOLBAR1TOOLS0)
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools1Tool,
              id=wxID_WXFRAME1TOOLBAR1TOOLS1)
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools2Tool,
              id=wxID_WXFRAME1TOOLBAR1TOOLS2)
        self.Bind(wx.EVT_TOOL, self.OnToolBar1OpentoolTool,
              id=wxID_WXFRAME1TOOLBAR1OPENTOOL)
        self.Bind(wx.EVT_TOOL, self.OnToolBar1SavetoolTool,
              id=wxID_WXFRAME1TOOLBAR1SAVETOOL)

        parent.Realize()

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='Status')

        parent.SetStatusWidths([-1])

    def _init_sizers(self):
        # generated method, don't edit
        self.gridBagSizer1 = wx.GridBagSizer(hgap=3, vgap=2)
        self.gridBagSizer1.SetCols(2)
        self.gridBagSizer1.SetRows(10)
        self.gridBagSizer1.SetFlexibleDirection(12)
        self.gridBagSizer1.SetNonFlexibleGrowMode(1)

        self.bsPanel = wx.BoxSizer(orient=wx.VERTICAL)

        self.boxSizerH = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.boxSizerV2 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_gridBagSizer1_Items(self.gridBagSizer1)
        self._init_coll_bsPanel_Items(self.bsPanel)
        self._init_coll_boxSizerH_Items(self.boxSizerH)
        self._init_coll_boxSizerV2_Items(self.boxSizerV2)

        self.SetSizer(self.bsPanel)

    def _init_utils(self):
        # generated method, don't edit
        self.menu1 = wx.Menu(title='File')

        self.menu3 = wx.Menu(title='Help')

        self.menuBar1 = wx.MenuBar()

        self.menu2 = wx.Menu(title='Analysis')

        self._init_coll_menu1_Items(self.menu1)
        self._init_coll_menu3_Items(self.menu3)
        self._init_coll_menuBar1_Menus(self.menuBar1)
        self._init_coll_menu2_Items(self.menu2)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_WXFRAME1, name='', parent=prnt,
              pos=wx.Point(362, 472), size=wx.Size(730, 480),
              style=wx.DEFAULT_FRAME_STYLE, title='Model Builder - ODE')
        self._init_utils()
        self.SetClientSize(wx.Size(730, 480))
        self.SetMenuBar(self.menuBar1)
        self.SetToolTipString('Model Builder')
        self.SetAutoLayout(True)
        self.SetInitialSize(wx.Size(730, 480))
        self.SetMaxSize(wx.Size(730, 480))
        self.SetIcon(MBicon.MB.GetIcon())#wx.Icon(MBicon.MB.GetIcon(),wx.BITMAP_TYPE_ICO))
        self.Bind(wx.EVT_CLOSE, self.OnWxFrame1Close)

        self.statusBar1 = wx.StatusBar(id=wxID_WXFRAME1STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self.statusBar1.SetSize(wx.Size(80, 19))
        self.statusBar1.SetPosition(wx.Point(-1, -1))
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.toolBar1 = wx.ToolBar(id=wxID_WXFRAME1TOOLBAR1, name='toolBar1',
              parent=self, pos=wx.Point(0, 31), size=wx.Size(248, 50),
              style=wx.TRANSPARENT_WINDOW | wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.toolBar1.SetToolTipString('')
        self.toolBar1.SetThemeEnabled(True)
        self.SetToolBar(self.toolBar1)

        self.panel1 = wx.Panel(id=wxID_WXFRAME1PANEL1, name='panel1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(730, 449),
              style=wx.TAB_TRAVERSAL)

        self.initValInput = wx.TextCtrl(id=wxID_WXFRAME1INITVALINPUT,
              name='initValInput', parent=self.panel1, pos=wx.Point(0, 208),
              size=wx.Size(465, 22), style=0, value='')
        self.initValInput.SetToolTipString('Initial conditions: values separated by spaces.')
        self.initValInput.SetInitialSize(wx.Size(465, 22))

        self.startText = wx.StaticText(id=wxID_WXFRAME1STARTTEXT,
              label='Start time:', name='startText', parent=self.panel1,
              pos=wx.Point(0, 232), size=wx.Size(153, 20), style=0)

        self.textCtrl2 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL2,
              name='textCtrl2', parent=self.panel1, pos=wx.Point(0, 254),
              size=wx.Size(153, 22), style=0, value='0')
        self.textCtrl2.SetToolTipString('Time value at the start of simulation')

        self.endText = wx.StaticText(id=wxID_WXFRAME1ENDTEXT, label='End Time:',
              name='endText', parent=self.panel1, pos=wx.Point(160, 232),
              size=wx.Size(153, 20), style=0)
        self.endText.SetToolTipString('Time value to end simulation')

        self.textCtrl3 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL3,
              name='textCtrl3', parent=self.panel1, pos=wx.Point(160, 254),
              size=wx.Size(153, 22), style=0, value='10')
        self.textCtrl3.SetToolTipString('Time value to end simulation')

        self.timeStepText = wx.StaticText(id=wxID_WXFRAME1TIMESTEPTEXT,
              label='Time Step:', name='timeStepText', parent=self.panel1,
              pos=wx.Point(320, 232), size=wx.Size(153, 20), style=0)

        self.textCtrl4 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL4,
              name='textCtrl4', parent=self.panel1, pos=wx.Point(320, 254),
              size=wx.Size(153, 22), style=0, value='0.1')
        self.textCtrl4.SetToolTipString('Time step for the output')

        self.critTimeText = wx.StaticText(id=wxID_WXFRAME1CRITTIMETEXT,
              label='Critical Time Steps:', name='critTimeText',
              parent=self.panel1, pos=wx.Point(0, 278), size=wx.Size(153, 20),
              style=0)

        self.textCtrl5 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL5,
              name='textCtrl5', parent=self.panel1, pos=wx.Point(0, 300),
              size=wx.Size(309, 22), style=0, value='')
        self.textCtrl5.SetToolTipString('Time points where integration care should be taken.')

        self.firstStepText = wx.StaticText(id=wxID_WXFRAME1FIRSTSTEPTEXT,
              label='First Step:', name='firstStepText', parent=self.panel1,
              pos=wx.Point(320, 278), size=wx.Size(153, 20), style=0)

        self.textCtrl6 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL6,
              name='textCtrl6', parent=self.panel1, pos=wx.Point(320, 300),
              size=wx.Size(153, 22), style=0, value='0')
        self.textCtrl6.SetToolTipString('Size of the first step (0=auto)')

        self.textCtrl7 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL7,
              name='textCtrl7', parent=self.panel1, pos=wx.Point(0, 348),
              size=wx.Size(153, 22), style=0, value='0')
        self.textCtrl7.SetToolTipString('Minimum absolute step size allowed (0=auto).')

        self.maxStepText = wx.StaticText(id=wxID_WXFRAME1MAXSTEPTEXT,
              label='Max Step Size:', name='maxStepText', parent=self.panel1,
              pos=wx.Point(160, 324), size=wx.Size(153, 22), style=0)

        self.textCtrl8 = wx.TextCtrl(id=wxID_WXFRAME1TEXTCTRL8,
              name='textCtrl8', parent=self.panel1, pos=wx.Point(160, 348),
              size=wx.Size(153, 22), style=0, value='0')
        self.textCtrl8.SetToolTipString('Maximum absolute step size allowed (0=auto)')

        self.separaLine = wx.StaticLine(id=wxID_WXFRAME1SEPARALINE,
              name='separaLine', parent=self.panel1, pos=wx.Point(477, 0),
              size=wx.Size(30, 780),
              style=wx.MAXIMIZE_BOX | wx.LI_VERTICAL | wx.THICK_FRAME | wx.LI_VERTICAL| 1)
        self.separaLine.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.separaLine.SetToolTipString('')
        self.separaLine.SetThemeEnabled(True)
        self.separaLine.SetAutoLayout(True)
        self.separaLine.SetExtraStyle(0)

        self.focheckBox = wx.CheckBox(id=wxID_WXFRAME1FOCHECKBOX,
              label='Full Output', name='focheckBox', parent=self.panel1,
              pos=wx.Point(507, 174), size=wx.Size(208, 22), style=0)
        self.focheckBox.SetValue(True)
        self.focheckBox.SetToolTipString('Check if you want the full output.')

        self.paramText = wx.StaticText(id=wxID_WXFRAME1PARAMTEXT,
              label='Parameters:', name='paramText', parent=self.panel1,
              pos=wx.Point(507, 0), size=wx.Size(88, 16), style=0)

        self.parEdit = wx.TextCtrl(id=wxID_WXFRAME1PAREDIT, name='parEdit',
              parent=self.panel1, pos=wx.Point(507, 16), size=wx.Size(208, 158),
              style=wx.HSCROLL | wx.TE_PROCESS_TAB | wx.VSCROLL | wx.TE_MULTILINE,
              value='')
        self.parEdit.SetToolTipString('Enter parameter values or expressions, one per line. Parameter should be refered to as p[0], p[1],... in the DEs.')
        self.parEdit.SetHelpText('Each line corresponds to one Parameter (p[0], p[1], ...)')

        self.gauge1 = wx.Gauge(id=wxID_WXFRAME1GAUGE1, name='gauge1',
              parent=self.panel1, pos=wx.Point(320, 348), range=100,
              size=wx.Size(153, 22), style=wx.GA_HORIZONTAL,
              validator=wx.DefaultValidator)
        self.gauge1.SetLabel('Percent Done')
        self.gauge1.SetValue(0)
        self.gauge1.SetToolTipString('Percent Done')
        self.gauge1.SetHelpText('Show the percentage of the simulation done.')
        self.gauge1.SetShadowWidth(10)
        self.gauge1.SetBezelFace(1)

        self.eqnEdit = wx.TextCtrl(id=wxID_WXFRAME1EQNEDIT, name='eqnEdit',
              parent=self.panel1, pos=wx.Point(0, 24), size=wx.Size(477, 158),
              style=wx.HSCROLL | wx.TE_PROCESS_TAB | wx.TE_MULTILINE, value='')
        self.eqnEdit.SetToolTipString('ODE box. Enter one equation per line. Right hand side only.')

        self.eqText = wx.StaticText(id=wxID_WXFRAME1EQTEXT,
              label='Differential Equations:', name='eqText',
              parent=self.panel1, pos=wx.Point(0, 0), size=wx.Size(465, 22),
              style=0)
        self.eqText.SetThemeEnabled(True)
        self.eqText.SetInitialSize(wx.Size(465, 22))

        self.initValText = wx.StaticText(id=wxID_WXFRAME1INITVALTEXT,
              label='Initial values:', name='initValText', parent=self.panel1,
              pos=wx.Point(0, 184), size=wx.Size(465, 22), style=0)
        self.initValText.SetInitialSize(wx.Size(465, 22))

        self.minStepText = wx.StaticText(id=wxID_WXFRAME1MINSTEPTEXT,
              label='Min. Step Size:', name='minStepText', parent=self.panel1,
              pos=wx.Point(0, 324), size=wx.Size(153, 22), style=0)

        self.progressText = wx.StaticText(id=wxID_WXFRAME1PROGRESSTEXT,
              label='Progress:', name='progressText', parent=self.panel1,
              pos=wx.Point(320, 324), size=wx.Size(153, 22), style=0)

        self.convcheckBox = wx.CheckBox(id=wxID_WXFRAME1CONVCHECKBOX,
              label='Show Convergence Message', name='convcheckBox',
              parent=self.panel1, pos=wx.Point(507, 323), size=wx.Size(208, 22),
              style=0)
        self.convcheckBox.SetValue(False)
        self.convcheckBox.SetToolTipString('Check if you want the convergence message to be displayed.')
        self.convcheckBox.Enable(True)
        self.convcheckBox.SetThemeEnabled(True)

        self._init_coll_toolBar1_Tools(self.toolBar1)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.FileName = None
        self.ModLoaded = None #no model has been loaded
        self.Neq = None
        self.modict = {'modelname':''}
        self.modtree = Model() #Object containing dom tree with model specification
        self.modbuilt = 0 #model has never been built
        self.modRan = 0 #model has never been ran
        self.plot = 0 #no plot has ever been generated
        self.gauge1.SetRange(100)
        self.uncertainty = 0 # uncertainty analysis is off
        self.ceqs = [] #compiled equations
        self.cpars = [] #compiled parameters
        self.curdir = ''


    def OnMenu1items0Menu(self, event):
        """
        Load a model file.
        """
        self.modtree = Model() #reset the modtree object upon the opening of a new model
        if self.curdir:
            os.chdir(self.curdir)
        dlg = wx.FileDialog(self, "Choose a file", self.curdir, "", "*.ode", wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                a = self.modtree.readFile(filename)
                if a==1: #model is not a xml file
                    f = open(filename)
                    self.modict = pickle.load(f)
                    self.fillGui()
                    self.FileName = filename
                    self.SetTitle('Model Builder - '+filename)
                    f.close()
                elif a == 2:
                    return
                else:
                    self.modict.update(self.modtree.modict)
                    self.fillGui()
                    self.FileName = filename
                    self.SetTitle('Model Builder - '+os.path.split(filename)[1])
                    #load data
                    try:
                        d = pickle.load(self.checkExt(filename,'.dat'))
                        self.modict['results']=d[0]
                        self.modict['trange']=d[1]
                    except: pass
                self.ModLoaded = 1
                self.curdir = os.path.split(filename)[0]
        finally:
            self.statusBar1.SetStatusText('Model loaded.')
            #print self.modict.keys()
            dlg.Destroy()

    def fillGui(self):
        """
        fill GUI from model dictionary
        """
        self.eqnEdit.SetValue(self.modict['equations'])
        self.textCtrl2.SetValue(str(self.modict['start']))
        self.textCtrl3.SetValue(str(self.modict['end']))
        self.textCtrl4.SetValue(str(self.modict['step']))
        self.initValInput.SetValue(str(self.modict['init']))
        self.parEdit.SetValue(self.modict['parameters'])
        self.BuildModel(r=0) # call BuildModel without running the model

    def checkExt(self,fn,ext):
        """
        Add a filename extension to the filename or replace
        original extension.
        fn: file name
        ext: desired extension
        """
        head,tail = os.path.split(fn)
        orext = '.'+tail.split('.')[-1]
        if not orext:
            tail += ext
        if orext and (ext != orext):
            tail = tail.replace(orext,ext)
        return head+tail


    def OnMenu1items1Menu(self, event):
        """
        Save model.
        """
        self.modtree = Model()
        if not self.FileName:
            return self.OnMenu1items2Menu(event)
        else:
            #print self.modict.keys()
            filename = os.path.split(self.FileName)[1]
            self.modict['modelname'] = filename
            self.modtree.path = self.curdir
            self.BuildModel(r=0) # call BuildModel without running the model
            #save data
            if self.modict.has_key('results')and self.modict.has_key('trange'):
                fna = open(self.checkExt(filename,'.dat'),'w')
                pickle.dump((self.modict['results'], self.modict['trange']),fna)
                fna.close()
            # Saving in xml format
            try:
                self.modict.pop('results')
                self.modict.pop('trange')
            except: pass
            self.modtree.Create(**self.modict)
            self.modtree.saveFile(self.checkExt(filename,'.ode'))
            self.ModLoaded = 1
            self.statusBar1.SetStatusText('Model saved.')
            #print self.modict.keys()


    def OnMenu1items2Menu(self, event):
        """
        Save as menu entry
        """
        self.modtree = Model()
        dlg = wx.FileDialog(self, "Save File As", self.curdir, "", "*.ode", wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.FileName = dlg.GetPath()
                filename = os.path.split(self.FileName)[-1]
                self.modtree.path = self.curdir = os.path.split(self.FileName)[0]
                if not filename.endswith('.ode'):
                    filename += '.ode'
                if not self.modbuilt: #check to see if model's dictionary has been built
                    self.BuildModel(r=0) # call BuildModel without running the model
                    self.modict['modelname'] = filename
                self.SetTitle('Model Builder - '+filename)
                #save data
                if self.modict.has_key('results'):
                    os.chdir(self.curdir)
                    fna = open(self.checkExt(filename,'.dat'),'w')
                    pickle.dump((self.modict['results'], self.modict['trange']),fna)
                    fna.close()
                # Saving in xml format
                #print self.modict.keys()
                try:
                    self.modict.pop('results')
                    self.modict.pop('trange')
                except:
                    pass
                self.modtree.Create(**self.modict)
                self.modtree.saveFile(self.checkExt(filename,'.ode'))
                self.ModLoaded = 1
                self.statusBar1.SetStatusText('Model saved.')

        finally:
            dlg.Destroy()


    def OnMenu1items3Menu(self, event):
        """
        Close model menu entry.
        """
        self.modtree = Model()
        self.FileName = None
        self.ModLoaded = None
        self.modict = {}
        self.eqnEdit.SetValue('')
        self.textCtrl2.SetValue('')
        self.textCtrl3.SetValue('')
        self.textCtrl4.SetValue('')
        self.initValInput.SetValue('')
        self.parEdit.SetValue('')
        self.SetTitle('Model Builder - ODE')


    def OnMenu1items4Menu(self, event):
        """
        Exit the program
        """

        self.Close()
        self.Destroy()


    def OnMenu2items0Menu(self, event):
        """
        If Uncertainty Analysis has been selected, it will Open the uncertainty panel to set
        the parameters for the analysis.
        """
        if not self.ModLoaded:
            self.OnMenu1items0Menu(event)
            return
        #--Checks if the Uncertainty item in the analysis menu (2) has been checked------

        if self.menu2.IsChecked(wxID_WXFRAME1MENU2ITEMS0):
            self.uncertaintyPanel = LHS(None)
            #self.uncertaintyPanel=uncertaintyMiniFrame.create(None)
            self.initUncertainty()
            self.uncertaintyPanel.Show()
            self.uncertainty = 1 #raises uncertainty flag
        else:
            self.uncertainty = 0 #Uncertainty mode off
            try:
                self.uncertaintyPanel.Close()
            except:
                pass


    def checkErrors(self):
        """
        Check for normal editing errors in model definition
        """
        while not self.eqnEdit.GetValue()=='':
            val = self.eqnEdit.GetValue().strip().splitlines()
            Neq = len(val)
            break
##~         Neq = int(self.eqnEdit.GetNumberOfLines()) #get number of ODEs
##~         while strip(self.eqnEdit.GetLineText(Neq-1)) == '': # avoid getting empty lines at the end of the eq. box
##~             Neq = Neq-1
##~             if Neq == 1:nty
##~                 break

        if not self.parEdit.GetValue() == '':
            valp = self.parEdit.GetValue().strip().splitlines()
            Npar = len(valp)
        else:
            Npar = 0

##~         Npar = int(self.parEdit.GetNumberOfLines()) #get Number of  Parameters
##~         while strip(self.parEdit.GetLineText(Npar-1)) == '':# avoid getting empty lines at the end of the eq. box
##~             Npar=Npar-1
##~             if Npar == 1:
##~                 break
##~             if Npar == 0:
##~                 Npar = 1
##~                 break

#---Check number of initial conditions----------------------------------------------------------------------------
        if self.initValInput.GetValue().strip() == '':
            ni = 0
        else:
            ni = len(self.initValInput.GetValue().strip().split(' '))
        if not ni == Neq:
            return 1

#---Check that all initial conditions are numbers----------------------------------------------------------------------------
        for i in xrange(ni):
            try:
                float(self.initValInput.GetValue().strip().split(' ')[i])
            except ValueError:
                e = 2
                return 2
#---Check syntax of equations----------------------------------------------------------------------------
        y=zeros(Neq)#fake equation array
        p=zeros(Npar)#fake parameter array
        t=0
        eqs = self.eqnEdit.GetValue().strip().split('\n')
        eql = [i.split('=')[-1] for i in self.eqnEdit.GetValue().strip().split('\n')]
        vnames = [i.split('=')[0] for i in self.eqnEdit.GetValue().strip().split('\n') if '=' in i]
        pnames = [i.split('=')[0] for i in self.parEdit.GetValue().strip().splitlines() if '=' in i]
        #replace ocurrences of variable names in equations.
        if vnames:
            #create fake variables
            for v in vnames:
                exec('%s = 0'%v)
        #replace occurrences of parameter names in equations by p[i]
        if pnames:
            for p in pnames:
                exec('%s = 0'%p)
        for k in eql:
            try:
                eval(k) #dy(k)/dt
            except (SyntaxError, NameError), details:
                print details
                return 3

        return 0


    def OnToolbar1tools0Tool(self, event):
        """
        Run button event.
        Call BuildModel with r=1, and times how long the model takes to run.
        The time elapsed is shown in a message dialog.
        """
        if not self.ModLoaded:
            if self.eqnEdit.GetValue().strip() == '':
                return self.OnMenu1items0Menu(event)
#----compile equations and store for later use
        eql = [i.split('=')[-1].strip() for i in self.eqnEdit.GetValue().strip().split('\n')]
        print "eql:%s"%eql
        self.vnames = [v.split('=')[0].strip() for v in self.eqnEdit.GetValue().strip().split('\n') if '=' in v]
        print self.vnames

        try:
            self.ceqs = [compile(i,'<string>','eval') for i in eql]
        except SyntaxError:
            dlg = wx.MessageDialog(self, 'There is a syntax error in the Equation Box.\nPlease fix it and try again.',
              'Syntax Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        self.compilePars()
#---checking for errors----------------------------------------------------------------------------
        e = self.checkErrors()
        if e == 1:
            dlg = wx.MessageDialog(self, 'Wrong number of initial condition values.',
              'Initial Condition Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        elif e == 2:
            dlg = wx.MessageDialog(self, 'There is a syntax error on the initial conditions box.',
              'Syntax Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        elif e==3:
            dlg = wx.MessageDialog(self, 'There is a syntax error in the Equation Box.\nPlease fix it and try again.',
              'Syntax Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        else:
            pass
        self.modbuilt = 0
        self.updateGauge(0)
        if self.uncertainty == 0:
            self.BuildModel(r=1) #regular run
            self.modRan = 1 #set the flag indicating model has been run
        else:
            if self.uncertaintyPanel.Done:
                self.statusBar1.SetStatusText('Simulation Started!\n')
                self.BuildModel(r=1) # Melding setup
                self.modRan = 1 #set the flag indicating model has been run
            else:
                dlg = wx.MessageDialog(self, 'Set the parameters for the Uncertainty Analysis\nin its panel and press the "OK" button',
                  'Uncertain Parameters', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()



    def OnToolbar1tools0ToolRclicked(self, event):
        event.Skip()

    def updateGauge(self,t):
        """
        This function simply updates the progress gauge
        """
        pd = (100*t)/(float(str(self.textCtrl3.GetValue()).strip())-float(str(self.textCtrl2.GetValue()).strip())) #calcutates percentage done
        self.gauge1.SetValue(int(pd))
        #self.gauge1.SetToolTipString(str(pd)+'%')
        self.gauge1.Refresh() #update the gauge

    def Equations(self, y, t):
        """
        This function defines the system of differential equations, evaluating
        each line of the equation text box as ydot[i]

        returns ydot
        """
        self.updateGauge(t)

        Neq=self.Neq
        Npar = self.Npar
        par = self.par
        #print "vnames:", self.vnames, self.pnames
        if self.vnames:
            #print y,type(y)
            if Neq ==1:
                exec('%s=%s'%(','.join(self.vnames), y[0]))
            else:
                exec('%s=%s'%(','.join(self.vnames),list(y)))

        ydot = zeros((Neq),'d') #initialize ydot
        p = zeros((Npar),'d') #initialize p
    #---Create Parameter Array----------------------------------------------------------------------------

        if self.uncertainty == 0:
            pars = self.cpars
            #par.GetValue().strip().split('\n')
            if pars: #only if there is at least one parameter
                for j in xrange(len(pars)):
                    if self.pnames:
                        exec(pars[j])
                    else:
                        p[j] = eval(pars[j]) #initialize parameter values

        else:
            if Npar:
                for i in xrange(Npar):
                    if self.pnames:
                        print pnames, par
                        sys.exit()
                        exec("%s=%s"%(self.pnames[i],par[i][self.run]))
                    else:
                        p[i] = par[i][self.run] # Get a new set of parameters for each repeated run
    #---Create equation array----------------------------------------------------------------------------
        eqs = self.ceqs
        #print par[0][0].shape,type(par[0][0]),par[0].shape,type(par[0]),type(par[0])
        for k in xrange(Neq):
            ydot[k] = eval(eqs[k]) #dy(k)/dt

        return ydot

    def compilePars(self):
        """
        compile parameter expressions
        """
        if self.parEdit.GetValue().strip() =="":
            self.cpars = []
            return
        pars = self.parEdit.GetValue().strip().splitlines()
        self.pnames = [p.split('=')[0] for p in pars if '=' in p]
        print self.pnames,  pars
        if self.pnames:
            #in this case returns the compete expression, including the '='
            #print pars
            try:
                self.cpars = [compile(i,'<parameter>','exec') for i in pars]
            except (SyntaxError),details:
                self.cpars =pars
                dlg = wx.MessageDialog(self, 'There is a syntax error in the parameter Box:\n%s\nPlease fix it and try again.'%details,
                  'Syntax Error', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
        else:
            try:
                self.cpars = [compile(i,'<parameter>','eval') for i in pars]
            except SyntaxError:
                dlg = wx.MessageDialog(self, 'There is a syntax error in the parameter Box.\nPlease fix it and try again.',
                  'Syntax Error', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()


    def OnToolbar1tools1Tool(self, event):
        """
        Show a figure with the equations typeset
        """
#---translate equations to pseudo-TeX notation----------------------------------------------------------------------------
        texdict = {
        '**':r'^','sqrt':r'\sqrt','[':r'_{',']':r'}',
        'sin':r'\rm{sin}','cos':r'\rm{cos}',
        'alpha':r'\alpha ','beta ':r'\beta ','gamma':r'\gamma '
        } #Can be extended to acomodate new strings
        texdict2 = {'*':r'\times '}# to take care of the multiplication sign *
        xlat = Xlator(texdict)
        xlat2 = Xlator(texdict2)
        if not self.modbuilt:
            self.BuildModel(r=0)
        eq = range(self.Neq) #initialize
        eqs = self.eqnEdit.GetValue().strip().split('\n')
        for i in xrange(self.Neq):
            e = eqs[i].split('=')[-1]
            eq[i] = xlat2.xlat(xlat.xlat(e))
#-------------------------------------------------------------------------------
        #getting variable names
        vnames = [n.split('=')[0].strip() for n in eqs if '=' in n]
        eqlist=[]
        for i in xrange(self.Neq):
            if len(vnames)==self.Neq:
                eq[i] = r'$d%s/dt = '%vnames[i] + eq[i] + r'$'
            else:
                eq[i] = r'$dY_%s/dt = '%i + eq[i] +r'$'
            eqlist.append(eq[i])
#---plot equations----------------------------------------------------------------------------
        DP = PF.create(None)
        DP.SetTitle('Model '+str(self.FileName)[:-4]+': Equations')
        DP.plotEquation(eqlist)
        DP.Show()


    def plotOutput(self, x, y):
        """
        Plots the results of a single run.
        Raises the flag that the plot has been created
        """
        self.PF = PF.create(None)
        self.PF.plot_data(x,y,self.vnames)
        self.PF.Show()


        self.plot = 1

    def plotMelding(self,x,y,tit='Results'):
        """
        This function preprocesses the output of the repeated Runs, calls Bayesian Melding run and sends the data to
        PlotFigure.plotStats to be plotted.
        x contains the time values and y is a list of outputs from odeint, one from each run.
        """
        self.statusBar1.SetStatusText('Preparing data for plotting...\n')
        yt = [] # initializes list of transposed runs
        nvar = min(y[0].shape) # Number of Variables
        runlen = max(y[0].shape) #Lenght of runs

        nruns = len(y) # Number of runs

##        SPF = PF.create(None)
##        SPF.plot_data(x,y)
##        SPF.Show()

        self.nruns = nruns
        runs_byvar = [] #List of arrays that will contain all runs for each given variable

        for i in y:
            yt.append(transpose(i)) #Extracts the time series arrays and transpose them (the median function needs to have the series in rows, not in columns).

        for v in xrange(nvar):
            runs_byvar.append(array([yt[i][v] for i in xrange(nruns)]))



        # TODO: Turn medianruns into a function
        medianRuns = [median(i) for i in runs_byvar]
        self.statusBar1.SetStatusText('Done!\n\n')



        #---95% Limits----------------------------------------------------------
        # TODO: Turn calculation of limits into a function
        self.statusBar1.SetStatusText('Calculating credibility intervals...\n')
        sorted=[]
        ll = []
        ul = []
        lc = int(runs_byvar[0].shape[0]*0.025) #column containing the lower boundary for the 95% interval
        hc = int(runs_byvar[0].shape[0]*0.975) #column containing the upper boundary for the 95% interval
        for l in xrange(nvar):
            sorted.append(msort(runs_byvar[l]))
            ll.append(sorted[l][lc])
            ul.append(sorted[l][hc])

        ts = (medianRuns,ll,ul)
        self.statusBar1.SetStatusText('Done!\n\n')

#---testing---------------------------------------------------------------------
##        med = medianRuns[0]-medianRuns[1]
##        SPF = PF.create(None)
##        SPF.plot(x,med)
##        SPF.Show()
#-------------------------------------------------------------------------------


        TP = PF.create(None)
        TP.SetTitle(tit)
        TP.plotStats(x,ts,self.vnames)
        TP.Show()


        self.plot = 1
        return (x,runs_byvar)


    def OnToolbar1tools2Tool(self, event):
        """
        Show Output Table
        """
        if self.modRan:
            self.TableOut = wxFrame2.create(None)
            output = self.modict['results'] # get output from model's dictionary
            x = self.modict['trange']
            y = output[0]
            info = output[1] #extra information dictionary
            infoarray = array([info['hu'],info['tcur'],info['tsw'],info['nqu'],info['mused']]).transpose()
            infoarray = concatenate((zeros((1,5)),infoarray),axis=0)
            #print infoarray.shape, y.shape
            r,c = y.shape # get size of t_course array
            self.TableOut.grid1.CreateGrid(r+1,c+6)

            # Filling the grid
            x.shape = (len(x),1)
            data = concatenate((x,y,infoarray),axis=1)
            self.TableOut.Show()
            self.TableOut.fillGrid(data)
            self.TableOut.table.SetColLabelValue(0,'Time')
            for j in xrange(1,c+1): #fill column labels
                if self.vnames:
                    self.TableOut.table.SetColLabelValue(j,self.vnames[j-1])
                else:
                    self.TableOut.table.SetColLabelValue(j,'y[%s]'%(j-1))
            #Adding info column labels
            clabels = ['Step sizes','Time reached','Last method switch','Method order','Method nused']
            for z in xrange(1,6):
                self.TableOut.table.SetColLabelValue(c+z,clabels[z-1])




    def BuildModel(self, r=0):
        """
        Constructs the model from the input fields and runs it if r==1
        """
        try:
            if self.modict:pass
        except:
            self.modict = {}
        try:
            self.modict['modelname'] = os.path.split(self.FileName)[-1]
        except AttributeError:
            self.modict['modelname'] = ''
        self.modict['equations'] = str(self.eqnEdit.GetValue()) #put equations into model's dictionary
        self.modict['parameters'] = str(self.parEdit.GetValue()) # put parameters into model's dictionary
        t_start = float(str(self.textCtrl2.GetValue()).strip())
        self.modict['start'] = str(self.textCtrl2.GetValue()).strip() #store start time
        t_end = float(str(self.textCtrl3.GetValue()).strip())
        self.modict['end'] = str(self.textCtrl3.GetValue()).strip() #store end time
        t_step = float(str(self.textCtrl4.GetValue()).strip())
        self.modict['step'] = str(self.textCtrl4.GetValue()).strip() # Store step size
        init_conds = array([float(i) for i in self.initValInput.GetValue().strip().split(' ') if i != ''])
        self.modict['init'] = str(self.initValInput.GetValue()).strip() # Store initial conditions
        t_range = arange(t_start, t_end+t_step, t_step)
        self.modict['trange'] = t_range
        if self.focheckBox.GetValue():
            fo = 1
        else:
            fo = 0
        if self.convcheckBox.GetValue():
            cm = 1
        else:
            cm = 0
        eqs = self.eqnEdit.GetValue().strip().splitlines()
        self.vnames = [n.split('=')[0].strip() for n in eqs if '=' in n]
        self.pnames = [n.split('=')[0].strip() for n in self.parEdit.GetValue().strip().splitlines() if '=' in n]


        while not self.eqnEdit.GetValue()=='':#get number of ODEs
            val = self.eqnEdit.GetValue().strip().split('\n')
            Neq = len(val)
            break


        self.Neq = Neq#to be used by Equations
        if r==1:
            self.sw = wx.StopWatch()
            self.gauge1.SetValue(0)
            self.sw.Start()
            #-----------------------------------------------------
            if self.uncertainty == 0:#regular (single) run
                if not self.parEdit.GetValue() == '':#get Number of  Parameters
                    valp = self.parEdit.GetValue().strip().split('\n')
                    Npar = len(valp)
                else:
                    Npar = 0

                self.Npar = Npar#to be used by Equations
                self.par = self.parEdit #to be used by Equations
                t_course = integrate.odeint(self.Equations,init_conds,t_range, full_output=fo, printmessg=cm)
                self.plotOutput(t_range,t_course)
                self.modict['results'] = t_course
                self.modRan = 1
            else:
#-------------Multiple runs (uncertainty analysis)------------------------------------
                self.uncRun(init_conds,t_range,cm)


            t = gmtime(self.sw.Time()/1000)

            dlg = wx.MessageDialog(self, 'The simulation was completed in '+str(t[3])+' hours, '+str(t[4])+' minutes and '+str(t[5])+' seconds.',
          'Time Elapsed', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            if self.uncertainty == 1:
                self.statusBar1.SetStatusText('The simulation was completed in: '+str(t[3])+' hours, '+str(t[4])+' minutes and '+str(t[5])+' seconds.')
#-------------------------------------------------------------------------------

        self.modbuilt = 1

    def uncRun(self, init_conds,t_range,cm):
        """
        Runs the model in uncertainty mode
        """
        Npar  = len(self.uncertaintyPanel.theta)
        nr= int(self.uncertaintyPanel.specs['samples']) # Get K from uncertaity panel
        t_courseList = []

        if self.uncertaintyPanel.anaChoice.GetStringSelection() == 'Uncertainty':
            self.parMeld = self.uncertaintyPanel.priords#[:Npar]
        else: #Sensitivity analysis
            self.parMeld = self.uncertaintyPanel.priords
        self.par = self.parMeld #to be used by Equations
        self.Npar = len(self.par)
        #print 'runs:%s'%nr
        for i in xrange(nr):
            self.run = i
#---tcourselist for multiple runs does not contain the full output of odeint, just the time series--------------
            t_courseList.append(integrate.odeint(self.Equations,init_conds,t_range, full_output=0, printmessg=cm))
            #if self.run%20 == 0:
             #   self.statusBar1.SetStatusText(str(self.run)+'\n')
            init_conds = array([float(i) for i in self.initValInput.GetValue().strip().split(' ') if i != '']) #reset initial conditions between runs

        self.modRan = 1
        te = gmtime(self.sw.Time()/1000)#time elapsed so far (first stage of melding)
        if self.uncertaintyPanel.anaChoice.GetStringSelection() == 'Uncertainty':
            self.statusBar1.SetStatusText('First stage of simulation completed in:'+str(te[3])+' hours, '+str(te[4])+' minutes and '+str(te[5])+' seconds.'+'\n')
            (x,runs_byvar) = self.plotMelding(t_range,t_courseList,tit='Median Runs and 95 percent intervals. n=%s'%nr)
            self.Bmeld(x,runs_byvar) # Perform the rest of the melding calculations
            self.modict['meldruns'] = t_courseList
        else: #Sensitivity Analysis
            self.statusBar1.SetStatusText('Simulations completed in:'+str(te[3])+' hours, '+str(te[4])+' minutes and '+str(te[5])+' seconds.'+'\n')
            (x,runs_byvar) = self.plotMelding(t_range,t_courseList,tit='Median Runs and 95 percent intervals. n=%s'%nr)


    def Bmeld(self,t,ModOut):
        """
        Performs the Melding.
        t is an array of time values.
        Modout is a list of n arrays of time courses where n is the number of variables.
        """
        nvar = len(ModOut)
        dlg = wx.TextEntryDialog(self, 'for which time do you want to run the Melding', 'Choose Time', str(t[-1]))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                if answer == '':
                    time = t[-1]
                else:
                    time  = eval(answer)
        finally:
            dlg.Destroy()


        Phis = [ModOut[i][:,int(time)] for i in xrange(nvar)] # list with all the specified values for each variable
        q2phis = self.uncertaintyPanel.priords[-nvar:] # priors (pre-model) for the phis
        q1thetas = tuple(self.uncertaintyPanel.priords[:-nvar]) # priors for the thetas (parameters)
        plimits = self.uncertaintyPanel.priors[1][-nvar:] #limits of the prior distributions of the phis
        ptype = self.uncertaintyPanel.priors[0][:-nvar] #types of the prior distributions
        lik = self.uncertaintyPanel.lhoods
        alpha = self.uncertaintyPanel.alpha
        L = int(self.nruns*0.1)
#---Run SIR----------------------------------------------------------------------------
#---meldout=(w, post_theta, qtilphi, q1est)----------------------------------------------------------------------------
        meldout = meld.SIR(alpha,q2phis,plimits,ptype, q1thetas,Phis,L,lik) # output of meld.SIR: (w,qtiltheta,qtilphi,q1est)
#---If SIR fails, don't proceed----------------------------------------------------------------------------
        if meldout == None:
            return


#---Calculate posterior of phis-----------------------------------------------------
        (x,post_phi) = self.postPHI(meldout, L)
#---Plotting results---------------------------------------------------------------------------
        nplots = len(self.uncertaintyPanel.priords)
        allpriors = self.uncertaintyPanel.priords
        nvp = self.uncertaintyPanel.theta + self.uncertaintyPanel.phi# Names of variable + parameters in the model)
        nlik = len (lik) # Get number of likelihood functions
        vname = ['prior of %s' % i for i in nvp]

        DP = PF.create(None)
        DP.SetTitle('Prior distributions for the parameters')
        DP.plotDist(allpriors,vname)
        DP.Show()

#---Plot posteriors of theta----------------------------------------------------------------------------
        MP = PF.create(None)
        MP.SetTitle('Theta posteriors')
        MP.plotMeldout(meldout, self.pnames)
        MP.Show()
#---Plot posteriors of phi----------------------------------------------------------------------------
# TODO: extract the values of post_phi at time time for each variable to plot.
        self.plotMelding(x,post_phi,tit='Series After Melding Calibration')
        yt = []
        runs_byvar = []
        for i in post_phi:
            yt.append(transpose(i)) #Extracts the time series arrays and transpose them (the median function needs to have the series in rows, not in columns).

        for v in xrange(nvar):
            runs_byvar.append(array([yt[i][v] for i in xrange(L)]))
        data = [runs_byvar[i][:,-1] for i in xrange(nvar)]
        #vname2 = ['v[%s]' % i for i in xrange(nvar)]
        MP = PF.create(None)
        MP.SetTitle('Phi posteriors at time t='+str(time))
        MP.plotDist(data,self.vnames)
        MP.Show()

    def postPHI(self,meldout,L):
        """
        this function takes the output of the SIR algorithm and calculates the posterior
        distributions of the Phis from the posteriors of the thetas.
        """
        self.post_theta = meldout[1]
        init_conds = array([float(i) for i in self.initValInput.GetValue().strip().split(' ') if i != ''])
        t_start = float(self.modict['start'])
        t_end = float(self.modict['end'])
        t_step = float(self.modict['step'])
        t_range = arange(t_start, t_end+t_step, t_step)
        t_courseList = []
        for i in xrange(L):
            self.run = i
            t_courseList.append(integrate.odeint(self.Equations2,init_conds,t_range, full_output=0, printmessg=0))
            #self.statusBar1.SetStatusText(str(self.run)+'\n')
            init_conds = array([float(i) for i in self.initValInput.GetValue().strip().split(' ') if i != '']) #reset initial conditions between runs

        return (t_range,t_courseList)
    def Equations2(self,y,t):
        """
        Variation of the Equations function to calculate the posterior of phi
        """
        Neq = self.Neq
        pars = self.post_theta
        Npar = len(pars) #get number of parameters
        if self.vnames:
            exec('%s=%s'%(','.join(self.vnames),list(y)))
        ydot = zeros((Neq),'d') #initialize ydot
        p = zeros((Npar),'d') #initialize p
    #---Create Parameter Array----------------------------------------------------------------------------
        for i in xrange(Npar):
            if self.pnames:
                exec("%s=%s"%(self.pnames[i],pars[i][self.run]))
            else:
                p[i] = pars[i][self.run] # Get a new set of parameters for each repeated run
    #---Create equation array----------------------------------------------------------------------------
        eqs = self.ceqs#self.eqnEdit.GetValue().strip().split('\n')
        for k in xrange(Neq):
            ydot[k] = eval(eqs[k]) #dy(k)/dt


        return ydot





    def OnMenu3items0Menu(self, event):
        """
        Opens the about window
        """
        dlg = about.wxDialog1(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

    def initUncertainty(self):
        """
        Initializes the values on the uncertainty Analysis Panel based on
        model specification
        """

        while not self.eqnEdit.GetValue()=='':#get number of ODEs
            val = self.eqnEdit.GetValue().strip().split('\n')
            Neq = len(val)
            break

        if not self.parEdit.GetValue() == '':#get number of parameters
            valp = self.parEdit.GetValue().strip().split('\n')
            Npar = len(valp)
        else:
            Npar = 0

        if self.vnames:
            phi = self.vnames
        else:
            phi = ["Y[%s]" % str(i) for i in xrange(Neq)]

        if Npar > 0:
            if self.pnames:
                theta = self.pnames
            else:
                theta = ['P[%s]' % str(i) for i in xrange(Npar)]

        self.uncertaintyPanel.phi = phi
        self.uncertaintyPanel.theta = theta
        self.uncertaintyPanel.grid_1.CreateGrid(Npar+Neq,Npar+Neq)
        self.uncertaintyPanel.parsCB.AppendItems(theta)
        #self.uncertaintyPanel.createVarList(items) # re-create varList on uncertaintyMiniFrame
        self.uncertaintyPanel.fileName = self.FileName #create local variable on Uncertainty panel with filename
        dir,fname = os.path.split(self.FileName)#[1]
        fname = fname[:-4]+'_unc.spec'
        if fname in os.listdir(dir):
            self.uncertaintyPanel.loadSpecs(fname)

    def OnWxFrame1Close(self, event):
        """
        Things to do before Exiting.
        """
        # Tries to close other windows if they exist
        try:
            DP.Close()
        except (NameError, AttributeError):
            pass
        try:
            self.PF.Close()
        except (NameError, AttributeError):
            pass
        try:
            MP.Close()
        except (NameError, AttributeError):
            pass
        try:
            self.TableOut.Close()
        except (AttributeError, NameError):
            pass
        try:
            self.uncertaintyPanel.Close()
        except (AttributeError, NameError):
            pass
        sys.exit()

    def OnMenu2Items1Menu(self, event):
        """
        Call the quiver plot menu
        """
        if not self.ModLoaded:
            dlg = wx.MessageDialog(self, 'Please Open or Create a Model First.',
              'No Model Available', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
                return


        if not self.modbuilt:
            self.BuildModel()
        if self.vnames:
            QF.ch = self.vnames
        else:
            QF.ch = ['y[%s]'%i for i in xrange(self.Neq)]
        #print self.Neq, self.FileName
        Vector = QF.create(None)
        Vector.modict = self.modict
        Vector.initsCtrl.SetValue(self.modict['init'])
        inits = array([float(i) for i in self.modict['init'].strip().split(' ')])
        Vector.limitsCtrl.SetValue("%s %s %s %s"%(min(inits),min(inits)*10,min(inits),min(inits)*10))
        Vector.Show()

    def OnToolBar1OpentoolTool(self, event):
        return self.OnMenu1items0Menu(event)

    def OnToolBar1SavetoolTool(self, event):
        return self.OnMenu1items1Menu(event)

    def OnMenu3MbhelpMenu(self, event):
        helpviewer.main(['','MB.hhp'])

class Future:
    """
    By David Perry - http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/84317
    To run a function in a separate thread, simply put it in a Future:

    >>> A=Future(longRunningFunction, arg1, arg2 ...)

    It will continue on its merry way until you need the result of your function.
    You can read the result by calling the Future like a function, for example:

    >>> print A()

    If the Future has completed executing, the call returns immediately.
    If it is still running, then the call blocks until the function completes.
    The result of the function is stored in the Future, so subsequent calls to
    it return immediately.

    A few caveats:
    Since one wouldn't expect to be able to change the result of a function,
    Futures are not meant to be mutable. This is enforced by requiring the
    Future to be "called", rather than directly reading __result. If desired,
    stronger enforcement of this rule can be achieved by playing
    with __getattr__ and __setattr__.

    The Future only runs the function once, no matter how many times you
    read it. You will have to re-create the Future if you want to re-run your
    function; for example, if the function is sensitive to the time of day.

    For more information on Futures, and other useful parallel programming
    constructs, read Gregory V. Wilson's _Practical Parallel Programming_.
    """
    def __init__(self,func,*param):
        # Constructor
        self.__done=0
        self.__result=None
        self.__status='working'

        self.__C=Condition()   # Notify on this Condition when result is ready

        # Run the actual function in a separate thread
        self.__T=Thread(target=self.Wrapper,args=(func,param))
        self.__T.setName("FutureThread")
        self.__T.start()

    def __repr__(self):
        return '<Future at '+hex(id(self))+':'+self.__status+'>'

    def __call__(self):
        self.__C.acquire()
        while self.__done==0:
            self.__C.wait()
        self.__C.release()
        # We deepcopy __result to prevent accidental tampering with it.
        a=copy.deepcopy(self.__result)
        return a

    def Wrapper(self, func, param):
        # Run the actual function, and let us housekeep around it
        self.__C.acquire()
        try:
            self.__result=func(*param)
        except:
            self.__result="Exception raised within Future"
        self.__done=1
        self.__status=`self.__result`
        self.__C.notify()
        self.__C.release()
