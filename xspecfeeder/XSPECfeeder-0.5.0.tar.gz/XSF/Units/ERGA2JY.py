""" Routine to convert flux density units from erg/cm2sA to Jy

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 28/07/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : ERGA2JY (xdata, ydata, eydata)
            xdata are wavelengths in Angstrom
            ydata, eydata are the corresponding flux densities and errors in the input units
            
            It returns flux densities and errors in Jy


History : (28/07/2011) First named version.
"""



def ERGA2JY (xdata,ydata,eydata):
    return ydata*3.34e4*xdata**2, eydata*3.34e4*xdata**2
    
