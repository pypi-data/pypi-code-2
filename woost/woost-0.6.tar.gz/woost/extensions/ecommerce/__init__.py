#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.events import event_handler, when
from cocktail.modeling import underscore_to_capital
from cocktail.translations import (
    translations,
    set_language,
    language_context
)
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import (
    Site,
    Extension,
    Publishable,
    Document,
    StandardPage,
    Template,
    Controller
)

translations.define("ECommerceExtension",
    ca = u"Comerç online",
    es = u"Comercio online",
    en = u"E-commerce"
)

translations.define("ECommerceExtension-plural",
    ca = u"Comerç online",
    es = u"Comercio online",
    en = u"E-commerce"
)


class ECommerceExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet vendre productes des del lloc web.""",
            "ca"
        )
        self.set("description",            
            u"""Permite vender productos des del sitio web.""",
            "es"
        )
        self.set("description",
            u"""Allows selling products online.""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):

        extension = event.source

        from woost.extensions.ecommerce import (
            strings,
            ecommerceproduct,
            ecommerceorder,
            ecommercepurchase,
            ecommercebillingconcept
        )

        # Add the necessary members to define pricing policies
        ECommerceExtension.members_order = [
            "pricing",
            "shipping_costs", 
            "taxes",
            "order_steps"
        ]

        ECommerceExtension.add_member(
            schema.Collection("pricing",
                items = schema.Reference(
                    type = ecommercebillingconcept.ECommerceBillingConcept
                ),
                bidirectional = True,
                related_end = schema.Collection(),
                integral = True
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("shipping_costs",
                items = schema.Reference(
                    type = ecommercebillingconcept.ECommerceBillingConcept
                ),
                bidirectional = True,
                related_end = schema.Collection(),
                integral = True
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("taxes",
                items = schema.Reference(
                    type = ecommercebillingconcept.ECommerceBillingConcept
                ),
                bidirectional = True,
                related_end = schema.Collection(),
                integral = True
            )
        )

        ECommerceExtension.add_member(
            schema.Collection("order_steps",
                items = schema.Reference(type = Publishable),
                related_end = schema.Collection()
            )
        )

        # If the payments extension is enabled, setup the payment gateway for
        # the shop
        from woost.extensions.payments import PaymentsExtension
        payments_ext = PaymentsExtension.instance

        if payments_ext.enabled:
            extension._setup_payment_gateway()
        
        # Create the pages for the shop the first time the extension runs
        if not extension.installed:
            extension.create_content()
            datastore.commit()

    def _setup_payment_gateway(self):
            
        from tpv import (
            Currency,
            Payment,
            PaymentItem,
            PaymentNotFoundError
        )
        from woost.extensions.payments.paymentgateway import PaymentGateway
        from woost.extensions.payments.transactionnotifiedtrigger \
            import launch_transaction_notification_triggers
        from woost.extensions.ecommerce.ecommerceorder import ECommerceOrder

        def get_payment(self, payment_id):

            order = ECommerceOrder.get_instance(int(payment_id))

            if order is None:
                raise PaymentNotFoundError(payment_id)
            
            payment = Payment()
            payment.id = order.id
            payment.amount = order.cost
            payment.order = order
            payment.currency = Currency(payments_ext.payment_gateway.currency)
            
            for entry in order.entries:
                payment.add(PaymentItem(
                    reference = str(entry.product.id),
                    description = translations(entry.product),
                    units = entry.quantity,
                    price = entry.cost
                ))

            return payment

        PaymentGateway.get_payment = get_payment

        def receive_order_payment(event):
            payment = event.payment
            order = payment.order
            set_language(order.language)
            order.status = payment.status
            order.gateway_parameters = payment.gateway_parameters

        def commit_order_payment(event):
            datastore.commit()

        events = PaymentGateway.transaction_notified
        pos = events.index(launch_transaction_notification_triggers)
        events.insert(pos, receive_order_payment)
        events.insert(pos + 2, commit_order_payment)

    def create_content(self):
        
        catalog = self._create_document("catalog")
        catalog.controller = self._create_controller("catalog")
        catalog.template = self._create_template("catalog")
        catalog.parent = Site.main.home
        catalog.insert()

        for child_name in (
            "basket",
            "checkout",
            "summary"
        ):
            child = self._create_document(child_name)
            child.hidden = True
            child.template = self._create_template(child_name)
            child.controller = self._create_controller(child_name)
            child.parent = catalog
            child.insert()
            self.order_steps.append(child)

        for child_name in (
            "success",
            "failure"
        ):
            child = self._create_document(child_name, StandardPage)
            child.hidden = True
            child.parent = catalog
            child.insert()

        self._create_controller("product").insert()
        self._create_template("product").insert()
    
    def _create_document(self, name, 
        cls = Document, 
        template = None,
        controller = None):

        document = cls()
        document.qname = "woost.extensions.ecommerce.%s_page" % name

        self.__translate_field(document, "title")

        if isinstance(document, StandardPage):
            self.__translate_field(document, "body")

        return document

    def _create_template(self, name):
        template = Template()
        template.qname = "woost.extensions.ecommerce.%s_template" % name
        self.__translate_field(template, "title")
        template.engine = "cocktail"
        template.identifier = \
            "woost.extensions.ecommerce.%sPage" % underscore_to_capital(name)
        return template

    def _create_controller(self, name):
        controller = Controller( )
        controller.qname = "woost.extensions.ecommerce.%s_controller" % name
        self.__translate_field(controller, "title")
        controller.python_name = \
            "woost.extensions.ecommerce.%scontroller.%sController" % (
                name,
                underscore_to_capital(name)
            )
        return controller

    def __translate_field(self, obj, key):
        for language in translations:
            with language_context(language):
                value = translations("%s.%s" % (obj.qname, key))
                if value:
                    obj.set(key, value)

