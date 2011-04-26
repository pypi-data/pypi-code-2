import os
import sys


CWD = sys.path[0] + '/'

def loadIcons(icondir, ext='.png'):
    '''
        return dict: {'iconname':'iconpath'}
    '''
    icons = {}
    dirList = os.listdir(icondir)
    for fname in dirList:
        if fname.endswith(ext):
            icons[fname[:-4]] = str(icondir + fname)
    return icons


def getFileContent(file):
    '''
        return file content
    '''
    file = open(file, 'r')
    content = file.read()
    file.close()
    return content.decode('utf8')
