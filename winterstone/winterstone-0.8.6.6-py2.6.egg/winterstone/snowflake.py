import os
import sys
import re


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


def replaceInFile(file,str,repl):
    content=getFileContent(file)
    content=re.sub(str,repl,content)
    file = open(file, 'w')
    file.write(content)
    file.close()
