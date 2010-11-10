"""

    Convergence options edit forms.
    
    This will override gomobile.mobile Mobile options form
    by overriding document_actions "mobile_options" action
    when quick installer is run (actions.xml)

    http://mfabrik.com
    
"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext"

import os

from Acquisition import aq_inner
import zope.interface
from zope import schema
from zope.component import getUtility, queryUtility
from zope.component import getMultiAdapter, queryMultiAdapter
from Products.Five.browser import BrowserView

import z3c.form.form
from z3c.form import subform
from z3c.form import field
from z3c.form import group

from gomobile.convergence.interfaces import IOverrideForm, IOverrider
from plone.z3cform.layout import FormWrapper, wrap_form

try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPER_FORM = True
except ImportError:
    HAS_WRAPPER_FORM = False # Old plone.z3cform version
    
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from gomobile.mobile.behaviors import IMobileBehavior 
from gomobile.mobile.browser.forms import MobileForm

from gomobile.convergence.behaviors import contentMediasVocabury, IMultiChannelBehavior, multichannel_behavior_factory
from gomobile.convergence.interfaces import ContentMediaOption, IConvergenceMediaFilter, IConvergenceBrowserLayer
from gomobile.convergence.filter import media_options_vocabulary
from gomobile.convergence.interfaces import IOverrideForm

from gomobile.convergence.overrider.base import IOverrideStorage

from gomobile.convergence import GMConvergenceMF as _


class PublishingForm(z3c.form.form.EditForm):
    """ Folder/page specific convergence options """

    fields = field.Fields(IMultiChannelBehavior)

    prefix = "publishing"
    label = _(u"Media options")

    def update(self):
        return z3c.form.form.EditForm.update(self)
    
    def getContent(self):
        """
        """
        behavior = IMultiChannelBehavior(self.context)
        return behavior        

    def applyChanges(self, data):
        # Call super
        val = z3c.form.form.EditForm.applyChanges(self, data)

        # Write behavior to database
        self.getContent().save()
        
        return val


class OverrideForm(z3c.form.form.EditForm):
    """ Fielde specific convergence options """


    label = _(u"Field overrides")
    prefix = "overrides"

    def __init__(self, context, request, content_object):
        self.context = context
        self.request = request
        self.content_object = content_object

    def update(self):
        """ Dynamically load fields.

        Form.update() is correct place to fiddle
        with fields information, before proceeding
        to parent update() and widget creation.
        """

        self.fields = self.getOverriderFields()
        z3c.form.form.EditForm.update(self)

    def getOverriderFields(self):
        """ Recycle fields dynamically from another form instance """

        # Get the mobile overrider form for the context
        form = getMultiAdapter((self.content_object, self.request), IOverrideForm)

        # Read its Fields instance
        fields = form.fields
        # Fields could be mofified in this point
        # (need to duplicate it first though)

        return fields



class MasterFormView(BrowserView):
    """ Custom view managing two separate forms on the same page """

    label = _(u"Multichannel management")

    # Page template we are using
    index = FiveViewPageTemplateFile("convergenceformview.pt")

    def media_status(self):
        """ Get human-readable text on which medias the context is available  """
        filter = getUtility(IConvergenceMediaFilter)
        context = self.context.aq_inner
        media = filter.solveContentMedia(context)

        # Translate vocabulary
        for id, text in media_options_vocabulary:
            if id == media:
                return text

    def render_override_form(self):
        """ Update and render one of forms on this view.

        Called by template.
        """
        return self.override_form_instance()

    def render_publishing_form(self):
        """ Update and render one of forms on this view.

        Called by template."""
        return self.publishing_form_instance()
    
    def render_mobile_form(self):
        return self.mobile_form_instance()

    def init(self):
        """ Constructor embedded sub forms """


        # Construct few embedded forms
        self.mobile_form_instance = MobileForm(self.context, self.request)
        
        self.publishing_form_instance = PublishingForm(self.context, self.request)        
        
        self.override_form_instance = getMultiAdapter((self.context, self.request), IOverrideForm)
        
        if HAS_WRAPPER_FORM:
            zope.interface.alsoProvides(self.publishing_form_instance, IWrappedForm)        
            zope.interface.alsoProvides(self.mobile_form_instance, IWrappedForm)
            zope.interface.alsoProvides(self.override_form_instance, IWrappedForm)
    
    
    def __call__(self):


        self.init()
        
        # Make z3c.form fields and widgetsre
        import z3c.form.interfaces
        from plone.z3cform import z2
        z2.switch_on(self, request_layer=z3c.form.interfaces.IFormLayer)

        

        # Render template
        return self.index()
