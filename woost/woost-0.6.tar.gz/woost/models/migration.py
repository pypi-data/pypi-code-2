#-*- coding: utf-8 -*-
u"""Defines migrations to the database schema for woost.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

def admin_members_restriction(members):
    
    def add_permission(e):

        from woost.models import Role, ModifyMemberPermission
        
        everybody_role = Role.require_instance(qname = "woost.everybody")
        permission = ModifyMemberPermission(
            matching_members = list(members),
            authorized = False
        )
        permission.insert()
        
        for i, p in enumerate(everybody_role.permissions):
            if isinstance(p, ModifyMemberPermission) and p.authorized:
                everybody_role.permissions.insert(i, permission)
                break
        else:
            everybody_role.permissions.append(permission)

    return add_permission

#------------------------------------------------------------------------------

step = MigrationStep("added woost.models.Document.robots_*")

step.executing.append(
    admin_members_restriction([
        "woost.models.document.Document.robots_should_index",
        "woost.models.document.Document.robots_should_follow"
    ])
)

@step.processor("woost.models.document.Document")
def set_defaults(document):
    if not hasattr(document, "_robots_should_index"):
        document.robots_should_index = True
        document.robots_should_follow = True

#------------------------------------------------------------------------------

step = MigrationStep("added woost.models.Publishable.requires_https")

step.executing.append(
    admin_members_restriction([
        "woost.models.publishable.Publishable.requires_https"
    ])
)

@step.processor("woost.models.publishable.Publishable")
def set_defaults(publishable):
    if not hasattr(publishable, "_requires_https"):
        publishable.requires_https = False


#------------------------------------------------------------------------------

step = MigrationStep("make Product extend Publishable")

@when(step.executing)
def update_keys(e):
    from woost.extensions.shop import ShopExtension

    if ShopExtension.enabled:
        from cocktail.translations import translations
        from woost.models import Publishable, Controller, Language
        from woost.extensions.shop import create_product_controller
        from woost.extensions.shop.product import Product

        # Update the publishable keys
        Publishable.keys.update([product.id for product in Product.select()])

        # Create the product controller
        create_product_controller()

