""" Routine to convert frequency (Hz) to Angstrom 

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 03/08/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : HZ2ANGC (idata)
            idata are frequensies in Hz
            
            It returns wavelengths in Ang


History : (03/08/2011) First named version.
"""

c = 3e8 # m/s


def HZ2ANG (idata):
    return 1e10*c/idata
    
