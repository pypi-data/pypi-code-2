#!/usr/bin/env python
#Boa:App:BoaApp
# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        PyMB.py
# Purpose:     Mathematical ODE Model simulator
#
# Author:      Flavio Codeco Coelho
#
# Created:     2003/02/04
# RCS-ID:      $Id: PyMB.py,v 1.6 2004/01/13 10:51:43 fccoelho Exp $
# Copyright:   (c) 2003-2008 Flavio Codeco Coelho <fccoelho@fiocruz.br>
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

import wxversion
wxversion.ensureMinimal('2.8')

import wx
import wxFrame1

##import psyco
##psyco.full

modules ={u'MB': [0, '', u'MB.hhp'],
 'Model': [0, '', 'Model.py'],
 'PlotFigure': [0, 'Plotting Frame', 'PlotFigure.py'],
 '__version__': [0, '', '__version__.py'],
 'about': [0, '', 'about.py'],
 u'cwt': [0, '', u'cwt.py'],
 'icones': [0, '', 'icones.py'],
 'lhsframe': [0, '', 'lhsframe.py'],
 'odexml': [0, '', 'odexml.py'],
 'quivVarFrame': [0, '', 'quivVarFrame.py'],
 'uncertaintyMiniFrame': [0,
                          'Mini frame with parameters for uncertainty analysis.',
                          'uncertaintyMiniFrame.py'],
 'wxFrame1': [1, 'Main frame of Application', 'wxFrame1.py'],
 'wxFrame2': [0, '', 'wxFrame2.py']}

class BoaApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.main = wxFrame1.create(None)
        # needed when running from Boa under Windows 9X
        self.SetTopWindow(self.main)
        self.main.Show();self.main.Hide();self.main.Show()
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
