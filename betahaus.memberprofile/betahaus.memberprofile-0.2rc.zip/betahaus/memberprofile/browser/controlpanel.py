from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_inner
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.app.form.validators import null_validator
from plone.protect import CheckAuthenticator
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapts, getMultiAdapter
from zope.event import notify
from zope.formlib import form
from zope.interface import implements


from betahaus.memberprofile.browser.interfaces import IMemberProfileConfigSchema
from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter
from betahaus.memberprofile import MemberProfileMessageFactory as _
from Products.CMFPlone import PloneMessageFactory as pmf
from zope.formlib.form import FormFields


class MemberProfileControlPanel(ControlPanelForm):
    implements(IMemberProfileConfigSchema)
    form_fields = FormFields(IMemberProfileConfigSchema)

    label = _(u"Member profile setup")
    description = _(u'control_panel_description', default = u"Site wide settings for the Member profiles.")
    form_name = _(u"Member profile setup")

    def available(self):
        root = aq_inner(self.context).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)

    @form.action(pmf(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = pmf("Changes saved.")
            notify(ConfigurationChangedEvent(self, data))
        else:
            self.status = pmf(u"No changes made.")

    @form.action(pmf(u'label_cancel', default=u'Cancel'), validator=null_validator, name=u'cancel')
    def handle_cancel_action(self, action, data):
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''

    @form.action(_(u'quick_reindex_label', default = u'Quick reindex'), name=u'quick_reindex')
    def handle_quick_reindex_action(self, action, data):
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(u'text_not_allowed_manage_server',
                            default=u'You are not allowed to manage the Zope server.')
            return
        
        #Quick-reindex member profiles
        catalog = getToolByName(self.context, 'portal_catalog')
        pm = getToolByName(self.context, 'portal_membership')
        brains = catalog(portal_type=pm.memberarea_type)
        for brain in brains:
            obj = brain.getObject()
            obj.reindexObject()
        
        self.status = _(u'quick_reindex_responce', 
                        default = u'Performed quick reindex of Member Profiles.')

class MemberProfileControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMemberProfileConfigSchema)

    def __init__(self, context):
        self.portal = context
        self.settings = IMemberProfileSettingsAdapter(context)
        self.portal_registration = self.portal.portal_registration
        
    def get_title_as(self):
        return self.settings.get('title_as')
    
    def set_title_as(self, value):
        self.settings.set('title_as', value)
    
    title_as = property(get_title_as, set_title_as)

    def get_id_pattern(self):
        return self.portal_registration.getIDPattern()
    
    def set_id_pattern(self, value):
        #Registration tool doesn't like None-type as value
        if value is None:
            value = ''
        self.portal_registration.manage_editIDPattern(value)

    id_pattern = property(get_id_pattern, set_id_pattern)

#May be readded later
#    def get_enforce_complete_profile(self):
#        return self.settings.get('enforce_complete_profile')
#    
#    def set_enforce_complete_profile(self, value):
#        self.settings.set('enforce_complete_profile', value)
#
#    enforce_complete_profile = property(get_enforce_complete_profile, set_enforce_complete_profile)
