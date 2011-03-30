#!/usr/bin/python
#
# test the MotorPanel

import wx
import sys
import time
import epics

from epics.wx import finalize_epics, pvText

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()
ID_FREAD = wx.NewId()
ID_FSAVE = wx.NewId()
ID_CONF  = wx.NewId()


class SimpleFrame(wx.Frame):
    def __init__(self, parent=None, *args, **kwds):

        wx.Frame.__init__(self, parent, wx.ID_ANY, '',
                         wx.DefaultPosition, wx.Size(220,100), **kwds)
        self.SetTitle(" Epics Display Page")

        wx.EVT_CLOSE(self, self.onClose)        

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self)
        self.desc  = wx.StaticText(self.panel, label='Value:', size=(60,25),
                                   style=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)
        
        self.motorval =  pvText(self.panel, size=(105, 25),  fg=wx.BLUE,
                                style=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT)

        self.sizer.Add(self.desc,     0, wx.ALIGN_CENTER|wx.GROW|wx.ALL, 4)
        self.sizer.Add(self.motorval, 0, wx.ALIGN_CENTER|wx.GROW|wx.ALL, 4)
        
        self.motorval.set_pv('13XRM:m1.VAL')
        
        self.SetSizer(self.sizer)
        self.sizer.Fit(self.panel)
        self.Refresh()
        print '========================================='

    def onClose(self, event):
        finalize_epics()
        self.Destroy()

if __name__ == '__main__':
    app = wx.App(redirect=False)
    SimpleFrame().Show()
    
    app.MainLoop()


