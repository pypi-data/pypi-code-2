# Copyright (c) 2008 ifPeople, Kapil Thangavelu, and Contributors
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from zope import interface, component

from getpaid.core.interfaces import IStoreSettings, IShippableLineItem, IOrder
from getpaid.core.payment import Address, ContactInformation

import interfaces

class OriginRouter( object ):

    component.adapts( IOrder )
    interface.implements( interfaces.IOriginRouter )
    
    def __init__( self, context ):
        self.context = context
            
    def getStoreSettings( self ):
        store_settings = component.getUtility( IStoreSettings )
        contact = ContactInformation( name = ( store_settings.contact_company or store_settings.store_name ),
                                      phone_number = store_settings.contact_phone,
                                      email = store_settings.contact_email )
                                      
        address = Address( first_line = store_settings.contact_address,
                           second_line = store_settings.contact_address2,
                           city = store_settings.contact_city,
                           state = store_settings.contact_state,
                           postal_code = store_settings.contact_postalcode,
                           country = store_settings.contact_country )
        
        return contact, address
        
    getOrigin = getStoreSettings