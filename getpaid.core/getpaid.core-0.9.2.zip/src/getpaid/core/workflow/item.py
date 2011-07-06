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

order line item fulfillment, we defer full implementation of shippable fulfillment workflows

transition : create

   destination - new

transition : deliver-virtual

   source - new
   condition : not shippable
   state - delivered
   trigger : system

transition : ship

   source - new
   destination - processing

transition : cancel

   source - new
   state - cancelled

transition : cancel - processing

   source - processing
   state - cancelled
   condition - shipment not authorized
    
transition :  shipment-authorized

   source - processing
   state - shipppable

transition : process return

   source - shipped
   state - return in progress
   condition - returnable
   option - restocking fee   
   generate - rma number

   -- returns are there own shipments with workflow ?

transition : received return
  source : return in progress
  condition :
  option : ? 


transition : refund-delievered

   condition : virtual delivery | or refundable
   source : delivered
   state : refund-processing

transition : refund-processed

   state : refunded
   source : refund-processing
   

$Id: item.py 1141 2007-12-30 23:47:15Z kapilt $
"""

from zope.interface import implements
from zope import component

from hurry.workflow import interfaces as iworkflow
from hurry.workflow import workflow

from getpaid.core.interfaces import workflow_states, IShippableContent

import getpaid.core.workflow

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid')

def VirtualDeliverable( wf, context ):
    return not component.queryAdapter( IShippableContent, context ) is None

def create_item_workflow( ):

    its = workflow_states.item

    transitions = []
    add = transitions.append
    
    add( workflow.Transition(
        transition_id = 'create',
        title='Create',
        source = None,
        destination = its.NEW
        ) )

    add( workflow.Transition(
        transition_id = 'deliver-virtual',
        title=_(u'Electronic Delivery'),
        condition = VirtualDeliverable,
        trigger = iworkflow.SYSTEM,
        source = its.NEW,
        destination = its.DELIVER_VIRTUAL
        ) )    

    add( workflow.Transition(
        transition_id = 'cancel',
        title=_(u'Cancel'),
        source = its.NEW,
        destination = its.CANCELLED
        ) )    


    add( workflow.Transition(
        transition_id = 'refund',
        title=_(u'Refund'),
        source = its.DELIVER_VIRTUAL,
        destination = its.REFUNDING
        ) )

    add( workflow.Transition(
        transition_id = 'refund-processed',
        title=_(u'Refund Processed'),
        source = its.REFUNDING,
        trigger = iworkflow.SYSTEM,
        destination = its.REFUNDED
        ) )


    add( workflow.Transition(
        transition_id = 'ship',
        title=_(u'Ship'),
        source = its.NEW,
        trigger = iworkflow.SYSTEM,
        destination = its.SHIPPED
        ) )
    
    return transitions

class ItemWorkflow( workflow.Workflow ):

    def __init__( self ):
        super( ItemWorkflow, self).__init__( create_item_workflow())

ItemWorkflowAdapter = workflow.AdaptedWorkflow( ItemWorkflow() )

if __name__ == '__main__':
    wf = ItemWorkflow()
    print wf.toDot()


    
