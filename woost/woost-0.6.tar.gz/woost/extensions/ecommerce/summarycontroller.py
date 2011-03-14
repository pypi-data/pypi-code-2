#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    request_property,
    FormProcessor
)
from woost.models import (
    Publishable,
    get_current_user,
    ModifyMemberPermission
)
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder
from woost.extensions.ecommerce.basket import Basket
from woost.extensions.ecommerce.orderstepcontroller import (
    ProceedForm,
    BackForm
)
from woost.extensions.payments import PaymentsExtension


class SummaryController(FormProcessor, DocumentController):

    @request_property
    def checkout_schema(self):
        checkout_schema = schema.Schema("OrderCheckoutSummary")
        self.checkout_adapter.export_schema(
            Basket.get().__class__,
            checkout_schema
        )
        return checkout_schema
        
    @request_property
    def checkout_adapter(self):
        user = get_current_user()            
        adapter = schema.Adapter()
        adapter.exclude(["customer", "status", "purchases"])
        adapter.exclude([
            member.name
            for member in Basket.get().__class__.members().itervalues()
            if not member.visible
            or not member.editable
            or not issubclass(member.schema, ECommerceOrder)
            or not user.has_permission(
                ModifyMemberPermission,
                member = member
            )
        ])
        return adapter

    @request_property
    def output(self):
        output = DocumentController.output(self)
        output["checkout_schema"] = self.checkout_schema
        return output

    class SubmitOrderForm(ProceedForm):
        
        def submit(self):

            ProceedForm.submit(self)
            
            order = Basket.pop()
            order.status = "payment_pending"
            order.update_cost()

            datastore.commit()
            payments = PaymentsExtension.instance
            
            # Redirect the user to the payment gateway
            if payments.enabled and payments.payment_gateway:
                payments.payment_request(order.id)
            
            # No payment gateway available, redirect the user to the success
            # page; the payment will have to be handled manually by the site's
            # personnel
            else:
                raise cherrypy.HTTPRedirect(
                    Publishable.require_instance(
                        qname = "woost.extensions.ecommerce.success_page"
                    ).get_uri(
                        parameters = {"order": order.id}
                    )
                )

    class PreviousStepForm(BackForm):
        pass

