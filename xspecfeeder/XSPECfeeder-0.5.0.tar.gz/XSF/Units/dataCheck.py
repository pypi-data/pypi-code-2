""" Routine to check input data sequence

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 05/08/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : dataCheck (t, tabtype)
            t is an ATpy table containing our data
            tabtype is the table type as accepted by XSPECfeeder
            
            it returns 0 if everything is fine, else an error code

History : (05/08/2011) First named version.
"""


dataCheckrsp = {0 : '', -1 : "Emin must always be lower than Emax.", 
                    -2 : "One only filter per file is allowed.", -3 : "Bins must be consecutive (no gaps)."}


def dataCheck (t, tabtype):
        # No check at present for spectra
        if tabtype == 'OPT':
            return dataCheckrsp[0]
        elif tabtype == 'VHE':
            # sort table
            t.sort('col1')
            # check correctness
            uplastbin = t.col1[0]
            for i in range(len(t)):
                if t.col1[i] >= t.col2[i]:
                    return dataCheckrsp[-1]
                elif t.col1[i] > uplastbin:
                    return dataCheckrsp[-3]
                uplastbin = t.col2[i]
        elif tabtype == 'MAG':
            if t.shape[0] > 1:
                return dataCheckrsp[-2]        
        #
        return dataCheckrsp[0]