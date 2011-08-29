from plone.app.registry.browser import controlpanel
from collective.cicero import ICiceroSettings
from collective.cicero import get_auth_token
from z3c.form.interfaces import ActionExecutionError
from zope.interface import Invalid


class CiceroSettingsControlPanel(controlpanel.RegistryEditForm):

    schema = ICiceroSettings
    label = u"Cicero API settings"

    def applyChanges(self, data):
        # validate credentials
        errmsg = get_auth_token(data['userName'], data['password'])
        if errmsg.startswith('ERROR'):
            raise ActionExecutionError(Invalid(errmsg))
        
        super(CiceroSettingsControlPanel, self).applyChanges()