#!/usr/bin/env python
from os import getenv, listdir, readlink, chdir
from sys import exit, argv

def clean_trailing_slash(path):
    if path.endswith('/'):
        return path[:-1]
    else:
        return path
cts = clean_trailing_slash

quick_projects = getenv('QUICK_PROJECTS',getenv('HOME',''))
projects = listdir(quick_projects)
projects = dict([(q,cts(readlink('%s/%s'% (quick_projects,q)))) for q in projects])

pwd = getenv('PWD')
pwds = pwd.split('/')
pwds = [(pwds[i],('/'.join(pwds[:i+1]),'/'.join(pwds[i+1:]))) for i in range(len(pwds))]

for key,values in pwds:
    if key in projects and values[0] in [projects[key],'%s/%s'%(quick_projects,key)]:
        if len(argv) > 1 and argv[1].strip() == 'w':
            print '%s/%s' %(quick_projects,key)
        else:
            print '%s/%s/%s' %(quick_projects,key,values[1])
        break
else:
    print pwd
