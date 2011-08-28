""" Routine to convert flux density units from erg/cm2sHz to Jy

Version : 1.0.0
Author  : jure.japelj@fmf.uni-lj.si, Stefano Covino
Date    : 28/07/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : ERGH2JY (xdata, ydata, eydata)
            xdata are wavelengths in Angstrom
            ydata, eydata are the corresponding flux densities and errors in the input units
            
            It returns flux densities and errors in Jy


History : (28/07/2011) First named version.
"""



def ERGH2JY (ydata,eydata):
    return ydata*10**23, eydata*10**23
    
