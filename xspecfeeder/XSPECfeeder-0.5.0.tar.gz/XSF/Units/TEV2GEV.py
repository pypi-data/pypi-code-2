""" Routine to convert energies units from TeV to GeV 

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 28/07/2011
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : TEV2GEV (imindata, imaxdata)
            imindata and imaxdata are energies in TeV
            
            It returns energies in GeV


History : (28/07/2011) First named version.
"""



def TEV2GEV (imindata, imaxdata):
    return imindata*1e3, imaxdata*1e3
    
