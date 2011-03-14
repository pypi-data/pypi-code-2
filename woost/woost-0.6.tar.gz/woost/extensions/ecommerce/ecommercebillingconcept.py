#-*- coding: utf-8 -*-
"""Provides a variety of models to implement customizable discounts, taxes and
shipping costs.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from decimal import Decimal
from datetime import datetime
from cocktail.modeling import abstractmethod
from cocktail.translations import translations
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Item, Role
from woost.extensions.locations.location import Location
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct

override_regexp = re.compile(r"^=\s*((-|\+)?\d+(.\d+)?)$")
add_regexp = re.compile(r"^((-|\+)?\d+(.\d+)?)$")
override_percentage_regexp = re.compile(r"^=\s*((-|\+)?\d+(\.\d+)?)%$")
add_percentage_regexp = re.compile(r"^((-|\+)?\d+(\.\d+)?)%$")
free_units_regexp = re.compile(r"^\d\s*x\s*\d?$")


class ECommerceBillingConcept(Item):

    members_order = [
        "title",
        "enabled",
        "start_date",
        "end_date",
        "hidden",
        "scope",
        "eligible_regions",
        "eligible_products",
        "eligible_roles",
        "condition",
        "implementation"
    ]
    
    title = schema.String(
        translated = True,
        descriptive = True,
        required = True
    )

    enabled = schema.Boolean(
        required = True,
        default = True
    )
    
    start_date = schema.DateTime(
        indexed = True
    )

    end_date = schema.DateTime(
        indexed = True,
        min = start_date
    )

    hidden = schema.Boolean(
        default = False,
        required = True
    )

    scope = schema.String(
        required = True,
        enumeration = ["order", "purchase"],
        default = "order",
        edit_control = "cocktail.html.RadioSelector",
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
               else translations(
                        "ECommerceBillingConcept.scope-" + value, 
                        language, 
                        **kwargs)
    )

    condition = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    eligible_regions = schema.Collection(
        items = schema.Reference(type = Location),
        related_end = schema.Collection()
    )

    eligible_products = schema.Collection(
        items = schema.Reference(type = ECommerceProduct),
        related_end = schema.Collection()
    )

    eligible_roles = schema.Collection(
        items = schema.Reference(type = Role),
        related_end = schema.Collection()
    )

    implementation = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    def is_current(self):
        return (self.start_date is None or self.start_date <= datetime.now()) \
           and (self.end_date is None or self.end_date > datetime.now())

    def applies_to(self, item, costs = None):

        if not self.enabled:
            return False

        if not self.is_current():
            return False

        from woost.extensions.ecommerce.ecommerceproduct \
            import ECommerceProduct

        order = None
        purchase = None
        product = None

        if isinstance(item, ECommerceProduct):

            if self.eligible_products and item not in self.eligible_products:
                return False

            product = item

        elif self.scope == "order":
            from woost.extensions.ecommerce.ecommerceorder \
                import ECommerceOrder
            if not isinstance(item, ECommerceOrder):
                return False

            if self.eligible_products and not any(
                purchase.product in self.eligible_products
                for purchase in item.purchases
            ):
                return False

            order = item
            
        elif self.scope == "purchase":
            from woost.extensions.ecommerce.ecommercepurchase \
                import ECommercePurchase
            if not isinstance(item, ECommercePurchase):
                return False

            if self.eligible_products \
            and item.product not in self.eligible_products:
                return False

            order = item.order
            purchase = item
            product = item.product

        if self.eligible_regions and (
            order is None
            or order.region is None
            or not any(
                order.region.descends_from(region) 
                for region in self.eligible_regions
            )
        ):
            return False

        # Eligible roles
        if self.eligible_roles and (
            order is None
            or order.customer is None
            or not any(
                role in self.eligible_roles
                for role in order.customer.iter_roles()
            )
        ):
            return False

        # Custom condition
        if self.condition:
            context = {
                "self": self, 
                "order": order,
                "purchase": purchase,
                "product": product,
                "costs": costs,
                "applies": True
            }
            exec self.condition in context
            if not context["applies"]:
                return False
                
        return True

    def apply(self, item, costs):

        costs["concepts"].append(self)

        kind, value = self.parse_implementation()
        
        if kind == "override":
            costs["cost"] = value

        elif kind == "add":
            costs["cost"] += value

        elif kind == "override_percentage":
            costs["percentage"] = value
        
        elif kind == "add_percentage":
            costs["percentage"] += value

        elif kind == "free_units":
            delivered, paid = value
            q, r = divmod(item.quantity, delivered)
            costs["paid_units"] = q * paid + r

        elif kind == "custom":
            context = {"self": self, "item": item, "costs": costs}
            exec value in context

    def parse_implementation(self):

        value = self.implementation
        
        # Cost override
        match = override_regexp.match(value)
        if match:
            return ("override", Decimal(match.group(1)))

        # Additive cost
        match = add_regexp.match(value)
        if match:
            return ("add", Decimal(match.group(1)))

        # Override percentage
        match = override_percentage_regexp.match(value)
        if match:
            return ("override_percentage", Decimal(match.group(1)))

        # Override percentage
        match = add_percentage_regexp.match(value)
        if match:
            return ("add_percentage", Decimal(match.group(1)))

        # Free units discount ("3x2", "2x1", etc)
        match = free_units_regexp.match(value)
        if match:
            return ("free_units", (int(match.group(1)), int(match.group(2))))

        return ("custom", value)

