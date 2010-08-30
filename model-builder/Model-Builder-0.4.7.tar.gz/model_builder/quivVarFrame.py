#-----------------------------------------------------------------------------
# Name:        quivVarFrame.py
# Purpose:     Miniframe to do the vector field plot
#
# Author:      Flavio Codeco Coelho
#
# Created:     2006/08/20
# RCS-ID:      $Id: quivVarFrame.py $
# Copyright:   (c) 2004-2006
# Licence:     GPL
# New field:   Whatever
#-----------------------------------------------------------------------------
#Boa:MiniFrame:quivVarFrame
#import wxversion
#wxversion.select('2.6')
import wx
import wx.lib.buttons
import PlotFigure as PF
from Model import Model
from numpy import *
from numpy.random import normal

ch=['a','b','c']
def create(parent):
    return quivVarFrame(parent)

[wxID_QUIVVARFRAME, wxID_QUIVVARFRAMEDRAWTRAJCHECK,
 wxID_QUIVVARFRAMEINITSCTRL, wxID_QUIVVARFRAMEINITSTEXT,
 wxID_QUIVVARFRAMELENGTHTEXT, wxID_QUIVVARFRAMELIMITSCTRL,
 wxID_QUIVVARFRAMELIMITSTEXT, wxID_QUIVVARFRAMEPLOTBUTTON,
 wxID_QUIVVARFRAMETRAJBOX, wxID_QUIVVARFRAMETRAJLENSPIN,
 wxID_QUIVVARFRAMEVARLIST1, wxID_QUIVVARFRAMEVARLIST2,
 wxID_QUIVVARFRAMEXVARTEXT, wxID_QUIVVARFRAMEYVARTEXT,
] = [wx.NewId() for _init_ctrls in range(14)]

class quivVarFrame(wx.MiniFrame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.MiniFrame.__init__(self, id=wxID_QUIVVARFRAME, name='quivVarFrame',
              parent=prnt, pos=wx.Point(449, 282), size=wx.Size(334, 244),
              style=wx.DEFAULT_FRAME_STYLE,
              title='Select Variables')
        self.SetClientSize(wx.Size(334, 244))
        self.Center(wx.BOTH)
        self.SetAutoLayout(True)
        self.SetMinSize(wx.Size(334, 244))
        self.SetMaxSize(wx.Size(334, 244))

        self.xvarText = wx.StaticText(id=wxID_QUIVVARFRAMEXVARTEXT,
              label='X - axis', name='xvarText', parent=self, pos=wx.Point(16,
              16), size=wx.Size(48, 16), style=0)

        self.yvarText = wx.StaticText(id=wxID_QUIVVARFRAMEYVARTEXT,
              label='Y - axis', name='yvarText', parent=self, pos=wx.Point(200,
              16), size=wx.Size(64, 16), style=0)

        self.varList1 = wx.ComboBox(choices=ch, id=wxID_QUIVVARFRAMEVARLIST1,
              name='varList1', parent=self, pos=wx.Point(16, 40),
              size=wx.Size(128, 24), style=0, value='Select Variable')
        self.varList1.SetLabel('')
        self.varList1.SetToolTipString('Select variable for the X axis.')
        self.varList1.Bind(wx.EVT_COMBOBOX, self.OnVarList1Combobox,
              id=wxID_QUIVVARFRAMEVARLIST1)

        self.varList2 = wx.ComboBox(choices=ch, id=wxID_QUIVVARFRAMEVARLIST2,
              name='varList2', parent=self, pos=wx.Point(192, 40),
              size=wx.Size(128, 25), style=0, value='Select Variable')
        self.varList2.SetLabel('')
        self.varList2.SetToolTipString('Select Variable for the Y axis.')
        self.varList2.Bind(wx.EVT_COMBOBOX, self.OnVarList2Combobox,
              id=wxID_QUIVVARFRAMEVARLIST2)

        self.trajBox = wx.StaticBox(id=wxID_QUIVVARFRAMETRAJBOX,
              label='Trajectory Plot', name='trajBox', parent=self,
              pos=wx.Point(16, 120), size=wx.Size(304, 112), style=0)
        self.trajBox.SetMinSize(wx.Size(304, 130))
        self.trajBox.SetBestFittingSize(wx.Size(304, 112))

        self.drawTrajCheck = wx.CheckBox(id=wxID_QUIVVARFRAMEDRAWTRAJCHECK,
              label='Draw trajectory', name='drawTrajCheck', parent=self,
              pos=wx.Point(32, 136), size=wx.Size(136, 24), style=0)
        self.drawTrajCheck.SetValue(False)
        self.drawTrajCheck.SetToolTipString('Check to superimpose a trajectory on the state diagram.')
        self.drawTrajCheck.SetThemeEnabled(True)
        self.drawTrajCheck.Bind(wx.EVT_CHECKBOX, self.OnDrawTrajCheckCheckbox,
              id=wxID_QUIVVARFRAMEDRAWTRAJCHECK)

        self.initsText = wx.StaticText(id=wxID_QUIVVARFRAMEINITSTEXT,
              label='Initial Conditions:', name='initsText', parent=self,
              pos=wx.Point(32, 176), size=wx.Size(112, 16), style=0)
        self.initsText.Enable(False)

        self.initsCtrl = wx.TextCtrl(id=wxID_QUIVVARFRAMEINITSCTRL,
              name='initsCtrl', parent=self, pos=wx.Point(144, 168),
              size=wx.Size(160, 24), style=0, value='')
        self.initsCtrl.SetToolTipString('Enter the initial conditions for the trajectory.')
        self.initsCtrl.SetThemeEnabled(True)
        self.initsCtrl.Enable(False)

        self.trajlenSpin = wx.SpinCtrl(id=wxID_QUIVVARFRAMETRAJLENSPIN,
              initial=10, max=5000, min=2, name='trajlenSpin', parent=self,
              pos=wx.Point(88, 200), size=wx.Size(72, 24),
              style=wx.SP_ARROW_KEYS)
        self.trajlenSpin.SetValue(10)
        self.trajlenSpin.SetThemeEnabled(True)
        self.trajlenSpin.Enable(False)

        self.lengthText = wx.StaticText(id=wxID_QUIVVARFRAMELENGTHTEXT,
              label='Length:', name='lengthText', parent=self, pos=wx.Point(32,
              208), size=wx.Size(56, 16), style=0)
        self.lengthText.Enable(False)

        self.plotButton = wx.lib.buttons.GenButton(id=wxID_QUIVVARFRAMEPLOTBUTTON,
              label='Plot', name='plotButton', parent=self, pos=wx.Point(232,
              80), size=wx.Size(89, 31), style=0)
        self.plotButton.Bind(wx.EVT_BUTTON, self.OnPlotButtonButton,
              id=wxID_QUIVVARFRAMEPLOTBUTTON)

        self.limitsText = wx.StaticText(id=wxID_QUIVVARFRAMELIMITSTEXT,
              label='Limits:', name='limitsText', parent=self, pos=wx.Point(16,
              88), size=wx.Size(48, 16), style=0)

        self.limitsCtrl = wx.TextCtrl(id=wxID_QUIVVARFRAMELIMITSCTRL,
              name='limitsCtrl', parent=self, pos=wx.Point(64, 80),
              size=wx.Size(160, 24), style=0, value='Xmin Xmax Ymin Ymax')
        self.limitsCtrl.SetThemeEnabled(True)
        self.limitsCtrl.SetToolTipString('Enter the axes limits separated by spaces: Xmin Xmax Ymin Ymax')

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.Xselected = self.Yselected = 0

    def OnDrawTrajCheckCheckbox(self, event):
        """
        enable the superimposition of a trajectory on the quiver plot
        """
        if self.drawTrajCheck.IsChecked():
            self.lengthText.Enable(True)
            self.trajlenSpin.Enable(True)
            self.initsCtrl.Enable(True)
            self.initsText.Enable(True)
        else:
            self.lengthText.Enable(False)
            self.trajlenSpin.Enable(False)
            self.initsCtrl.Enable(False)
            self.initsText.Enable(False)
        event.Skip()

    def OnPlotButtonButton(self, event):
        if not self.Xselected and self.Yselected:
            dlg = wx.MessageDialog(self, 'Please select X and Y variables.',
              'Variables not Selected', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
                return


        try:
            self.limits = [float(i) for i in self.limitsCtrl.GetValue().strip().split(' ')]
        except ValueError:
            dlg = wx.MessageDialog(self, 'Please enter only number for the axes limits.',
              'Non numerical limits', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
                return

        inits = array([float(i) for i in self.initsCtrl.GetValue().strip().split(' ')])
        lengt = int(self.trajlenSpin.GetValue())
        if self.drawTrajCheck.IsChecked():

            self.calcPlot(inits,lengt,traj=1)
        else:
            self.calcPlot(inits,lengt,traj=0)
        self.Destroy()


    def calcPlot(self,inits=None,lengt=None,traj=0):
        """
        Generate the data to be plotted
        """
        xstep = (self.limits[1]-self.limits[0])/15.
        ystep = (self.limits[3]-self.limits[2])/15.
        if not inits.any():
            inits = array([float(i) for i in self.modict['init'].strip().split(' ')])
        Plot = PF.create(None)
        trajetoria = []
        if traj:
            M = Model(self.modict['equations'],self.modict['parameters'],inits,lengt)
            results = M.Run()
            #print results[0][0].shape
            trajetoria.append(results[0][0][:,self.var1])
            trajetoria.append(results[0][0][:,self.var2])
            xbump = normal(inits[self.var1],xstep,6)
            ybump = normal(inits[self.var2],ystep,6)
            for i in xrange(6): #calculate
                inits[self.var1] = xbump[i]
                inits[self.var2] = ybump[i]
                M = Model(self.modict['equations'],self.modict['parameters'],inits,lengt)
                results = M.Run()
                #print results[0][0].shape
                trajetoria.append(results[0][0][:,self.var1])
                trajetoria.append(results[0][0][:,self.var2])

        x=[];y=[];u=[];v=[]
        for i in arange(self.limits[0],self.limits[1],xstep):
            for j in arange(self.limits[2],self.limits[3],ystep):
                #print inits, type(inits)
                inits[self.var1] = i
                inits[self.var2] = j
                M = Model(self.modict['equations'],self.modict['parameters'],inits,1)
                results = M.Run()
                #print results[0][0].shape
                x.append(i)
                y.append(j)
                u.append(results[0][0][1,self.var1])
                v.append(results[0][0][1,self.var2])
        x=array(x)
        y=array(y)
        u=array(u)
        v=array(v)
        c = sqrt((u-x)**2+(v-y)**2) #map color to the size of the vector
        Plot.vectorField(x,y,u-x,v-y,c=c,xlabel=self.X,ylabel=self.Y,trajectory=trajetoria)

        Plot.Show()

    def OnVarList1Combobox(self, event):
        self.X = self.varList1.GetValue()
        self.var1 = ch.index(self.X)
        self.Xselected = 1

    def OnVarList2Combobox(self, event):
        self.Y = self.varList2.GetValue()
        self.var2 = ch.index(self.Y)
        self.Yselected = 1




if __name__ == '__main__':
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = create(None)
    frame.Show()

    app.MainLoop()
