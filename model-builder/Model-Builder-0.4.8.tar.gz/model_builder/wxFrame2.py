#-----------------------------------------------------------------------------
# Name:        wxFrame2.py
# Purpose:     Data output frame (wx.grid.Grid)
#
# Author:      <Flavio Codeco Coelho>
#
# Created:     2003/02/04
# RCS-ID:      $Id: wxFrame2.py,v 1.3 2004/01/13 10:51:44 fccoelho Exp $
# Copyright:   (c) 2003-6 Flavio Codeco Coelho <fccoelho@fiocruz.br>
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
#Boa:Frame:wxFrame2

#import wxversion

import wx
import wx.grid
from numpy import *
import icones,cwt
import PlotFigure as PF
from pylab import show


def create(parent):
    return wxFrame2(parent)

[wxID_WXFRAME2, wxID_WXFRAME2GRID1, wxID_WXFRAME2PANEL1,
 wxID_WXFRAME2STATUSBAR1, wxID_WXFRAME2TOOLBAR1,
] = [wx.NewId() for _init_ctrls in range(5)]

[wxID_WXFRAME2TOOLBAR1CWT, wxID_WXFRAME2TOOLBAR1PLOT,
 wxID_WXFRAME2TOOLBAR1PSD, wxID_WXFRAME2TOOLBAR1TOOLS0,
] = [wx.NewId() for _init_coll_toolBar1_Tools in range(4)]

class wxFrame2(wx.Frame):
    def _init_coll_panelSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.panel1, 1, border=0, flag=wx.EXPAND)

    def _init_coll_sheetBSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.grid1, 1, border=0, flag=wx.EXPAND)

    def _init_coll_toolBar1_Tools(self, parent):
        # generated method, don't edit

        parent.AddTool(bitmap=icones.getSaveBitmap(),
              id=wxID_WXFRAME2TOOLBAR1TOOLS0, isToggle=False,
              longHelpString='Save this table', pushedBitmap=wx.NullBitmap,
              shortHelpString='Save As')
        parent.DoAddTool(bitmap=icones.getplotBitmap(),
              bmpDisabled=wx.NullBitmap, id=wxID_WXFRAME2TOOLBAR1PLOT,
              kind=wx.ITEM_NORMAL, label='plotSel',
              longHelp='Plot selected column', shortHelp='Plot')
        parent.DoAddTool(bitmap=icones.getSpectrumBitmap(),
              bmpDisabled=wx.NullBitmap, id=wxID_WXFRAME2TOOLBAR1PSD,
              kind=wx.ITEM_NORMAL, label='Spectrogram',
              longHelp='Spectrogram display', shortHelp='Spectrogram')
        parent.DoAddTool(bitmap=icones.getCWTBitmap(),
              bmpDisabled=wx.NullBitmap, id=wxID_WXFRAME2TOOLBAR1CWT,
              kind=wx.ITEM_NORMAL, label='Continuous Wavelet Transform',
              longHelp='Continuous Wavelet Transform',
              shortHelp='Wavelet Transform')
        self.Bind(wx.EVT_TOOL, self.OnToolbar1tools0Tool,
              id=wxID_WXFRAME2TOOLBAR1TOOLS0)
        self.Bind(wx.EVT_TOOL, self.OnToolBar1Tools1Tool,
              id=wxID_WXFRAME2TOOLBAR1PLOT)
        self.Bind(wx.EVT_TOOL, self.OnToolBar1PsdTool,
              id=wxID_WXFRAME2TOOLBAR1PSD)
        self.Bind(wx.EVT_TOOL, self.OnToolBar1CwtTool,
              id=wxID_WXFRAME2TOOLBAR1CWT)

        parent.Realize()

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='Status')

        parent.SetStatusWidths([-1])

    def _init_sizers(self):
        # generated method, don't edit
        self.panelSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.sheetBSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_panelSizer_Items(self.panelSizer)
        self._init_coll_sheetBSizer_Items(self.sheetBSizer)

        self.grid1.SetSizer(self.sheetBSizer)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_WXFRAME2, name='', parent=prnt,
              pos=wx.Point(778, 556), size=wx.Size(686, 491),
              style=wx.DEFAULT_FRAME_STYLE, title='Output Table')
        self.SetClientSize(wx.Size(686, 491))
        self.SetAutoLayout(True)
        self.SetToolTipString('')

        self.statusBar1 = wx.StatusBar(id=wxID_WXFRAME2STATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.toolBar1 = wx.ToolBar(id=wxID_WXFRAME2TOOLBAR1, name='toolBar1',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(204, 48),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        self.toolBar1.SetToolTipString('')
        self.SetToolBar(self.toolBar1)

        self.panel1 = wx.Panel(id=wxID_WXFRAME2PANEL1, name='panel1',
              parent=self, pos=wx.Point(1, 1), size=wx.Size(684, 464),
              style=wx.TAB_TRAVERSAL)

        self.grid1 = wx.grid.Grid(id=wxID_WXFRAME2GRID1, name='grid1',
              parent=self.panel1, pos=wx.Point(0, 0),size=wx.Size(684, 464),
              style=0)
        self.grid1.SetAutoLayout(True)
        self.grid1.SetMinSize(wx.Size(684, 464))
        self.grid1.SetToolTipString(u'Data grid')
        self.grid1.SetThemeEnabled(True)

        self._init_coll_toolBar1_Tools(self.toolBar1)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.filename = None

    def OnToolbar1tools0Tool(self, event):
        dlg = wx.FileDialog(self, "Save Data As", ".", "", "*.dat", wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                f = open(filename,'w')
                for k in xrange(self.grid1.GetNumberCols()):
                    f.write(self.table.GetColLabelValue(k)+',')
                f.write('\n')
                for l in self.data:
                    l.tofile(f, sep="," )
                    f.write('\n')
#                for i in xrange(self.table.GetNumberRows()):
#                    if i == 0:
#                        for k in xrange(self.grid1.GetNumberCols()):
#                            f.write(self.table.GetColLabelValue(k)+',')
#                        f.write('\n')
#                    for j in xrange(self.table.GetNumberCols()):
#                        f.write(self.grid1.GetCellValue(i,j)+',')
#                    f.write('\n')
#                f.close()
        finally:
            f.close()
            dlg.Destroy()


    def fillGrid(self,data):
        """
        this function will fill the spreadsheet
        """
        self.data = data
        self.table = TableBase(self.grid1,data)
        self.grid1.SetTable(self.table,True)

    def OnToolBar1Tools1Tool(self, event):
        """
        Plot Selected columns
        """

        sel = self.grid1.GetSelectedCols()
        #data = self.createDataMatrix()
        leg = tuple([self.table.GetColLabelValue(i) for i in self.grid1.GetSelectedCols()])
        y = []
        for i in sel:
            y.append(self.data[:,i])


        p=PF.create(None)
        p.SetTitle('Selected Variables')
        p.plot(self.data[:,0],y,leg)
        p.Show()


    def createDataMatrix(self):
        """
        create a Numeric array with the contents of the spreadsheet
        """
        rows = self.grid1.GetNumberRows()
        cols = self.grid1.GetNumberCols()
        data = zeros((rows-2,cols),float)
        for i in xrange(rows-2):
            for j in xrange(cols):
                data[i,j] = float(self.grid1.GetCellValue(i+1,j))
        print data, data.shape, data[0,0]
        return data


    def OnToolBar1PsdTool(self, event):
        """
        Plots the spectrogram of a vector
        """
        sel = self.grid1.GetSelectedCols()
        if len(sel)!=1:
            dlg = wx.MessageDialog(self, 'You have selected %s columns.\nPlease select only one.'%len(sel),
              'Selection Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        coln = self.grid1.GetSelectedCols()[0]#number of the selected column
        #print coln, type(coln)
        coll = self.grid1.GetNumberRows()#height of sel. column.
        name = self.table.GetColLabelValue(coln)
        y= self.data[:, coln]


        p=PF.create(None)
        p.SetTitle('Spectrogram')
        p.plotSpecg(y,name)
        p.Show()

        q=PF.create(None)
        q.SetTitle('Power Spectrum')
        q.plotSpec(y,name)
        q.Show()

    def OnToolBar1CwtTool(self, event):
        """
        Plots the continuous wavelet transform of a given series.
        """
        origin = 'image'
        interpolation = 'bilinear'
        sel = self.grid1.GetSelectedCols()
        if len(sel)!=1:
            dlg = wx.MessageDialog(self, 'You have selected %s columns.\nPlease select only one.'%len(sel),
              'Selection Error', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return
        coln = self.grid1.GetSelectedCols()[0]#number of the selected column
        #print coln, type(coln)
        coll = self.grid1.GetNumberRows()#height of sel. column.
        name = self.table.GetColLabelValue(coln)
        y= self.data[:, coln]
#        y = zeros(coll,float)
#        for i in xrange(coll):
#            try:
#                y[i] = float(self.grid1.GetCellValue(i,coln))
#            except: print i

        c = cwt.cwt(y,nvoice=8,wavelet="Morlet",oct=2,scale=4)
        cwt.imageCWT(c,title='%s Continuous Wavelet Transform\nMorlet wavelet'% name,origin=origin,interpolation=interpolation)
        show()

class TableBase(wx.grid.PyGridTableBase):
    """
    This class will store a numpy array to fill
    the grid
    """
    def __init__(self, parentgrid, data):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.grid = parentgrid
        self.collabels = range(data.shape[1]+6)

    def GetNumberRows(self):
        return self.data.shape[0]

    def GetNumberCols(self):
        return self.data.shape[1]

    def GetValue(self, row, col):
        return self.data[row][col]

    def GetColLabelValue(self, col):
        return self.collabels[col]

    def SetColLabelValue(self, col, label):
        self.collabels[col]= label

if __name__ == '__main__':
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = create(None)
    frame.Show()

    app.MainLoop()
