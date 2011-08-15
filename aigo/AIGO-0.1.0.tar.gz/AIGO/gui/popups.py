"""
popus.py

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

import wx
import wx.lib.dialogs

class Popup:
    """Class for handling all our fancy GUI stuff"""
    def msg(self, frame, string, title):
        """Display STRING in a wx.MessageDialog"""
        dlg = wx.lib.dialogs.ScrolledMessageDialog(frame, string, title)
        #aStyle=wx.OK|wx.ICON_EXCLAMATION
        dlg.ShowModal()
        dlg.Destroy()

    def error(self, frame, string, title="Error"):
        """Display STRING in a wx.MessageDialog"""
        wx.lib.dialogs.messageDialog(frame, string, title,
                                     aStyle=wx.OK | wx.ICON_ERROR)

    def choice(self, frame, string, title="Question"):
        """Display STRING in a wx.MessageDialog"""
        ret = wx.lib.dialogs.messageDialog(frame, string, title,
                                           aStyle=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        return ret
