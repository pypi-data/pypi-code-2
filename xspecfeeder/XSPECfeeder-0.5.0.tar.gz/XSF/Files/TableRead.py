""" Routine to read data to be transformed

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 05/08/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : TableRead (tablename, tabtype='ASCII')
            tablename is the file name of the input table
            tabtype can be 'ASCII' or 'FITS'
            
            It returns the table data or None in case of failure


History : (05/08/2011) First named version.
"""


import atpy


def TableRead(tablename,tabtype='ASCII'):
    try:
        t = atpy.Table(tablename,type=tabtype.lower())
    except:
        t = None
    #
    return t    
        