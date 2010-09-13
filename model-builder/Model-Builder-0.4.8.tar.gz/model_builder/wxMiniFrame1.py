# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        wxMiniFrame1.py
# Purpose:
#
# Author:      <Flavio Codeco Coelho>
#
# Created:     2003/02/04
# RCS-ID:      $Id: wxMiniFrame1.py,v 1.3 2004/01/13 10:51:44 fccoelho Exp $
# Copyright:   (c) 2003 Flavio Codeco Coelho <fccoelho@uerj.br>
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
#Boa:MiniFrame:wxMiniFrame1

import wx
import wx.lib.buttons
from scipy import gplt
from string import *

def create(parent):
    return wxMiniFrame1(parent)

[wxID_WXMINIFRAME1, wxID_WXMINIFRAME1BUTTON1, wxID_WXMINIFRAME1BUTTON2,
 wxID_WXMINIFRAME1BUTTON3, wxID_WXMINIFRAME1BUTTON4, wxID_WXMINIFRAME1BUTTON5,
 wxID_WXMINIFRAME1BUTTON6, wxID_WXMINIFRAME1BUTTON7,
 wxID_WXMINIFRAME1GENTOGGLEBUTTON1, wxID_WXMINIFRAME1PANEL1,
] = [wx.NewId() for _init_ctrls in range(10)]

class wxMiniFrame1(wx.MiniFrame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.MiniFrame.__init__(self, id=wxID_WXMINIFRAME1, name='', parent=prnt,
              pos= wx.Point(258, 166), size= wx.Size(200, 170),
              style=wx.DEFAULT_FRAME_STYLE, title='Plot Properties')
        self.SetClientSize(wx.Size(200, 170))
        self.SetToolTipString('Edit plot properties')

        self.panel1 = wx.Panel(id=wxID_WXMINIFRAME1PANEL1, name='panel1',
              parent=self, pos= wx.Point(0, 0), size= wx.Size(200, 170),
              style=wx.TAB_TRAVERSAL)
        self.panel1.SetToolTipString('')
        self.panel1.SetLabel('Plot Properties')

        self.button1 = wx.Button(id=wxID_WXMINIFRAME1BUTTON1, label='Title',
              name='button1', parent=self.panel1, pos= wx.Point(14, 14),
              size= wx.Size(80, 22), style=0)
        self.button1.SetToolTipString('Set the title.')
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1Button, id=wxID_WXMINIFRAME1BUTTON1)

        self.button2 = wx.Button(id=wxID_WXMINIFRAME1BUTTON2, label='X title',
              name='button2', parent=self.panel1, pos= wx.Point(14, 44),
              size= wx.Size(80, 22), style=0)
        self.button2.SetToolTipString('Set title of X axis')
        self.button2.SetHelpText('Set X-axis title')
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2Button, id=wxID_WXMINIFRAME1BUTTON2)

        self.button3 = wx.Button(id=wxID_WXMINIFRAME1BUTTON3, label='Y title',
              name='button3', parent=self.panel1, pos= wx.Point(14, 74),
              size= wx.Size(80, 22), style=0)
        self.button3.SetToolTipString('Set title of Y axis')
        self.button3.SetHelpText('Set Y-axis title')
        self.button3.Bind(wx.EVT_BUTTON, self.OnButton3Button, id=wxID_WXMINIFRAME1BUTTON3)

        self.genToggleButton1 = wx.GenToggleButton(ID=wxID_WXMINIFRAME1GENTOGGLEBUTTON1,
              label='Grid', name='genToggleButton1', parent=self.panel1,
              pos= wx.Point(14, 104), size= wx.Size(80, 22), style=0)
        self.genToggleButton1.SetToggle(1)
        self.genToggleButton1.SetToolTipString('Toggle gridlines')
        self.genToggleButton1.Bind(wx.EVT_BUTTON, self.OnGentogglebutton1Button, id=wxID_WXMINIFRAME1GENTOGGLEBUTTON1)

        self.button4 = wx.Button(id=wxID_WXMINIFRAME1BUTTON4, label='Log Scale',
              name='button4', parent=self.panel1, pos= wx.Point(14, 134),
              size= wx.Size(80, 22), style=0)
        self.button4.SetToolTipString('Set logarithm scale for axes, individually.')
        self.button4.Bind(wx.EVT_BUTTON, self.OnButton4Button, id=wxID_WXMINIFRAME1BUTTON4)

        self.button5 = wx.Button(id=wxID_WXMINIFRAME1BUTTON5, label='X limits',
              name='button5', parent=self.panel1, pos= wx.Point(104, 44),
              size= wx.Size(80, 22), style=0)
        self.button5.Bind(wx.EVT_BUTTON, self.OnButton5Button, id=wxID_WXMINIFRAME1BUTTON5)

        self.button6 = wx.Button(id=wxID_WXMINIFRAME1BUTTON6, label='Y limits',
              name='button6', parent=self.panel1, pos= wx.Point(104, 74),
              size= wx.Size(80, 22), style=0)
        self.button6.Bind(wx.EVT_BUTTON, self.OnButton6Button, id=wxID_WXMINIFRAME1BUTTON6)

        self.button7 = wx.Button(id=wxID_WXMINIFRAME1BUTTON7, label='Autoscale',
              name='button7', parent=self.panel1, pos= wx.Point(104, 14),
              size= wx.Size(80, 22), style=0)
        self.button7.Bind(wx.EVT_BUTTON, self.OnButton7Button, id=wxID_WXMINIFRAME1BUTTON7)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnButton1Button(self, event):
        """
        sets the title of the plot on the event
        """
        dlg = wx.TextEntryDialog(self, 'Enter a title for this plot:', 'Plot Title', 'Time Series')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                gplt.title(answer)

        finally:
            dlg.Destroy()

    def OnButton2Button(self, event):
        """
        sets the X axis title of the plot on the event
        """
        dlg = wx.TextEntryDialog(self, 'Enter the X-axis title:', 'X-axis Title', 'Time')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                gplt.xtitle(answer)
        finally:
            dlg.Destroy()




    def OnButton3Button(self, event):
        """
        sets the Y axis title of the plot on the event
        """
        dlg = wx.TextEntryDialog(self, 'Enter the Y-axis title:', 'Y-axis Title', 'Y[i]')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                gplt.ytitle(answer)
        finally:
            dlg.Destroy()

    def OnGentogglebutton1Button(self, event):
        """
        toggle gridlines
        """
        t = self.genToggleButton1.GetValue()
        if t == 1:
            gplt.grid('on')
        else:
            gplt.grid('off')

    def OnButton4Button(self, event):
        """
        log scale on chosen axis
        """
        dlg = wx.SingleChoiceDialog(self, 'Choose Axis', 'Caption', ['X-axis','Y-axis', 'None'])
        try:
            if dlg.ShowModal() == wx.ID_OK:
                selected = dlg.GetStringSelection()
                if selected == 'X-axis':
                    gplt.logx()
                elif selected == 'Y-axis':
                    gplt.logy()
                elif selected == 'None':
                    gplt.logx('off')
                    gplt.logy('off')
        finally:
            dlg.Destroy()

    def OnButton5Button(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter two numbers separated by a space:', 'Define X-Axis Limits', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                lims = [i for i in strip(answer).split(' ') if i!= '']
                gplt.xaxis((float(lims[0]),float(lims[1])))
        finally:
            dlg.Destroy()


        event.Skip()

    def OnButton6Button(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter two numbers separated by a space:', 'Define Y-Axis Limits', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                answer = dlg.GetValue()
                lims = [i for i in strip(answer).split(' ') if i!= '']
                gplt.yaxis((float(lims[0]),float(lims[1])))

        finally:
            dlg.Destroy()


        event.Skip()

    def OnButton7Button(self, event):
        gplt.autoscale()
        event.Skip()
