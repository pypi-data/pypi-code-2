"""
$Id: install.py 2615 2009-05-22 14:42:00Z dholth $
"""
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

def uninstall( self ):
    out = StringIO()
    setup_tool = getToolByName(self, 'portal_setup')
    print >> out, "Removing Solgema.fullcalendar"
    setup_tool.runAllImportStepsFromProfile('profile-Solgema.fullcalendar:uninstall', purge_old=False)
    return out.getvalue()

