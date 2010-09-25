
# zope
from AccessControl.Permissions import manage_users as ManageUsers

# cmf
from Products.PluggableAuthService.PluggableAuthService import \
     registerMultiPlugin

from anz.cas.centralauthservice import AnzCentralAuthService, \
     manage_addAnzCentralAuthService, addAnzCentralAuthServiceForm

# register plugins with pas
try:
    registerMultiPlugin( AnzCentralAuthService.meta_type )
except RuntimeError:
    # make refresh users happy
    pass

def initialize( context ):
    context.registerClass( AnzCentralAuthService,
                           permission=ManageUsers,
                           constructors=( addAnzCentralAuthServiceForm,
                                          manage_addAnzCentralAuthService
                                          ),
                           icon='www/anz_cas.png',
                           visibility=None
                           )
