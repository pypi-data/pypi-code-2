'''
Created on Mar 2, 2011

@author: raul
'''

import os

def get_data_path():
    try:
        from win32com.shell import shellcon, shell            
        homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
    except ImportError:
        #quick semi-nasty fallback for non-windows/win32com case
        homedir = os.path.expanduser("~")
    return os.path.join(homedir,'pyling_data')

if __name__ == '__main__':
    print get_data_path()