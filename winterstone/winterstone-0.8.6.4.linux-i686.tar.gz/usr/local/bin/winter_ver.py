#!/usr/bin/python
# -*- coding: utf-8 -*-
# Change project version

__author__ = 'Averrin'
__version__ = '0.2'

path='config/main.cfg'


import re
import optparse

def main():
    p=optparse.OptionParser(description="Change project version", prog='winter_ver.py', version='0.2', usage="%prog [command]")
    p.add_option('--custom-ver','-c',action='store',help='custom version', type="string", dest="newver",default='')
    p.add_option('--custom-postfix','-p',action='store',help='custom postfix', type="string", dest="postfix",default='')
    options, arguments = p.parse_args()
    f=open(path,'r')
    VERSION=f.read()
    f.close()

    ver = re.findall('\'(\d+)\.(\d+)\.(\d+) ([^ \']*)\'',VERSION)[0]
    regexp='\'\d+\.\d+\.\d+ ([^ \']*)\''
    try:
        pf = re.findall(regexp,VERSION)[0]
    except:
        pf=''
    oldver='.'.join(ver[0:3])+' '+pf
    if not options.newver:
        build=int(ver[2])+1
        newver='%s.%s.%d' % (ver[0],ver[1],build)
    else:
        newver=options.newver
    if options.postfix:
        newver+=' '+options.postfix
    else:
        newver+=' '+pf
    VERSION=re.sub(regexp,'\'%s\''%newver,VERSION)
    print 'Switch to', newver, 'from',oldver
    f=open(path,'w')
    f.write(VERSION)
    f.close()


if __name__ == '__main__':
    main()
