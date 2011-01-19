#    Copyright (C) 2003-2006  Corporation of Balclutha and contributors.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

#
# still not very certain about price policies - whether they
# should be ZClass's (but then constrained to ControlPanel/Products)
# or where they should reside ie vertically within Accounts or
# horizontally within Inventory - or something else altogether!!
#
import Globals, string
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view, change_configuration
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
from ZClasses.Property import ZCommonSheet
from ZClasses.ZClass import PersistentClass, PersistentClassDict, ZClass

manage_addPaymentPolicyForm = PageTemplateFile('zpt/add_paymentpolicy', globals())
def manage_addPaymentPolicy(self, id, title='', description='', REQUEST=None):
    """ """
    self._setObject(id, PaymentPolicy(id, title, description))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' % (REQUEST['URL3'], id))
    return self._getOb(id)
                    
class PaymentPolicy(ZCommonSheet, SimpleItem):
    """
    A mechanism to define a policy from which to make payments to/from an account
    """
    meta_type = 'PaymentPolicy'
    icon = ZCommonSheet.icon

    __ac_permissions__ = ZCommonSheet.__ac_permissions__ + (
        (view_management_screens, ('v_self',
                                   'permissionMappingPossibleValues',)),
        (change_configuration, ('manage_edit',)),
        (view, ('render_form',)),
    ) + SimpleItem.__ac_permissions__

    #
    # support for our extensions stuff ...
    #
    _zclass_ = type(PersistentClass)('PaymentPolicy',
                                     (Globals.Persistent,),
                                     PersistentClassDict( 'PaymentPolicy' ))

    manage_options = (
        { 'label':'Attributes', 'action':'manage_main',
                        'help':('BastionBanking', 'paymentpolicy_attrs.stx') },
        { 'label':'Service', 'action': 'manage_service'},
    ) + SimpleItem.manage_options

    manage_main = ZCommonSheet.manage
    manage_main._setName('manage_main')
    manage_service = PageTemplateFile('zpt/paymentservice', globals())
    
    def manage_edit(self, service, REQUEST=None):
        """ """
        self.service = service
        if REQUEST:
            REQUEST.set('mangement_view', 'Service')
            REQUEST.set('manage_tabs_message', 'Updated')
            return self.manage_service(self, REQUEST)

    
    def __init__(self, id, title, description):
        ZCommonSheet.__init__(self, id, title)
        self._properties = ()
        self.description = description
        
    def v_self(self):
        return self

    def permissionMappingPossibleValues(self): return []
    
    def render_form(self, item):
        #
        # form generation ...
        #
        r = []
        for p in item.propertyMap():
            r.append('  <tr><td valign="top" class="form-label">%s</td>' % p['id'])
            r.append('      <td valign="top" class="form-element">%s</td>' %
                     self._edit_widget_for_type(p['type'], p['id'], p, item))
            r.append('  </tr>')
        if item.propertyMap():
            r.append('  <tr><td colspan=2><input type="submit" value=" Edit "></td></tr>')
        return string.join(r)

    
    def _edit_widget_for_type(self, t, id, p, item):
        if t in ('int', 'long', 'float'):
            value = item.getProperty(id)
            return ('''
            <input name="%s:%s" size="8" value="%s">'''
                    % (id, t, value)
                    )
        if t in ('date', 'string'):
            value = item.getProperty(id)
            return ('''
            <input name="%s:%s" size="25" value="%s">'''
                    % (id, t, value)
                    )
        if t=='boolean':
            if item.getProperty(id):
                value = ' checked'
            else:
                value = ''
            return ('''
            <input type="checkbox" name="%s:boolean" size="35"%s/>'''
                    % (id, value)
                    )
        if t=='tokens':
            value =  item.getProperty(id).join(' ')
            return ('''
            <input type="text" name="%s:tokens" size="35" value="%s"'''
                    % (id, value)
                    )
        if t=='text':
            value =  item.getProperty(id).join(' ')
            return ('''
            <textarea name="%s:text" rows="6" cols="35">%s</textarea>'''
                    % (id, value)
                    )

        if t=='lines':
            value =  itementry.getProperty(id).join('\n')
            return ('''
            <textarea name="%s:lines" rows="6" cols="35">%s</textarea>'''
                    % (id, value)
                    )

        if t=='selection':
            function = getattr(self, p['select_variable'])
            return (r'''
              <select name="%s">
                %s 
              </select>''' % ( id, map(lambda x: '<option>%s</option>' % x, 
                                       function.__of__(item)() ) )
                    )

        if t=='multiple selection':
            function = getattr(self, p['select_variable'])
            return (r'''
              <select name="%s:list" size="6" multiple>
                %s 
             </select>''' % ( id, reduce(operator.add, map(lambda x: '<option>%s</option>' % x, 
                                      function.__of__(item)() ) ) )
                    )

        return ''

Globals.InitializeClass(PaymentPolicy)


class PaymentPolicySupport(PropertyManager):
    """
    This is used by a class implementing payment policy support.  Note that this
    class will screw with the _properties of it's parent!!

    Payment Policies ARE optional so we can't make any assumptions about presence
    of attributes - thus attribute creation and deletion is left to the functions
    themselves.  If a function is called, implicitly this stuff should be done -
    if you don't want it then don't call it!
    """
    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (view_management_screens, ('manage_paymentPolicyForm', 'manage_paymentPolicy',
                                   'manage_paymentServiceForm',
                                   'paymentPolicies', 'getPaymentPolicy')),
        )
    
    manage_options = (
        {'label':'Payments', 'action':'manage_paymentPolicyForm'},
        )
    manage_paymentPolicyForm = PageTemplateFile('zpt/paymentpolicy', globals())
    manage_paymentServiceForm = PageTemplateFile('zpt/paymentservice', globals())
    
    def manage_paymentPolicy(self, policy, REQUEST=None):
        """
        sync the _properties with underlying payment policy
        """
        assert policy in self.paymentPolicies(), "Unknown Policy: %s" % policy
        if not hasattr(aq_base(self), 'paymentpolicy'):
            self.paymentpolicy = policy
            #
            # copy the properties of the policy - we really need to define this stuff
            # as a property set ...
            #
            self._properties = self.getPaymentPolicy()._properties
            map( lambda x,y=self,z=self.getPaymentPolicy(): setattr(y, x, z.getProperty(x)),
                 self.propertyIds())
        elif self.paymentpolicy != policy:
            oldpolicy = self.getPaymentPolicy()
            self.paymentpolicy = policy
            self.manage_delProperties(oldpolicy.propertyIds())
            self._properties = self.getPaymentPolicy()._properties
            map( lambda x,y=self,z=self.getPaymentPolicy(): setattr(y, x, z.getProperty(x)),
                 self.propertyIds())

        if REQUEST:
            del REQUEST.form['policy']
            # apply defaults from policy
            if REQUEST.form.keys():
                try:
                    # this could go from a policy with data to one without - in this
                    # case, there will be old info from old policy in the request packet
                    self.manage_editProperties(REQUEST)
                except:
                    pass
            REQUEST.set('management_view', 'Payments')
            return self.manage_paymentPolicyForm(self, REQUEST)

    def paymentPolicies(self):
        # valid policies
        return self.BastionBankService.objectIds('PaymentPolicy')

    def getPaymentPolicy(self):
        # the 'meta-policy' object ...
        try:
            if not hasattr(aq_base(self), 'paymentpolicy'):
                return None
            return self.BastionBankService._getOb(self.paymentpolicy)
        except:
            return None

Globals.InitializeClass(PaymentPolicySupport)
