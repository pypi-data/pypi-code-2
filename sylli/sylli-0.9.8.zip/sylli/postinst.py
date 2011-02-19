#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        post-install
# Purpose:     post-install script
#
# Author:      Luca Iacoponi
#
# Created:     08/01/2011
# Copyright:   (c) Luca Iacoponi 2011
# Licence:     Apache 2
#-------------------------------------------------------------------------------

""" Execute post-install operations """

import os
import wx
import sylli

def main():
    """ Run post-install user alert.
    """
    if os.path.exists(sylli.filepath.get_path('config_dir')):
        user_alert()

def user_alert():
    """ Alert the user that a configuration directory already exists and
    eventually overwrite the user sonority with the installation one.
    >>> user_alert()
    """
    app = wx.App(False)
    frame = wx.Frame(None, wx.ID_ANY, "Sylli")
    frame.Show(False)
    inst_msg = "It seems that you already have a user directory in: \n" + \
    sylli.filepath.get_path('config_dir')
    inst_msg += """
This happens when you upgrade an old version of Sylli or if you're reinstalling.
It is possible that your old sonority.txt is no longer compatible with Sylli.
Do you want to install the new sonority.txt anyway?
(You can save a copy meanwhile)
"""
    dlg = wx.MessageDialog(frame, inst_msg,
                           'Sylli already installed?',
                           wx.YES_NO | wx.YES_DEFAULT | wx.ICON_EXCLAMATION)

    if dlg.ShowModal() == wx.ID_YES:
        sylli.reset_son()
    dlg.Destroy()
    frame.Destroy()

if __name__ == '__main__':
    main()
