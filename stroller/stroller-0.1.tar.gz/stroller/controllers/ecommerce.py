# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import tmpl_context
from tw.api import WidgetsList
from tw.forms import TableForm, SingleSelectField, FormField, TextField
from tw.dynforms import OtherSingleSelectField, HidingContainerMixin, HidingSingleSelectField
from formencode import validators

from tg import expose, flash, require, url, request, redirect, session, TGController
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates
from webob.exc import HTTPNotFound

from stroller.lib import stroller_url, style_css
from stroller.lib.cart import results, get_cart
from stroller.model.commerce import *
from stroller.model.core import DBSession
from stroller.controllers.payment import PaymentController
from stroller.controllers.manage import ManageController
from stroller.controllers.widgets import QuantityOtherSingleSelectField
from stroller import model

from tw.jquery import jquery_js

__all__ = ['StrollerController']

class NumberForm(TableForm):
    class fields(WidgetsList):
        quantity = QuantityOtherSingleSelectField(field='Quantity', label_text='Quantity')
create_number_form = NumberForm("create_number_form", submit_text = None)

class StrollerController(TGController):
    payment = PaymentController()
    admin = AdminController([Category, Product, ProductInfo], DBSession, config_type=TGAdminConfig)
    manage = ManageController()

    @expose('stroller.templates.index')
    def index(self):
        category = DBSession.query(Category).filter_by(name='Shop').first()
        front_categories = DBSession.query(Category).filter_by(featured=True).all()
        featured = DBSession.query(Product).filter_by(featured=True).all()
        favourites = DBSession.query(Product).order_by(Product.bought.desc())[:6]
            
        style_css.inject()
        return results(front_categories=front_categories,
                        featured=featured, favourites=favourites,
                        category=category)
        
    @expose('stroller.templates.category')
    def category(self, uid=None):
        category = DBSession.query(Category).filter_by(uid=uid).first()
        if category.name == 'Shop':
            return redirect(stroller_url('/'))
            
        if not category:
            raise HTTPNotFound()
            
        style_css.inject()
        return results(category=category)

    @expose(content_type='image/jpeg')
    def category_icon(self, uid=None):
        category = DBSession.query(Category).filter_by(uid=uid).first()
        if not uid:
            raise HTTPNotFound()

        return category.icon
        
    @expose('stroller.templates.product')
    def product(self, uid=None):
        product = DBSession.query(Product).filter_by(uid=uid).first()
        if not product:
            raise HTTPNotFound()
            
        jquery_js.inject()
        style_css.inject()
        return results(product=product, form=create_number_form)
        
    @expose('stroller.templates.search')
    def search(self, what=''):
        if not what or len(what) < 3:
            flash('Search too short', 'warning')
            return redirect(stroller_url('/'))

        category = DBSession.query(Category).filter_by(name='Shop').first()
        products = DBSession.query(Product).join(ProductInfo).filter(ProductInfo.name.like('%'+what+'%'))
            
        jquery_js.inject()
        style_css.inject()
        return results(what=what, products=products, category=category)
       
        
    @expose(content_type='image/jpeg')
    def product_thumb(self, uid=None):
        product = DBSession.query(Product).filter_by(uid=uid).first()
        if not uid:
            raise HTTPNotFound()
        
        return product.thumb
        
    @expose(content_type='image/jpeg')
    def product_image(self, uid=None):
        product = DBSession.query(Product).filter_by(uid=uid).first()
        if not uid:
            raise HTTPNotFound()
        
        return product.photo
        
    @expose('json')
    def add_to_cart(self, product=None, qnt=1):
        cart = get_cart()
        product = Product.get(product)
        if product and cart:
            if (product.stock == None) or (product.stock):
                cart.add_item(product, int(qnt))
            else:
                flash(_('Product is currently not available'))
            
        return results(cart=cart, price=cart.total_price, 
                        quantity=cart.total_quantity)
        

    @expose()
    def conclude(self, order=None):
        order = Order.get(order)
        if not order.dispatched and order.payed:
            flash(_('Payment successfully registered.'))
            order.dispatched = True
        if not order.payed:
             flash(_('Order registered but not payed, Please provide your order id either by telephone or fax to proceed with payment. Order ID: %s') % order.uid)
        return redirect(stroller_url('/'))
