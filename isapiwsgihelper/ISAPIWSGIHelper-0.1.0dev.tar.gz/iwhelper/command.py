import argparse
import os
from os import path
import shutil

from isapi.install import CheckLoaderModule

def main():
    parser = argparse.ArgumentParser(description='Create isapi-wsgi helper files')
    parser.add_argument('targetpath', nargs='?', help='location to create isapi-wsgi directory (default: cwd)', default='')

    args = parser.parse_args()
    basepath = args.targetpath or os.getcwd()
    tplpath = path.join(path.dirname(__file__), 'templates')

    iwpath = path.join(path.abspath(basepath), 'isapi-wsgi')
    loaderpy_path = path.join(iwpath, '_loader.py')
    loaderdll_path = path.join(iwpath, '__loader.dll')
    appinit_path = path.join(iwpath, 'appinit.py')
    iwhlog_path = path.join(iwpath, 'isapi-wsgi-helper.log')

    print 'target dir: %s' % iwpath
    # make isapi-wsgi directory if needed
    if not path.isdir(iwpath):
        os.mkdir(iwpath)

    # copy the DLL from pywin install directory to iwpath
    CheckLoaderModule(loaderdll_path)

    # copy _loader.py & appinit.py
    loadertpl_path = path.join(tplpath, '_loader.py.tpl')
    appinittpl_path = path.join(tplpath, 'appinit.py.tpl')
    shutil.copy(loadertpl_path, loaderpy_path)
    shutil.copy(appinittpl_path, appinit_path)
    # touch the log file
    open(iwhlog_path, 'a').close()

    print 'DON\'T FORGET to make the isapi-wsgi-helper.log file writeable by the web user.'
