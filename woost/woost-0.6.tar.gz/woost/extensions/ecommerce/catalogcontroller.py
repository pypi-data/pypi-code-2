#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import (
    request_property,
    get_state,
    get_parameter,
    Pagination
)
from woost.models import Publishable
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.ecommerce.ecommerceproduct import ECommerceProduct

SESSION_KEY = "woost.extensions.ecommerce.catalog_state"

def catalog_current_state_uri():
    state = cherrypy.session.get(SESSION_KEY) or {}
    catalog = Publishable.require_instance(
        qname = "woost.extensions.ecommerce.catalog_page"
    )
    return catalog.get_uri(parameters = state)


class CatalogController(DocumentController):

    @request_property
    def products(self):
        return ECommerceProduct.select_accessible(order = [
            schema.expressions.CustomExpression(translations)
        ])

    @request_property
    def pagination(self):
        return get_parameter(
            Pagination.copy(**{
                "page_size.default": 20,
                "page_size.max": 100,
                "items": self.products
            }),
            errors = "set_default"
        )

    def submit(self):
        cherrypy.session[SESSION_KEY] = get_state()

    @request_property
    def output(self):
        output = DocumentController.output(self)
        output.update(
            products = self.products,
            pagination = self.pagination
        )
        return output

