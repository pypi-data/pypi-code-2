#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from tpv.pasat4b import Pasat4bPaymentGateway as Implementation
from cocktail import schema
from woost.extensions.payments.paymentgateway import PaymentGateway


class Pasat4bPaymentGateway(PaymentGateway, Implementation):

    instantiable = True

    merchant_code = schema.String(
        required = True,
        shadows_attribute = True,
        text_search = False
    )

