""" Init file for XSPECfeeder

Version : 1.0.0
Author  : Jure Japelj, Stefano Covino
Date    : 05/08/2011
E-mail  : jure.japelj@fmf.uni-lj.si, stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (05/08/2011) First named version.
"""



# import
__all__ = ['Files', 'System', 'Units']


# Version
__version__ = '0.5.0'


# External packages
FLX2XSP = 'flx2xsp'


# Input flux units
XSFIFU = ('JY', 'ERGA', 'ERGH', 'TEV')
XSFIFUOPT = XSFIFU[0:3]
XSFIFUVHE = XSFIFU[3]


# Input data type
XSFIDT = ('OPT', 'VHE', 'MAG')

# Input units
XSFIU = ('ANG', 'NM', 'HZ', 'GEV', 'TEV')
XSFIUOPT = XSFIU[0:3]
XSFIUVHE = XSFIU[3:]


# Tab type
XSFTT = ('ASCII', 'FITS')


# XSPEC input default filename
xscfname = 'xspecinput.txt'

