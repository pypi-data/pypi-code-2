#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.controllers import (
    request_property,    
    Form,
    FormProcessor
)
from woost.models import get_current_user, ModifyMemberPermission
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder
from woost.extensions.ecommerce.basket import Basket
from woost.extensions.ecommerce.orderstepcontroller import (
    ProceedForm,
    BackForm
)


class CheckoutController(FormProcessor, DocumentController):

    class CheckoutForm(ProceedForm):
        
        @request_property
        def source_instance(self):
            return Basket.get()

        @request_property
        def adapter(self):
            user = get_current_user()
            adapter = ProceedForm.adapter(self)
            adapter.exclude(["customer", "status", "purchases"])
            adapter.exclude([
                member.name
                for member in self.model.members().itervalues()
                if not member.visible
                or not member.editable
                or not issubclass(member.schema, ECommerceOrder)
                or not user.has_permission(
                    ModifyMemberPermission,
                    member = member
                )
            ])      
            return adapter

        def submit(self):
            Form.submit(self)
            Basket.store()
            self.proceed()

    class PreviousStepForm(BackForm):
        pass

