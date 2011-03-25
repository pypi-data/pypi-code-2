"""
    Simple Payment Processor for Realex
"""

import logging

from five import grok

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.PloneGetPaid.interfaces import IGetPaidManagementOptions
from getpaid.core.interfaces import IPaymentProcessor, keys

from realexoptions import IRealexOptions
from realex import Realex
from aborthook import registerAbortHook

logger = logging.getLogger('getpaid.realex')

class RealexProcessor( grok.Adapter ):
    """ A Payment Processor

    a processor can keep processor specific information on an orders
    annotations.
    """
    grok.context(ISiteRoot)
    grok.name('Realex')
    grok.provides(IPaymentProcessor)

    options_interface = IRealexOptions

    _options = None
    _management_options = None

    def __init__( self, context ):
        self.context = context


    @property
    def options(self):
        if self._options == None:
            siteroot = getToolByName(self.context, "portal_url").getPortalObject()
            self._options = IRealexOptions( siteroot )
        return self._options

    @property
    def management_options(self):
        if self._management_options == None:
            siteroot = getToolByName(self.context, "portal_url").getPortalObject()
            self._management_options = IGetPaidManagementOptions( siteroot )
        return self._management_options

    def authorize(self, order, payment_information ):
        """
        Authorization confirms that an order may be processed using the given billing
        information.
        """

        logging.info('About to authorise order: %s' % order.order_id)

        order_id = order.order_id
        amount = str(int(order.getTotalPrice() * 100)) # amount in cent
        card_number = payment_information.credit_card
        card_expdate = payment_information.cc_expiration.strftime('%m%y')  # format MMYY
        card_chname = payment_information.name_on_card
        card_type = payment_information.credit_card_type  # TODO review mappings
        cvn = payment_information.cc_cvc

        custipaddress = self.context.REQUEST.HTTP_X_FORWARDED_FOR
        if not custipaddress:
            custipaddress = self.context.REQUEST.REMOTE_ADDR

        realex = Realex(self.options.MerchantID, self.options.Secret, self.options.Testing,
                SubAccount=self.options.SubAccount, chargeDescription=self.options.chargeDescription)

        try:
            prodid = order.shopping_cart.values()[0].product_code
        except:
            prodid = None

        rv = realex.Authorise(order_id, amount, card_number, card_expdate,
            card_chname, card_type, card_cvn=cvn, prodid=prodid,
            chargeDescription=self.management_options.store_name,
            custipaddress=custipaddress)

        # Store authcode and pasref code - These are required to void / rebate the transaction
        if rv['result'] == 0:
            logging.info('Authorised order: %s' % order.order_id)

            order.realex_result = rv['result']
            order.realex_authcode = rv['authcode']
            order.realex_orderid = rv['orderid']
            order.realex_pasref = rv['pasref']
            order.realex_message = rv['message']
            order.realex_rebate_total = 0.0  # track rebates

            order.processor_order_id = rv['orderid']
            order.user_payment_info_trans_id= "%s/%s" % (rv['authcode'], rv['pasref'])

            registerAbortHook(lambda: self._abortHook(rv['orderid'], rv['pasref'], rv['authcode'], realex))

            return keys.results_success

        logging.info('Failed to authorised order: %s, result %s' % (order.order_id, rv['result']))

    def _abortHook(self, orderid, pasref, authcode, realex):
        logger.warn("Voiding credit card request due to transaction abort. orderid = %s, pasref = %s, authcode = %s" %
                (orderid, pasref, authcode))
        realex.Void(orderid, pasref, authcode, "voiding payment/rebate due to transaction abort")

    def capture(self, order, amount ):
        """
        Capturing an order tells Realex to queue payment for settlement. (Actual
        settlement happens in a daily batch process.)

        This is called in the work flow after authorize returns. Just ignore it.
        """
        return keys.results_success

    def refund(self, order, amount ):
        """
        Refunding an order tells Realex to return the payment to the customer.
        """
        logging.info('About to refund order: %s, amount %s' % (order.order_id, amount))

        realex = Realex(self.options.MerchantID, self.options.Secret, self.options.Testing,
                SubAccount=self.options.SubAccount, chargeDescription=self.options.chargeDescription)

        order_id = order.order_id
        amount = str(int(amount * 100)) # amount in cent

        rv = realex.Rebate(order_id, order.realex_pasref, order.realex_authcode, amount,
            self.management_options.RebatePassword)

        order.realex_result = rv['result']
        order.realex_message = rv['message']

        if rv['result'] == 0:
            order.realex_rebate_total += amount
            logging.info('Refunded order: %s, amount %s' % (order.order_id, amount))
            return keys.results_success
        logging.info('Failed to refund order: %s, amount %s, result %s' % (order.order_id, amount, rv['result']))
