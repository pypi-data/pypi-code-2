""" Routine to convert flux units in TeV/cm2s to ph/cm2s as required by the XSPEC (KeV and ph/cm2s)

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 28/07/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : FLHE2XSPEC (xmin, xmax, phfl, ephfl)
            xmin and xmax are energies in GeV
            phfl, ephfl are the corresponding fluxes and errors in TeV/cm2s

            It returns minimum and maximum energies and fluxes and errors for each bin


History : (28/07/2011) First named version.
"""

def FLHE2XSPEC (xmin,xmax,phfl,ephfl):
    emint = []
    emaxt = []
    fluxt = []
    efluxt = []
    for i in range(len(xmin)):
        en_mean = (xmin[i] + xmax[i])*1e-3/2.0
        emin = xmin[i]*1e6
        emax = xmax[i]*1e6
        flux = phfl[i]/en_mean
        eflux = ephfl[i]/en_mean
        #
        emint.append(emin)
        emaxt.append(emax)
        fluxt.append(flux)
        efluxt.append(eflux)
    #
    return emint, emaxt, fluxt, efluxt
