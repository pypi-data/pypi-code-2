from tg import expose, flash, require, url, request, redirect, session, TGController, config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from webob.exc import HTTPNotFound

from stroller.lib import stroller_url, confirm_css
from stroller.lib.cart import results, get_cart, drop_cart
from stroller.lib.paypal import PayPal, ResponseError

from stroller.model.commerce import *
from stroller.model.core import DBSession

from tw.jquery import jquery_js
from datetime import datetime, timedelta

__all__ = ['PaymentController']

class PaymentController(TGController):
    @expose()
    def index(self):
        cart = get_cart()

        if not cart.total_quantity:
            flash(_('Your cart is empty'))
            return redirect(stroller_url('/'))

        for old_cart in  DBSession.query(Order).filter(Order.uid!=cart.uid)\
                                                .filter(Order.time<datetime.now()-timedelta(7))\
                                                .filter(Order.payed==False).all():
            DBSession.delete(old_cart)
        if config.get('avoid_manage_payment', False):
            return redirect(stroller_url('/payment/confirm_static', qualified=True))
        p = PayPal()
        try:

            r = p.call('SetExpressCheckout', amt=cart.total_price, landingpage='Billing',
                                             returnurl=stroller_url('/payment/confirm', qualified=True), 
                                             cancelurl=stroller_url('/payment/cancel', qualified=True))
        except ResponseError, e:
            flash(_('There has been an error in processing your payment request: %s') % e)
            return redirect(stroller_url('/'))

        return redirect(p.express_checkout_url(r.tokens['TOKEN']))
        
    @expose()
    def cancel(self):
        flash(_('Your transaction has been revoked'))
        return redirect(stroller_url('/'))        
    
    @expose()
    def cancel_static(self):
        flash(_('Your Cart was reset'))
        cart = get_cart()
        drop_cart()
        return redirect(stroller_url('/'))
    
    @expose('stroller.templates.payment.confirm')
    def confirm_static(self, **kw):
        cart = get_cart()

        confirm_css.inject()
        return results(proceed_url=stroller_url('/payment/proceed_static'))
            
    @expose()
    def proceed_static(self, **kw):
        cart = get_cart()
        drop_cart()
        cart.payed = False
        return redirect(stroller_url('/conclude', order=cart.uid))

    @expose('stroller.templates.payment.confirm')
    def confirm(self, **kw):
        
        cart = get_cart()
        
        p = PayPal()
        try:
            r = p.call('GetExpressCheckoutDetails', token=kw['token'])
        except ResponseError, e:
            flash('There has been an error in processing your payment request: %s' % e)
        
        if r.tokens['TOKEN'] != kw['token']:
            flash("Paypal didn't confirm the payment token, payment considered invalid")
            return redirect(stroller_url('/'))

        cart.set_data('first_name', r.tokens['FIRSTNAME'])
        cart.set_data('last_name', r.tokens['LASTNAME'])
        cart.set_data('email', r.tokens['EMAIL'])
        cart.set_data('ship_name', r.tokens['SHIPTONAME'])
        cart.set_data('ship_address', r.tokens['SHIPTOSTREET'])
        cart.set_data('ship_zip', r.tokens['SHIPTOZIP'])
        cart.set_data('ship_city', r.tokens['SHIPTOCITY'])
        cart.set_data('ship_state', r.tokens['SHIPTOSTATE'])
        cart.set_data('ship_country', r.tokens['SHIPTOCOUNTRYNAME'])
        
        confirm_css.inject()
        return results(userdata=r.tokens, token=kw['token'], payerid=kw['PayerID'],
                       proceed_url=stroller_url('/payment/proceed'))
        
    @expose()
    def proceed(self, **kw):
        token = kw['token']
        payer = kw['payerid']
        amount = kw['total']
        
        p = PayPal()
        try:
            r = p.call('DoExpressCheckoutPayment', paymentaction="Sale", token=token, payerid=payer, amt=amount)
        except ResponseError, e:
            flash('There has been an error in processing your payment: %s' % e)
            return redirect(stroller_url('/'))
            
        cart = get_cart()
        for p in cart.items:
            p.product.bought += 1
            
        drop_cart()
        cart.payed = True
        return redirect(stroller_url('/conclude', order=cart.uid))
        
