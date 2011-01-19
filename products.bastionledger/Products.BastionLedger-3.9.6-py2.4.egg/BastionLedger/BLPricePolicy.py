#
#    Copyright (C) 2002-2010  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#
# still not very certain about price policies - whether they
# should be ZClass's (but then constrained to ControlPanel/Products)
# or where they should reside ie vertically within Accounts or
# horizontally within Inventory - or something else altogether!!
#
import Globals
from AccessControl.Permissions import view_management_screens, view
from Acquisition import aq_base
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.PythonScript import PythonScript
from BLBase import *
from Permissions import OperateBastionLedgers

from zope.interface import Interface, implements

class IPricePolicyFolder(Interface): pass

manage_addBLPricePolicyForm = PageTemplateFile('zpt/add_pricepolicy', globals())
def manage_addBLPricePolicy(self, id, title='', description='', REQUEST=None):
    """ """
    self._setObject(id, BLPricePolicy(id, title, description))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_workspace' % (REQUEST['URL3'], id))
    return self._getOb(id)


#
# we haven't figured out how to skin/Plonify this yet - it's default view is the
# price calculating functor ...
#

class BLPricePolicy(PythonScript, BCommonSheet, SimpleItem):
    """
    A mechanism to define a pricing model to apply to a BLOrderItem to determine
    its value
    """
    meta_type = 'BLPricePolicy'
    __ac_permissions__ = (
        (view_management_screens, ( 'ZPythonScriptHTML_editAction', 'ZPythonScript_setTitle',
                                    'ZPythonScript_edit', 'ZPythonScriptHTML_editForm', 'manage_main',
                                    'read', 'ZScriptHTML_tryForm', 'PrincipiaSearchSource',
                                    'document_src', 'params', 'body','manage_proxyForm',
                                    'manage_access', 'manage_changePermissions', 'manage_edit')),
        (view, ('__call__',) )
        )

    manage_options = ({ 'label':'Details', 'action':'manage_main' },
                      { 'label':'Policy Attributes', 'action':'manage_common_sheet',
                        'help':('BastionLedger', 'pricepolicy_attrs.stx') },
                      PythonScript.manage_options[0],
                      PythonScript.manage_options[3],
                      PythonScript.manage_options[7])

    manage_main = PageTemplateFile('zpt/pricepolicy_details', globals())

    def manage_edit(self, title, description, REQUEST=None):
        self.title = title
        self.description = description
        if REQUEST:
            REQUEST.set('mangement_view', 'Details')
            REQUEST.set('manage_tabs_message', 'Details Updated')
            return self.manage_main(self, REQUEST)

    _params = 'orderitem,account'
    __setstate__ = PythonScript.__setstate__

    def __init__(self, id, title, description):
        PythonScript.__init__(self, id)
        BCommonSheet.__init__(self, id, title)
        self.description = description
        
    def __call__(self, orderitem, account):
        return PythonScript.__call__(self, orderitem, account)
    
    def ZPythonScript_editAction(self, REQUEST, title, params, body):
        """ """
        return PythonScript.ZPythonScript_editAction(self, REQUEST, title, self._params, body)

    def ZPythonScript_edit(self, params, body):
        PythonScript.ZPythonScript_edit(self, BLPricePolicy._params, body)

    def standard_price(self, orderitem):
        return orderitem.part().sellprice

    def price_deviation(self, orderitem):
        return abs( self(orderitem) - self.standard_price(orderitem) )
    
Globals.InitializeClass(BLPricePolicy)


class BLPricePolicySupport(PropertyManager):
    """
    This is used by a class implementing price policy support.  Note that this
    class will utilise the PropertyManager of the object to add any PricePolicy
    attributes.

    Price Policies ARE optional so we can't make any assumptions about presence
    of attributes - thus attribute creation and deletion is left to the functions
    themselves.  If a function is called, implicitly this stuff should be done -
    if you don't want it then don't call it!
    """
    __ac_permissions__ = (
        (view_management_screens, ('manage_policyForm', 'manage_policy',
                                   'pricePolicies', 'getPricePolicy')),
        )
    
    manage_options = ( {'label':'Price Policy', 'action':'managePolicyForm'}, )
    manage_policyForm = PageTemplateFile('zpt/pricepolicy', globals())
    
    def manage_policy(self, policy, REQUEST=None):
        """
        sync the _properties with underlying price policy
        """
        assert policy in self.pricePolicies(), "Unknown Policy: %s" % policy
        if not getattr(aq_base(self), 'pricepolicy', None):
            self.pricepolicy = policy
            #
            # copy the properties of the policy - we really need to define this stuff
            # as a property set ...
            #
            the_policy = self.getPricePolicy()
            for prop in the_policy.propertyValues():
                self._setProperty(prop['id'], the_policy.getProperty(prop['id']) , prop['type'])
        elif self.pricepolicy != policy:  
            oldpolicy = self.getPaymentPolicy()
            self.pricepolicy = policy
            self.manage_delProperties(oldpolicy.propertyIds())
            the_policy = self.getPricePolicy()
            for prop in the_policy.propertyValues():
                self._setProperty(prop['id'], the_policy.getProperty(prop['id']) , prop['type'])
            
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
            REQUEST.set('management_view', 'Price Policy')
            return self.manage_policyForm(self, REQUEST)

    def pricePolicies(self):
        # valid policies
        return self.PricePolicies.objectIds()

    def getPricePolicy(self):
        # the 'meta-policy' object ...
        try:
            if not getattr(aq_base(self), 'pricepolicy', None):
                return self.PricePolicies.defaultPolicy()
            return self.PricePolicies._getOb(self.pricepolicy)
        except:
            return None

manage_addBLPricePolicyFolderForm = PageTemplateFile('zpt/add_pricepolicyfolder', globals())
def manage_addBLPricePolicyFolder(self, REQUEST=None):
    """
    A repository for price policy objects
    """
    self._setObject('PricePolicies', BLPricePolicyFolder())
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL3'])
         
class BLPricePolicyFolder(OrderedFolder):
    """
    A folder for BLPricePolicies
    """
    meta_type = 'BLPricePolicyFolder'

    implements(IPricePolicyFolder)
    
    __ac_permissions = OrderedFolder.__ac_permissions__ + (
        (OperateBastionLedgers, ('defaultPolicy',)),
        )

    manage_options = (
        {'label':'Contents', 'action':'manage_main',
         'help':('BastionLedger', 'pricepolicies.stx') },
        ) + OrderedFolder.manage_options[2:5]
    
    id = 'PricePolicies'
    title = 'Price Policy Folder'

    def __init__(self): pass

        
    def all_meta_types(self):
        return ( ProductsDictionary('BLPricePolicy'), )

    def defaultPolicy(self):
        return self.objectValues()[0]
    
Globals.InitializeClass(BLPricePolicyFolder)

def addPricePolicyFolder(ob, event):
    ob._setObject('Standard',
                  BLPricePolicy('Standard', 'Standard', 'Price as set in inventory'))

    ob._getOb('Standard').ZPythonScript_edit('', '''return orderitem.calculateNetPrice()''')
    
