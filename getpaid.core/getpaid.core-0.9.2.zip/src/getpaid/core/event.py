# Copyright (c) 2007 ifPeople, Kapil Thangavelu, and Contributors
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

"""
$Id: event.py 3416 2010-04-07 20:30:10Z dglick $
"""

from zope.interface import implements
from zope.component.interfaces import ObjectEvent

import interfaces

class PayableCreationEvent( ObjectEvent ):

    implements( interfaces.IPayableCreationEvent )
    
    def __init__( self, object, payable, payable_interface ):
        super( PayableCreationEvent, self).__init__( object )
        self.payable = payable
        self.payable_interface = payable_interface

class BeforeCheckoutEvent( ObjectEvent ):
    
    def __init__( self, context, order, request):
        super( BeforeCheckoutEvent, self).__init__( order )
        self.request = request
        self.context = context

# we need to move the payable markers into getpaid
# def objectCreation( object, event ):
#     
#     if interfaces.IPayable.providedBy( object ):
#         notify( PayableCreationEvent( object, object, interfaces.IPayable ) )
