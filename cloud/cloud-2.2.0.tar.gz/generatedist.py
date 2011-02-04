#!/usr/bin/env python
'''
This file is used generate cloud module distribution.
Run it as generateDistribution
This must be run in its current directory!
'''

import os
import sys
import subprocess 
import re

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
            print 'usage: %s <ReleaseVersion>' % sys.argv[0]
            sys.exit(1)
    
    p = subprocess.Popen('svn info', shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = p.communicate(input=False)
    if stderr:
        raise Exception('svn info errored::\n\n' + stderr)
    
    revision = re.compile('Revision: (.*)')
    matches = revision.findall(stdout)
    
    
    if not matches:
        raise Exception('svn info failed to return Revision tag')
    
    revision = int(matches[0])
    print "Revision is %d" % revision 
      
    try:
        os.unlink('src')
    except:
        pass
    try:
        os.unlink('MANIFEST')
    except Exception, e:
        print 'except', e
    
    os.symlink('../client', 'src')
    
    versioninfo = file('src/versioninfo.py','w')
    versioninfo.write('# This file defines versioning information\n')
    versioninfo.write('release_version="%s"\n' % sys.argv[1])
    versioninfo.write('svn_version=%d\n' %revision)
    versioninfo.close()    
    
    p = subprocess.Popen('python2.6 setup.py bdist_egg', shell=True)
    p.communicate()

    p = subprocess.Popen('python2.6 setup.py sdist', shell=True)
    p.communicate()

    p = subprocess.Popen('python2.5 setup.py bdist_egg', shell=True)
    p.communicate()

    p = subprocess.Popen('python2.7 setup.py bdist_egg', shell=True)
    p.communicate()

    
    os.unlink('src')



    
    
    
    
    




