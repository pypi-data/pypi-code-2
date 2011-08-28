""" Routine to execute a pipe

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 28/07/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : Pipe (file)
            file is the command to be executed.
            
            It returns the output of the command or None in case of failure


History : (28/07/2011) First named version.
"""


import os, os.path, sys


# SRP pipe
if sys.version_info[0] >= 2 and sys.version_info[1] >= 6:
    import subprocess
    
    def Pipe (file):
        f = subprocess.Popen(file,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
        ky = f.stdout.read()
        estatus = f.wait()
        del f
        if os.WEXITSTATUS (estatus):
            return None
        else:
            return ky
else:
    import popen2
    
    def Pipe (file):
        f = popen2.Popen4(file)
        ky = f.fromchild.read()
        estatus = f.wait()
        del f
        if os.WEXITSTATUS (estatus):
            return None
        else:
            return ky
