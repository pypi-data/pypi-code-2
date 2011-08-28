""" Routine to convert flux density units from Jy to ph/cm2s as required by the XSPEC (KeV and ph/cm2s)

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 28/07/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : FL2XSPEC (xdata, ydata, eydata)
            xdata are wavelengths in Angstrom
            ydata, eydata are the corresponding flux densities and errors in the input units
            
            It returns minimum and maximum energies and fluxes and errors for each bin


History : (28/07/2011) First named version.
"""


def FL2XSPEC (xdata,ydata,eydata):
    emint = []
    emaxt = []
    fluxt = []
    efluxt = []
    for i in range(len(xdata)-1):
        emax = 12.43/xdata[i]
        emin = 12.43/xdata[i+1]
        d_en = emax-emin
        en_mean = (emax + emin)/2.0
        flux = ydata[i]*d_en*1e4/(6.63*en_mean)
        eflux = flux*(eydata[i]/ydata[i])
        #
        emint.append(emin)
        emaxt.append(emax)
        fluxt.append(flux)
        efluxt.append(eflux)
    #
    emint.reverse()
    emaxt.reverse()
    fluxt.reverse()
    efluxt.reverse()
    #
    return emint, emaxt, fluxt, efluxt