print 'Running post-install...'

import sys,os

if ('install' in sys.argv) and ('--help' not in sys.argv) and ('--help-commands' not in sys.argv):
    import wx_py

    d = wx_py.__path__[0]

    if sys.platform == 'win32':
        import pythoncom
        from win32com.shell import shell, shellcon
        shortcut = pythoncom.CoCreateInstance (
          shell.CLSID_ShellLink,
          None,
          pythoncom.CLSCTX_INPROC_SERVER,
          shell.IID_IShellLink
        )
        shortcut.SetPath (os.path.join(d,'PySlices.py'))
        shortcut.SetDescription ("PySlices "+str(wx_py.version.VERSION))
        shortcut.SetIconLocation (d, 0)
        
        desktop_path = shell.SHGetFolderPath (0, shellcon.CSIDL_DESKTOP, 0, 0)
        persist_file = shortcut.QueryInterface (pythoncom.IID_IPersistFile)
        persist_file.Save (os.path.join (desktop_path, "PySlices.lnk"), 0)
    elif sys.platform == 'linux2':
        fid = open(os.path.join(os.path.expanduser('~'),'Desktop','PySlices.desktop'),'w')
        fid.write('''#!/usr/bin/env xdg-open
[Desktop Entry]
Name=PySlices
Comment=None
Exec=python -m wx_py.PySlices
Icon='''+os.path.join(d,'PySlices.png')+'''
Terminal=False
Type=Application
Categories=Development;IDE
StartupNotify=true
MimeType=text/x-python;
GenericName=PySlices
''')
        fid.close()
    elif sys.platform == 'darwin':
        fid = open(os.path.join(os.path.expanduser('~'),'Desktop','PySlices.command'),'w')
        fid.write('''#!/bin/env sh
python -m wx_py.PySlices\n''')
        fid.close()
