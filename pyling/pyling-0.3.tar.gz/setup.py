#!/usr/bin/env python
'''
Created on Mar 2, 2011

@author: raul
'''

from distutils.core import setup
import os
import stat

def get_data_path():
    try:
        from win32com.shell import shellcon, shell            
        homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
    except ImportError: # quick semi-nasty fallback for non-windows/win32com case
        homedir = os.path.expanduser("~")
    return os.path.join(homedir,'pyling_data')

setup(name='pyling',
      version='0.3',
      description='Python linguistic libraries for software developers.',
      author='Raul Garreta',
      author_email='raul@tryolabs.com',
      url='http://www.pyling.org',
      packages=['pyling'],
      package_dir={'pyling': 'src/pyling'},
      data_files=[(get_data_path(), ['src/pyling/data/chunker_en.pickle'])]
     )

#chmod to read, write and execute for others
os.chmod(get_data_path(), stat.S_IWOTH | stat.S_IROTH | stat.S_IXOTH)
for file in os.listdir(get_data_path()):
    os.chmod(os.path.join(get_data_path(),file), stat.S_IWOTH | stat.S_IROTH | stat.S_IXOTH)

