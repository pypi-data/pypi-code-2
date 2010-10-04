from Acquisition import aq_inner
from zope.interface import implements
from zope.interface import alsoProvides, providedBy
from zope.interface import noLongerProvides

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView

from collective.salesforce.rsvp import interfaces
from collective.salesforce.rsvp import RSVPMessageFactory as _
from collective.salesforce.rsvp.config import OBJ_FIELD_SELECT_LISTS, RSVP_SCHEMATA, \
    LIMIT_CAPACITY_HIDABLE

class RSVPConfigurationView(BrowserView):
    """See ..interfaces.IRSVPConfigurationView"""
    implements(interfaces.IRSVPConfigurationView)
    iprovides = (interfaces.ISalesforceRSVPable,)
    
    def isRSVPEnabled(self):
        """See ..interfaces.IRSVPConfigurationView"""
        return interfaces.ISalesforceRSVPable.providedBy(self.context)
    
    def enableRSVPs(self):
        """See ..interfaces.IRSVPConfigurationView"""
        for iface in self.iprovides:
            if not iface.providedBy(self.context):
                alsoProvides(self.context, iface)
        
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(
            _(u'message_rsvp_enabled', default=u"Your item is ready for RSVP configuration via the '%s' section under the edit tab." % RSVP_SCHEMATA))
        if hasattr(self.request, 'RESPONSE'):
            self.request.RESPONSE.redirect(self.context.absolute_url())

    def disableRSVPs(self):
        """See ..interfaces.IRSVPConfigurationView"""
        rsvpable = aq_inner(self.context)
        if interfaces.ISalesforceRSVPable in providedBy(rsvpable):
            noLongerProvides(rsvpable, interfaces.ISalesforceRSVPable)
        
        if hasattr(self.request, 'RESPONSE'):
            plone_utils = getToolByName(self.context, 'plone_utils')
            plone_utils.addPortalMessage(_(u'message_rsvp_disabled', default=u"Disabled RSVP capabilities"))
            self.request.RESPONSE.redirect(self.context.absolute_url())
    

class DynamicSFObjectFields(PloneKSSView):
    """See ..interfaces.IDynamicSFObjectFields
    """
    implements(interfaces.IDynamicSFObjectFields)
    
    @kssaction
    def hide_custom_form_selector_if_inactive(self):
        """See ..interfaces.IDynamicSFObjectFields"""
        ksscore = self.getCommandSet('core')
        current_val = self.context.getField('enableCustomRegistration').get(self.context)
        if current_val == u'custom':
            return ''
        ksscore.addClass('#archetypes-fieldname-customRegistration', 'hiddenStructure')
    
    @kssaction
    def hide_capacity_selectors_if_inactive(self):
        """See ..interfaces.IDynamicSFObjectFields"""
        ksscore = self.getCommandSet('core')
        current_val = self.context.getField('limitRegistrationCapacity').get(self.context)
        if current_val == u'yes':
            return ''
        
        for widget_name in LIMIT_CAPACITY_HIDABLE:
            ksscore.addClass('#archetypes-fieldname-%s' % widget_name, 'hiddenStructure')
    
    @kssaction
    def toggle_capacity_fields_visibility(self, formvar):
        """See ..interfaces.IDynamicSFObjectFields"""
        ksscore = self.getCommandSet('core')
        
        if formvar == 'yes':
            core_act = getattr(ksscore, 'removeClass')
        else:
            core_act = getattr(ksscore, 'addClass')
        
        for widget_name in LIMIT_CAPACITY_HIDABLE:
            core_act('#archetypes-fieldname-%s' % widget_name, 'hiddenStructure')
    
    @kssaction
    def toggle_available_field_options(self, sfobject):
        """See ..interfaces.IDynamicSFObjectFields"""
        ksscore = self.getCommandSet('core')
        eligible_fields = self._listFieldsForSFObjectType(sfobject)
        eligible_fields.insert(0, ('','')) # add blank to the front of the list to decrease calls to SF.com
        
        # push out the various options as a select list
        for widget_name in OBJ_FIELD_SELECT_LISTS:
            widget_id_attr = '#%s' % widget_name
            select_html = self._buildSelectElement(eligible_fields, widget_name)
            ksscore.replaceHTML(widget_id_attr, select_html)
    
    def _listFieldsForSFObjectType(self, sfobject):
        """Returns a list of fields for a given Salesforce object"""
        sbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
        obj_schema = sbc.describeSObjects(sfobject)[0]
        return [(k, '%s (%s)' % (v.label, v.name)) for k, v in obj_schema.fields.items()]
    
    def _buildSelectElement(self, eligible_fields, widget_name):
        current_value = self.context.getField(widget_name).get(self.context)
        option_elements = self._buildOptionElements(current_value, eligible_fields)
        select_element = '''<select name="%s" id="%s">%s</select>''' % \
                    (widget_name, widget_name, option_elements)
        return select_element   
        
    def _buildOptionElements(self, current_value, eligible_fields):
        option_list = []
        for name, label in eligible_fields:
            selected_marker = self._markIfSelected(current_value, name)
            option_list.append("""<option value="%s" %s>%s</option>""" % (name, selected_marker, label))
        return "\n\t".join(option_list)
        
    def _markIfSelected(self, current_value, option_value):
        if current_value == option_value:
            return 'selected="selected"'
        return ''
