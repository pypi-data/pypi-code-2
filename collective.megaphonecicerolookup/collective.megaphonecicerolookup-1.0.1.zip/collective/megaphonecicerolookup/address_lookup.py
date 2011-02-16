import logging
from zope.component import getUtility
from zope.app.component.hooks import getSite
from zope.interface import implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.megaphone.interfaces import IRecipientSource, IRecipientSourceRegistration
from collective.megaphone.recipients import get_recipient_settings, recipient_label
from collective.cicero import call_cicero, get_settings
from collective.megaphonecicerolookup.interfaces import IRegistrySettings, ICiceroAddressLookup
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from plone.memoize import ram
from suds import WebFault

logger = logging.getLogger('collective.megaphonecicerolookup')

@ram.cache(lambda func, *args: args)
def _cached_lookup(*args):
    return call_cicero('ElectedOfficialQueryService', 'GetOfficialsByAddress', *args)


class AddressLookupRecipientSource(object):
    implements(IRecipientSource)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.settings = get_recipient_settings(context, 'cicero_address_lookup')
    
    def lookup(self):
        instance_settings = self.settings
        if not instance_settings:
            return []
        cicero_settings = get_settings()
        site_settings = getUtility(IRegistry).forInterface(IRegistrySettings)
        putils = getToolByName(self.context, 'plone_utils')
        
        street = self.request.form.get('street')
        city = self.request.form.get('city')
        state = self.request.form.get('state')
        zip = self.request.form.get('zip')
        country = self.request.form.get('country', cicero_settings.country)
        if not street or not city or not state or not zip:
            logger.warn('Skipping address --> official lookup; not all of the following were '
                        'provided in the form submission: street, city, state, zip')
            return []
        
        info = []
        for id, settings in instance_settings:
            
            allowed_states = settings.get('allowed_states')
            if allowed_states is None:
                allowed_states = site_settings.allowed_states
            if allowed_states is not None and state not in allowed_states:
                logger.warn("Address --> official lookup not enabled for this state (%s); skipping." % state)
                continue
            
            try:
                officials = _cached_lookup(street, city, state, zip, country, settings['districtType'], settings['includeAtLarge'])
            except IOError, e:
                if hasattr(e, 'reason'):
                    logger.warn('Failed to connect to Cicero: %s' % e.reason)
                elif hasattr(e, 'code'):
                    logger.warn('Unable to expected response from Cicero: %s' % e.code)
                continue
            except WebFault, e:
                logger.warn('Unable to look up officials via Cicero: %s' % str(e))
                continue
            
            if hasattr(officials, 'ElectedOfficialInfo'):
                for official in officials.ElectedOfficialInfo:
                    email = getattr(official, 'EMail1', getattr(official, 'EMail2', u''))
                    if not putils.validateSingleEmailAddress(email):
                        # might be a web URL or other non-email;
                        # returning a blank e-mail means letter will be generated but not delivered
                        logger.warn("Didn't find e-mail address (%s); skipping delivery." % email)
                        email = u''
                    info.append({
                        'honorific': getattr(official, 'Salutation', getattr(official, 'Title', u'')),
                        'first': official.FirstName,
                        'last': official.LastName,
                        'email': email,
                        'description': u'',
                        })
                    if info[-1]['honorific'] != getattr(official, 'Title', u''):
                        info[-1]['description'] = getattr(official, 'Title', u'')

        return info
    
    snippet = ViewPageTemplateFile('form_snippet.pt')
    def render_form(self):
        if self.settings:
            recipients = [s['label'] for _, s in self.settings]
            return self.snippet(recipients=recipients)
        return ''

    def async(self):
        # for AJAX use; perform lookup and return updated info on recipients
        recipients = [recipient_label(r) for r in self.lookup()]
        if not recipients:
            if self.settings:
                recipients = [s['label'] for _, s in self.settings]
            else:
                return ''
        return self.snippet(recipients=recipients, async=True)


class AddressLookupRecipientSourceRegistration(object):
    implements(IRecipientSourceRegistration)
    
    name = 'cicero_address_lookup'
    title = u'Cicero lookup: address to official'
    description = u'Looks up elected officials based on the address entered by the activist.'
    settings_schema = ICiceroAddressLookup
    
    @property
    def enabled(self):
        qi = getToolByName(getSite(), 'portal_quickinstaller')
        return qi.isProductInstalled('collective.megaphonecicerolookup')
    
    def get_label(self, settings):
        return settings['label']
