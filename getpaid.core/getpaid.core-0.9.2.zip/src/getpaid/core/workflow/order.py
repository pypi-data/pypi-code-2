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

$Id: order.py 1488 2008-04-23 22:29:06Z horacio.duran $
"""

from zope import interface

from hurry.workflow import interfaces as iworkflow
from hurry.workflow import workflow

from getpaid.core.interfaces import workflow_states, IOrder, IPaymentProcessor, IDefaultFinanceWorkflow
from zope import component
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('getpaid')

def create_fulfillment_workflow( ):

    fs = workflow_states.order.fulfillment

    transitions = []
    add = transitions.append

    add( workflow.Transition( transition_id = 'create',
                              title= _(u'Create'),
                              source = None,
                              destination = fs.NEW ) )

    # needs condition on charged finance state..
    add( workflow.Transition( transition_id = 'process-order',
                              title = _(u'Process Order'),
                              source = fs.NEW,
                              destination = fs.PROCESSING ) )

    add( workflow.Transition( transition_id = 'deliver-processing-order',
                              title = _(u'Order Processed'),
                              #trigger = iworkflow.SYSTEM,
                              source = fs.PROCESSING,
                              destination = fs.DELIVERED ) )
    
    add( workflow.Transition( transition_id = 'cancel-order',
                              title = _(u'Will Not Deliver'),
                              destination = fs.WILL_NOT_DELIVER,
                              source = fs.PROCESSING ) )

    add( workflow.Transition( transition_id = 'cancel-new-order',
                              title = _(u'Will Not Deliver'),
                              source = fs.NEW,
                              destination = fs.WILL_NOT_DELIVER
                              ) )

    return transitions

#Separate workflow for shippable orders, I has different names on some of the 
#states and also a few states more
def create_shippable_fulfillment_workflow( ):

    fs = workflow_states.shippable_order.fulfillment

    transitions = []
    add = transitions.append

    add( workflow.Transition( transition_id = 'create',
                              title= _(u'Create'),
                              source = None,
                              destination = fs.NEW ) )

    # needs condition on charged finance state..
    add( workflow.Transition( transition_id = 'process-order',
                              title = _(u'Process Order'),
                              source = fs.NEW,
                              destination = fs.PROCESSING ) )

    add( workflow.Transition( transition_id = 'deliver-processing-order',
                              title = _(u'Order Processed'),
                              #trigger = iworkflow.SYSTEM,
                              source = fs.PROCESSING,
                              destination = fs.DELIVERED ) )
    
    add( workflow.Transition( transition_id = 'cancel-order',
                              title = _(u'Will Not Deliver'),
                              destination = fs.WILL_NOT_DELIVER,
                              source = fs.PROCESSING ) )

    add( workflow.Transition( transition_id = 'cancel-new-order',
                              title = _(u'Will Not Deliver'),
                              source = fs.NEW,
                              destination = fs.WILL_NOT_DELIVER
                              ) )

    return transitions


def create_finance_workflow( ):

    fs = workflow_states.order.finance

    transitions = []
    add = transitions.append

    # REVIEWING
    add( workflow.Transition( transition_id = 'create',
                              title = _(u'Create'),
                              source = None,
                              destination = fs.REVIEWING ) )


    add( workflow.Transition( transition_id = 'reviewing-declined',
                              title=_(u'Payment Declined'),
                              trigger = iworkflow.SYSTEM,
                              source = fs.REVIEWING,
                              destination = fs.PAYMENT_DECLINED ) )


    add( workflow.Transition( transition_id = 'authorize',
                              title = _(u'Authorize'),
                              trigger = iworkflow.SYSTEM,
                              source = fs.REVIEWING,
                              destination = fs.CHARGEABLE ) )

    # CHARGEABLE TRANSITIONS
    add( workflow.Transition( transition_id = 'charge-chargeable',
                              title = _(u'Charge Order'),
                              source = fs.CHARGEABLE,
                              destination = fs.CHARGING,
                              trigger = iworkflow.AUTOMATIC ) )

    add( workflow.Transition( transition_id = 'cancel-chargeable',
                              title = _(u'Cancel Order'),
                              source = fs.CHARGEABLE,
                              destination = fs.CANCELLED ) )
                              
    # CHARGING TRANSITIONS
    add( workflow.Transition( transition_id = 'decline-charging',
                              title = _(u'Processor Declined'),
                              source = fs.CHARGING,
                              destination = fs.PAYMENT_DECLINED,
                              trigger = iworkflow.SYSTEM ) )
                              
    add( workflow.Transition( transition_id = 'charge-charging',
                              title = _(u'Processor Charged'),
                              source = fs.CHARGING,
                              destination = fs.CHARGED,
                              trigger = iworkflow.SYSTEM ) )
                                                    

    # add( workflow.Transition( transition_id = 'authorize-chargeable',
    #                           title = _(u'Authorize Order'),
    #                           source = fs.CHARGEABLE,
    #                           destination = fs.CHARGEABLE ) )

    # CHARGED TRANSITIONS
    # add( workflow.Transition( transition_id = 'authorize-charged',
    #                           title = _(u'Authorize Order'),
    #                           source = fs.CHARGED,
    #                           destination = fs.CHARGED ) )

    # add( workflow.Transition( transition_id = 'refund-order',
    #                           title = _(u'Refund Order'),
    #                           source = fs.CHARGED,
    #                           destination = fs.REFUNDED ) )

    # add( workflow.Transition( transition_id = 'charge-charged',
    #                           title = _(u'Charge Order'),
    #                           source = fs.CHARGED,
    #                           destination = fs.CHARGED ) )


    # PAYMENT DECLINED TRANSITIONS

    add( workflow.Transition( transition_id = 'cancel-declined',
                              title=_(u'Cancel Order'),
                              source = fs.PAYMENT_DECLINED,
                              destination = fs.CANCELLED ) )

    # SYSTEM TRANSITIONS
    
    add( workflow.Transition( transition_id = 'processor-cancelled',
                              title = _(u'Processor Cancel'),
                              source = fs.REVIEWING,
                              destination = fs.CANCELLED_BY_PROCESSOR,
                              trigger = iworkflow.SYSTEM, ) )

    return transitions



class FulfillmentWorkflow( workflow.Workflow ):
    interface.implements( iworkflow.IWorkflow )
    def __init__( self ):
        super( FulfillmentWorkflow, self).__init__( create_fulfillment_workflow())

class ShippableFulfillmentWorkflow( workflow.Workflow ):
    interface.implements( iworkflow.IWorkflow )
    def __init__( self ):
        super( ShippableFulfillmentWorkflow, self).__init__( create_shippable_fulfillment_workflow())

class FinanceWorkflow( workflow.Workflow ):
    interface.implements( iworkflow.IWorkflow )
    def __init__( self ):
        super( FinanceWorkflow, self).__init__( create_finance_workflow() )

# if we passed in IOrder we could have all of these registered for us, but
# to make it easier to change these, we plugin them in via zcml.
FulfillmentWorkflowAdapter, FulfillmentState, FulfillmentInfo = workflow.ParallelWorkflow(
    workflow.AdaptedWorkflow( FulfillmentWorkflow() ),
    workflow_states.order.fulfillment.name,
    )

ShippableFulfillmentWorkflowAdapter, ShippableFulfillmentState, ShippableFulfillmentInfo = workflow.ParallelWorkflow(
    workflow.AdaptedWorkflow( ShippableFulfillmentWorkflow() ),
    workflow_states.order.fulfillment.name,
    )


FinanceWorkflowAdapter, FinanceState, FinanceInfo = workflow.ParallelWorkflow(
    workflow.AdaptedWorkflow( FinanceWorkflow() ),
    workflow_states.order.finance.name,
    )

interface.classImplements( FinanceWorkflowAdapter, IDefaultFinanceWorkflow )


if __name__ == '__main__':
    wk = FinanceWorkflow(None)


