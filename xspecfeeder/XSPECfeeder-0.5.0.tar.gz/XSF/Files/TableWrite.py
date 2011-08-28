""" Routine to write data to be transformed

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 28/07/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : TableWrite (tablename, emin,emax,phfl,ephfl)
            tablename is the output file name 
            emin and emax are vectors containing the minimum and maximum energy if each bin
            phfl and ephfl are vectors containing the photon flux and errors for each bin
            
            It returns the tabl name or None in case of failure


History : (28/07/2011) First named version.
"""


import os.path, atpy, asciitable


def TableWrite(tablename,emin,emax,phfl,ephfl):
    #
    t = atpy.Table()
    #
    t.add_column('E_min',emin)
    t.add_column('E_max',emax)
    t.add_column('Ph_fl',phfl)
    t.add_column('ePh_fl',ephfl)
    #
    if os.path.exists(tablename):
        try:
            os.remove(tablename)
        except IOError, OSError:
            return None
    #
    t.write(tablename,type='ASCII',Writer=asciitable.NoHeader)
    #
    return tablename