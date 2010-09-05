from Products.Five.browser import BrowserView

from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from plone.app.registry.browser import controlpanel

from collective.xdv.interfaces import ITransformSettings, _
from collective.xdv.utils import getHost

try:
    # only in z3c.form 2.0
    from z3c.form.browser.textlines import TextLinesFieldWidget
except ImportError:
    from plone.z3cform.textlines import TextLinesFieldWidget

class TransformSettingsEditForm(controlpanel.RegistryEditForm):
    
    schema = ITransformSettings
    label = _(u"XDV theme settings") 
    description = _(u"Use the settings below to configure an XDV-based theme for this site")
    
    def updateFields(self):
        super(TransformSettingsEditForm, self).updateFields()
        self.fields['domains'].widgetFactory = TextLinesFieldWidget
        self.fields['notheme'].widgetFactory = TextLinesFieldWidget
        self.fields['alternate_themes'].widgetFactory = TextLinesFieldWidget
        
    
    def updateWidgets(self):
        super(TransformSettingsEditForm, self).updateWidgets()
        self.widgets['domains'].rows = 4
        self.widgets['domains'].style = u'width: 30%;'
        self.widgets['notheme'].rows = 4
        self.widgets['notheme'].style = u'width: 30%;'
        self.widgets['theme'].size = 60
        self.widgets['rules'].size = 60
        self.widgets['alternate_themes'].rows = 4
        self.widgets['alternate_themes'].style = u'width: 40%;'
        self.widgets['extraurl'].size = 60        
        self.widgets['absolute_prefix'].size = 60
    
class TransformSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TransformSettingsEditForm

class Utility(BrowserView):
    """Utility view to determine if the site is currently styled with xdv
    """
    
    def enabled(self):
        """Determine if the utility is enabled and we are in an enabled domain
        """
       
        # This assumes the X-XDV header has been set, either through
        # a front end proxy, or the setHeader() event handler that fires after
        # traversal
        
        return 'HTTP_X_XDV' in self.request.environ
    
    def domain_enabled(self):
        """Determine if the current request is in an xdv domain. Will return
        True even if the actual transform is disabled.
        """
        
        registry = queryUtility(IRegistry)
        if registry is None:
            return False
        
        settings = None
        try:
            settings = registry.forInterface(ITransformSettings)
        except KeyError:
            return False
        
        domains = settings.domains
        if not domains:
            return False
        
        host = getHost(self.request)
        for domain in domains:
            if domain.lower() == host:
                return True
        
        return False