from zope.interface import implements, Interface
from zope import schema
from zope.app.pagetemplate import viewpagetemplatefile
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.site.hooks import getSite

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


# z3c.form support
from plone.z3cform import z2
from z3c.form import button, field, form, interfaces
from plone.app.z3cform.layout import wrap_form

from inqbus.bannerrotation import _

POSSIBLE_EFFECTS = ["fade", "blindX", "blindY", "blindZ", "cover", 
                    "curtainX", "curtainY", "fadeZoom", "growX", 
                    "growY", "none", "scrollUp", "scrollDown", 
                    "scrollLeft", "scrollRight", "scrollHorz", 
                    "scrollVert", "shuffle", "slideX", "slideY", 
                    "toss", "turnUp", "turnDown", "turnLeft", 
                    "turnRight", "uncover", "wipe", "zoom"
]

class IBannerrotationConfigSchema(Interface):
    """
    """
    
    effect = schema.Choice(
        description = _(
            u"descr_bannerrotation_effect",
            u"",
        ),
        required = True,
        values = POSSIBLE_EFFECTS,
        title = _(
            u"label_bannerrotation_effect",
            u"Effect",
        ),
    )
    
    timeout = schema.Int(
        description = _(
            u"descr_bannerrotation_timeout",
            u"Specify the time between the imagechanges in milliseconds",
        ),
        required = True,
        title = _(
            u"label_bannerrotation_timeout",
            u"Timeout",
        ),
    )
    
    speed = schema.Int(
        description = _(
            u"descr_bannerrotation_speed",
            u"Specify the animationspeed in milliseconds",
        ),
        required = True,
        title = _(
            u"label_bannerrotation_speed",
            u"Speed",
        ),
    )
    
    enabled = schema.Bool(
        description = _(
            u"descr_bannerrotation_enabled",
            u"Enable or disable the bannerrotation",
        ),
        required = False,
        title = _(
            u"label_bannerrotation_enabled",
            u"Enabled",
        ),
    )
    
    random = schema.Bool(
        description = _(
            u"descr_bannerrotation_random",
            u"Enable or disable randomization of the images",
        ),
        required = False,
        title = _(
            u"label_bannerrotation_random",
            u"Random",
        ),
    )
    
    
class BannerrotationConfigForm(form.Form):
    """
    """
    fields = field.Fields(IBannerrotationConfigSchema)
    
    ignoreContext = True
    
    method = 'get'
    template = viewpagetemplatefile.ViewPageTemplateFile('z3c_formmacros.pt')
    
    def updateWidgets(self):
        """ Get the Values from the property sheet and set them
        """
        super(BannerrotationConfigForm, self).updateWidgets()
        
        # get the values out of the propery sheet
        portal = getSite()
        ptool = portal.portal_properties
        effect = ptool.bannerrotation_properties.effect
        timeout = ptool.bannerrotation_properties.timeout
        speed = ptool.bannerrotation_properties.speed
        enabled = ptool.bannerrotation_properties.enabled
        random = ptool.bannerrotation_properties.random
        
        # set them to the fields
        self.widgets['enabled'].field.default = enabled
        self.widgets['random'].field.default = random
        super(BannerrotationConfigForm, self).updateWidgets()
        
        self.widgets['effect'].value = effect
        self.widgets['timeout'].value = timeout
        self.widgets['speed'].value = speed

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handle_send(self, action):
        """
        """

SearchFormView = wrap_form(BannerrotationConfigForm)

class IBannerrotationConfigView(Interface):
    """
    """

class BannerrotationConfigView(BrowserView):
    """
    """
    implements(IBannerrotationConfigView)
    
    template_file = ViewPageTemplateFile("bannerrotation_config_view.pt")

    def __init__(self, context, request):
        """
        """
        self.context = context
        self.request = request
        
    def __call__(self):
        """
        """
        self.set_properties()
        return self.index()

    def set_properties(self):
        """
        """
        if self.request.get('form.buttons.save'):
            portal = getSite()
            ptool = portal.portal_properties
            ptool.bannerrotation_properties.effect = self.request.get('form.widgets.effect')[0]
            ptool.bannerrotation_properties.timeout = self.request.get('form.widgets.timeout')
            ptool.bannerrotation_properties.speed = self.request.get('form.widgets.speed')
            if self.request.get('form.widgets.enabled')[0] == 'true':
                ptool.bannerrotation_properties.enabled = True
            else:
                ptool.bannerrotation_properties.enabled = False
            if self.request.get('form.widgets.random')[0] == 'true':
                ptool.bannerrotation_properties.random = True
            else:
                ptool.bannerrotation_properties.random = False
    
    def get_config_form(self):
        """
        """
        z2.switch_on(self)
        form = BannerrotationConfigForm(self.context, self.request)
        form.update()
        return form.render()