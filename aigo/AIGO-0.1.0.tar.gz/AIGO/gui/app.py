"""
app.py

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

from pylab import *
import os

import wx
from ObjectListView import FastObjectListView, ColumnDefn

import pydoc


from PIL import Image as Image
from AIGO.gui import project, popups, grid, gui


from AIGO import allAspect
from AIGO.Statistics import registerStat
from AIGO.Plot import PlotFA, registerPlot
from AIGO.IO import IOType


def PNGtoBitmap(fileName, resize=None):

    mypilimage = Image.open(fileName, "r")
    if resize:
        #mypilimage.resize(resize, , Image.ANTIALIAS)
        mypilimage.thumbnail( resize, Image.ANTIALIAS)
    mywximage = wx.EmptyImage(mypilimage.size[0],mypilimage.size[1])
    mywximage.SetData(mypilimage.convert("RGB").tostring())
    mywximage.SetAlphaData(mypilimage.convert("RGBA").tostring()[3::4])
    return wx.BitmapFromImage(mywximage)


def  setNewID(wid):
    ID=wx.NewId()
    wid.SetId(ID)
    return ID





class AIGOApp(wx.PySimpleApp):
    
    def OnInit(self, doSplash=False):

        #-----------------------------------------------------
        #                     IMAGES
        #-----------------------------------------------------
        import os
        import AIGO.gui
        self.guiDir=os.path.dirname(AIGO.gui.__file__)
        self.AIGOBmp = PNGtoBitmap("%s/AIGO.png" % self.guiDir)
        self.checkBmp = PNGtoBitmap("%s/check.png" % self.guiDir, resize=[17,13])
        self.crossBmp = PNGtoBitmap("%s/cross.png" % self.guiDir, resize=[13,13])

        self.icon = wx.EmptyIcon()
        self.icon.CopyFromBitmap(self.AIGOBmp)



        #-----------------------------------------------------
        #                     SPLASH
        #-----------------------------------------------------
        if doSplash:
            splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
            splashDuration = 2000 # milliseconds
            splash=wx.SplashScreen(self.AIGOBmp, splashStyle,splashDuration, None)
            splash.Show(True)
        
        self.popup = popups.Popup()

        #-----------------------------------------------------
        #                     FRAMES
        #-----------------------------------------------------

        #Create main frame
        self.frame = gui.AIGOFrame(None, -1, "")
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.frame.SetIcon(self.icon)
        self.statusField=self.frame.statusbar.GetFields()

        #Create new project frame
        self.npFrame = gui.NewProjectFrame(self.frame, -1, "New Project")
        self.npFrame.Show(False)
        self.npFrame.SetIcon(self.icon)

        #Create new functional annotation frame
        self.FAFrame = gui.FAFrame(self.frame, -1, "Add Functional Annotation")
        self.FAFrame.combo_box_FileType.Clear()
        self.FAFrame.combo_box_FileType.AppendItems(sort(IOType.keys()))
        self.FAFrame.Show(False)
        self.FAFrame.SetIcon(self.icon)

        #Create view annotation set frame
        self.ViewFrame = gui.ViewFrame(self.frame, -1, "View gene product annotations")
        self.ViewFrame.Show(False)
        self.ViewFrame.SetIcon(self.icon)

        #-----------------------------------------------------
        #                     LIST FA
        #-----------------------------------------------------
        self.frame.notebook.list_FA.InsertColumn(0, "Status")
        self.frame.notebook.list_FA.InsertColumn(1, "Name")
        self.frame.notebook.list_FA.InsertColumn(2, "File", wx.LIST_FORMAT_RIGHT)
        self.frame.notebook.list_FA.InsertColumn(3, "File Type")

        self.frame.notebook.list_FA.SetColumnWidth(0, 100)
        self.frame.notebook.list_FA.SetColumnWidth(1, 200)
        self.frame.notebook.list_FA.SetColumnWidth(2, 400)
        self.frame.notebook.list_FA.SetColumnWidth(3, 100)


        #-----------------------------------------------------
        #                     STATISTICS
        #-----------------------------------------------------
        self.workflow=list()
        self.viewStat=dict()
        for statistics in registerStat.getAll():
            if hasattr(self.frame.notebook, 'checkbox_%s' % statistics):
                self.viewStat[statistics]=True
                self.workflow.append(statistics)

        self.frame.notebook.button_Export.SetLabel("Export")

        for statistics in self.viewStat:
            bmp=getattr(self.frame.notebook, 'bitmap_%s' % statistics)
            bmp.SetBitmap(self.crossBmp)

        #-----------------------------------------------------
        #                     COMPARE
        #-----------------------------------------------------
        self.frame.notebook.button_Update_Venn.SetLabel("Venn diagram")
        self.frame.notebook.button_Update_FuncSim.SetLabel("Functional Similarity")
                
        for name in ["FA1", "FA2"]:
            lst=getattr(self.frame.notebook, 'combo_box_Compare_%s' % name)
            lst.SetName(name)

        compareColumns = [
            ColumnDefn("Gene Product",            "left", 300, valueGetter="gp", minimumWidth=40, maximumWidth=500),
            ColumnDefn("Annotations in first FA", "right", 250, valueGetter="nb1", minimumWidth=40, maximumWidth=300),
            ColumnDefn("Annotations in second FA", "right", 250, valueGetter="nb2", minimumWidth=40, maximumWidth=300),
            ColumnDefn("Functional Similarity",   "right", 200, valueGetter="funcSim", minimumWidth=40)
            ]

        for aspect in allAspect:
            bmp=getattr(self.frame.notebook, 'bitmap_%s' % aspect)
            size=bmp.GetSize().Get()
            bmp.SetBitmap(self.AIGOBmp)
            
            btn=getattr(self.frame.notebook, 'button_Compare_%s' % aspect)
            btn.SetLabel("View")

            lst=getattr(self.frame.notebook, 'list_ctrl_Compare_%s' % aspect)
            lst.SetName(aspect)

            lst.SetColumns(compareColumns)

            btn=getattr(self.frame.notebook, 'button_Compare_%s' % aspect)
            btn.SetName(aspect)


        #-----------------------------------------------------
        #                     PLOT
        #-----------------------------------------------------

        #-----------------------------------------------------
        #                     EVENTS
        #-----------------------------------------------------
        
        # Menu Events
        #
        #wx.EVT_MENU(self, gui.ID_BLURB, self.MenuBlurb)
        #self.frame.SetAcceleratorTable(wx.AcceleratorTable([
        #                (wx.ACCEL_NORMAL, wx.WXK_F1, gui.ID_EXIT),
        #                (wx.ACCEL_NORMAL, wx.WXK_F2, gui.ID_BLURB),
        #                ]))

        #Menu
        wx.EVT_MENU(self, gui.MENU_NEW,  self.MenuNew)
        wx.EVT_MENU(self, gui.MENU_OPEN, self.MenuOpen)
        wx.EVT_MENU(self, gui.MENU_SAVE, self.MenuSave)
        wx.EVT_MENU(self, gui.MENU_QUIT, self.MenuQuit)
        wx.EVT_MENU(self, gui.MENU_ABOUT, self.MenuAbout)

        #New Project        
        wx.EVT_BUTTON(self, self.npFrame.button_DirectoryChoose.GetId(),  self.OnNewProjectDirChoose)
        wx.EVT_BUTTON(self, setNewID(self.npFrame.button_NewProjectOK),     self.OnNewProjectOK)
        wx.EVT_BUTTON(self, setNewID(self.npFrame.button_NewProjectCancel), self.OnNewProjectCancel)
        
        #Data
        wx.EVT_BUTTON(self, self.frame.notebook.button_RefSetChoose.GetId(), self.OnBrowseRefSet)
        wx.EVT_BUTTON(self, setNewID(self.frame.notebook.button_RefSetLoad),   self.OnLoadRefSet)

        wx.EVT_BUTTON(self, self.frame.notebook.button_GOChoose.GetId(), self.OnBrowseGO)
        wx.EVT_BUTTON(self, setNewID(self.frame.notebook.button_GOLoad),   self.OnLoadGO)

        #Add FA
        wx.EVT_BUTTON(self, self.frame.notebook.button_AddFA.GetId(),    self.OnAddFA)
        wx.EVT_BUTTON(self, self.frame.notebook.button_RemoveFA.GetId(), self.OnRemoveFA)
        wx.EVT_BUTTON(self, self.frame.notebook.button_LoadFA.GetId(),   self.OnLoadFA)
        
        wx.EVT_BUTTON(self, self.FAFrame.button_FileChoose.GetId(), self.OnFAFileChoose)
        wx.EVT_BUTTON(self, setNewID(self.FAFrame.button_FAOK),       self.OnFAOK)
        wx.EVT_BUTTON(self, setNewID(self.FAFrame.button_FACancel),   self.OnFACancel)

        #Statistics
        wx.EVT_BUTTON(self, self.frame.notebook.button_Apply.GetId(),   self.OnStatApply)
        for statistics in registerStat.getAll():
            cb=self.frame.notebook.__dict__.get('checkbox_%s' % statistics, None)
            if cb:
                cb.SetName(statistics)
                wx.EVT_CHECKBOX(self,     cb.GetId(),  self.OnStatCheck)

        wx.EVT_BUTTON(self, setNewID(self.frame.notebook.button_Export),   self.OnStatExport)

        #Compare
        wx.EVT_BUTTON(self, setNewID(self.frame.notebook.button_Update_Venn),   self.OnUpdateVenn)
        wx.EVT_BUTTON(self, setNewID(self.frame.notebook.button_Update_FuncSim),   self.OnUpdateFuncSim)
                
        wx.EVT_SIZE(self.ViewFrame, self.OnResizeView)
        
        for name in ["FA1", "FA2"]:
            lst=getattr(self.frame.notebook, 'combo_box_Compare_%s' % name)
            wx.EVT_COMBOBOX(self, lst.GetId(), self.OnCompareStat)
            
        for aspect in allAspect:
            btn=getattr(self.frame.notebook, 'button_Compare_%s' % aspect)
            wx.EVT_BUTTON(self, setNewID(btn), self.OnCompareView)

            #lst=getattr(self.frame.notebook, 'list_ctrl_Compare_%s' % aspect)
            #wx.EVT_LIST_COL_CLICK(self, setNewID(lst), self.OnCompareColClick)


        #Plot
        wx.EVT_COMBOBOX(self, self.frame.notebook.combo_PlotStat.GetId(),   self.OnStatPlot)
        
        return True

