from tg import expose, flash, require, url, request, redirect, session, TGController, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from webob.exc import HTTPNotFound

from stroller.lib import stroller_url, manage_css, language
from stroller.model.commerce import *
from stroller.model.core import DBSession

from tw.jquery import jquery_js
from sprox.formbase import AddRecordForm, Field
from tw.api import WidgetsList
import tw.forms as twf
from tw.forms import validators, TextField, TextArea

import Image, cgi
from cStringIO import StringIO

__all__ = ['ManageController']

class CategoryForm(AddRecordForm):
    __model__ = Category
    __omit_fields__ = ['subcategories', 'products']
    __hide_fields__ = ['parent']
    __require_fields__ = ['name', 'parent']
category_form = CategoryForm(DBSession)

class ProductForm(AddRecordForm):
    __model__ = Product
    __omit_fields__ = ['info', 'orderitems', 'thumb', 'featured', 'bought']
    __hide_fields__ = ['category']
    __require_fields__ = ['name', 'category', 'sku', 'description', 'price']
    __field_order__ = ['name', 'sku', 'photo', 'price', 'needs_shipping', 'description']
    __field_validators__ = {'photo':validators.FieldStorageUploadConverter(not_empty=True)}
    name = TextField('name', validator=validators.String(not_empty=True))
    description = TextArea('description', validator=validators.String(not_empty=True))
product_form = ProductForm(DBSession)

class SkuValidator(twf.validators.FancyValidator):
    messages = { 'exists':'That value already exists' }
    
    def validate_python(self, value, state):
        para = request.params
        if DBSession.query(Product).filter_by(sku=value).first():
             if not para.get('p') or not str(DBSession.query(Product).filter_by(sku=value).first().uid) == str(para['p']):
                raise twf.validators.Invalid('exists', value, state)

class CloneField(twf.TableForm):
    class fields(WidgetsList):
        op = twf.HiddenField()
        sku = twf.TextField(label_text="SKU", validator = SkuValidator(not_empty=True))

skuform = CloneField(submit_text="Set")


class EditProductFields(twf.TableForm):
    class fields(WidgetsList):
        p = twf.HiddenField()
        name = twf.TextField(label_text="Name")
        sku = twf.TextField(label_text="SKU", validator = SkuValidator(not_empty=True))
        price = twf.TextField(label_text="Price")
        description = twf.TextField(label_text="Description")
        photo = twf.FileField(label_text="Photo", validator=validators.FieldStorageUploadConverter())
        nstock = twf.TextField(label_text="in Stock") #, validator=Integer(min=0)) 
        nshtime = twf.TextField(label_text="Shipping Time in days") #, validator=Integer())
edit_product_form = EditProductFields(submit_text="Edit")


class EditOrderFields(twf.TableForm):
    class fields(WidgetsList):
        fname = twf.TextField(label_text="First Name")
        lname = twf.TextField(label_text="Last Name")
        email = twf.TextField(label_text="email")
        shname = twf.TextField(label_text="Ship Name")
        shaddr = twf.TextField(label_text="Ship Address")
        shzip = twf.TextField(label_text="Ship Zip")
        shcity = twf.TextField(label_text="Ship City")
        shstate = twf.TextField(label_text="Ship State")
        shcountry = twf.TextField(label_text="Ship Country")
edit_order_form = EditOrderFields(submit_text="Edit")

def thumbnail(what, size=(128,128)):
    thumb_data = StringIO()

    thumb = Image.open(what)
    thumb.thumbnail(size)
    thumb = thumb.convert('RGB')
    thumb.save(thumb_data, 'JPEG')

    return thumb_data.getvalue()

def productimage(what):
    img_data = StringIO()

    img = Image.open(what)
    img = img.convert('RGB')
    img.save(img_data, 'JPEG')

    return img_data.getvalue()


class ManageController(TGController):
    allow_only = predicates.in_group('stroller', msg=l_('Only for people in the "stroller" group'))


    @expose('stroller.templates.manage.form')
    def create_category(self, **kw):
        manage_css.inject()
        values = {'parent':kw['parent']}
        action = stroller_url('/manage/do_create_category')
        return dict(form=category_form, 
                     title="Create Category",
                     values=values,
                     action=action)

    @expose()
    @validate(category_form, create_category)
    def do_create_category(self, **kw):
        del kw['sprox_id']
        kw['parent'] = Category.by_id(kw['parent'])

        if kw.get('icon') != None:
            kw['icon'] = thumbnail(kw['icon'].file, (164, 164))
        else:
            kw['icon'] = None

        cat = Category(**kw)
        flash('Correctly created the new category')
        return redirect(stroller_url('/category', uid=kw['parent'].uid))

    @expose()
    def do_delete_category(self, **kw):
        def recursively_delete(cat):
            for c in cat.subcategories:
                recursively_delete(c)
            DBSession.delete(cat)
            
        category = Category.by_id(kw['category_id'])
        parent = category.parent
        recursively_delete(category)
        flash('Category correctly deleted')
        return redirect(stroller_url('/category', uid=parent.uid))

    @expose('stroller.templates.manage.form')
    def add_product(self, **kw):
        manage_css.inject()
        values = {'category':kw['category']}
        action = stroller_url('/manage/do_add_product')
        return dict(form=product_form,
                     title="Add Product",
                     values=values,
                     action=action)
                     
    @expose()
    @validate(product_form, add_product)
    def do_add_product(self, **kw):
        product_data = kw
        
        del product_data['sprox_id']
        product_data['category'] = Category.by_id(kw['category'])
        product_data['thumb'] = thumbnail(product_data['photo'].file)
        product_data['photo'].file.seek(0)
        product_data['photo'] = productimage(product_data['photo'].file)
        
        product_info = {}
        product_info['name'] = kw['name']
        product_info['description'] = kw['description']
        product_info['lang'] = language()[0]
        
        del kw['name']
        del kw['description']
        
        p = Product(**product_data)
        DBSession.add(p)
        
        product_info['product'] = p
        pi = ProductInfo(**product_info)
        DBSession.add(pi)
        
        return redirect(stroller_url('/category', uid=kw['category'].uid))
        

    
    
    @expose('stroller.templates.manage.form')
    def clone_product(self, op, **kw):
        manage_css.inject()
        p = Product.get(op)
        kw['op'] = p.uid
        return dict(title="New Product SKU", form=skuform, p=p, values=kw,
                    action=stroller_url('/manage/do_clone_product'))
        
    @expose()
    @validate(skuform, clone_product)
    def do_clone_product(self, **kw):
        p = Product.get(kw['op'])
        product_info = {'name':p.name+" copy"}
        product_info['description'] = p.description
        product_info['lang'] = language()[0]
        
        product_data = {}
        #product_data['name'] = p.name
        product_data['photo'] = p.photo
        product_data['sku'] = kw['sku']
        product_data['price'] = p.price
        product_data['needs_shipping'] = p.needs_shipping
        product_data['category'] = p.category
        product_data['thumb'] =p.thumb

        #product_info['lang'] =p.lang #??
        
        p = Product(**product_data)
        DBSession.add(p)
        product_info['product'] = p
        pi = ProductInfo(**product_info)
        DBSession.add(pi)
        
        return redirect(stroller_url('/category', uid=product_data['category'].uid))
    
    @expose()
    def del_product(self, p):
        p = Product.get(p)
        dest = '/'
        if p:
            if p.category:
                dest = stroller_url('/category', uid=p.category.uid)
            else:
                dest = stroller_url('/')
            flash("Product successfully removed")
            DBSession.delete(p)
        return redirect(dest)
    
    @expose('stroller.templates.manage.form')
    def edit_product(self, p, **kw):
        manage_css.inject()
        p = Product.get(p)
        kw['p'] = p.uid
        kw['name'] = p.name
        kw['sku'] = p.sku
        kw['price'] = p.price
        kw['nstock'] = p.stock
        kw['nshtime'] = p.shiptime
        kw['description'] = p.description

        return dict(title="Edit Product", form=edit_product_form, values=kw,
                    action=stroller_url('/manage/do_edit')) #, p=p.uid))
    
    @expose()
    @validate(edit_product_form, edit_product)
    def do_edit(self, **kw):
        p = Product.get(kw['p'])
        pi = DBSession.query(ProductInfo).filter_by(product_uid=p.uid).first()
        pi.name = kw['name']
        pi.description = kw['description']
        p.sku = kw['sku']
        p.price = kw['price']
        if isinstance(kw['photo'], cgi.FieldStorage):
            p.thumb = thumbnail(kw['photo'].file)
            kw['photo'].file.seek(0)
            p.photo = productimage(kw['photo'].file)
        p.stock = kw['nstock']
        p.shiptime = kw['nshtime']
        return redirect(stroller_url('/'))

    @expose()
    def featured_add(self, p):
        p = Product.get(p)
        dest = '/'
        if p:
            dest = stroller_url('/category', uid=p.category.uid)
            flash("Product marked as featured")
            p.featured = True

        return redirect(dest)
        
    @expose()
    def featured_del(self, p):
        p = Product.get(p)
        dest = '/'
        if p:
            dest = stroller_url('/category', uid=p.category.uid)
            flash("Product removed from featured")
            p.featured = False

        return redirect(dest)

    @expose()
    def front_add(self, c):
        p = Category.by_id(c)
        dest = stroller_url('/')
        if p:
            flash("Category marked as featured")
            p.featured = True

        return redirect(dest)
        
    @expose()
    def front_del(self, c):
        p = Category.by_id(c)
        dest = stroller_url('/')
        if p:
            flash("Category removed from featured")
            p.featured = False

        return redirect(dest)
         
    @expose('stroller.templates.manage.orderlist')
    def list_orders(self):
        unpaid_orders     = DBSession.query(Order).filter_by(payed=0).order_by(Order.uid)
        paid_orders       = DBSession.query(Order).filter_by(payed=1).filter_by(dispatched=0).order_by(Order.uid)
        dispatched_orders = DBSession.query(Order).filter_by(dispatched=1).order_by(Order.uid)
        return dict(unpaid_orders=unpaid_orders, paid_orders=paid_orders, dispatched_orders=dispatched_orders)

    @expose()
    def promote_order(self, uid):
        
        order = DBSession.query(Order).filter_by(uid=uid).first()
        if not order.payed:
            if not order.get_data('ship_name') or order.get_data('ship_name').value == '':
                flash("Missing shipping name in order "+str(order.uid)+" so it isn't promoted.")
            else:
                order.payed = True
        else:
            for p in order.items:
                if p.product.stock and p.product.stock > -1:
                    if p.product.stock < p.quantity:
                        flash("Didn't - Stock doesn't have enough quantity of item "+p.product.name)
                        return redirect(stroller_url('/manage/list_orders'))
            order.dispatched = True
            for p in order.items:
                if p.product.stock > -1:
                    if p.product.stock > p.quantity:
                        p.product.stock -= p.quantity
        return redirect(stroller_url('/manage/list_orders'))

    @expose()
    def demote_order(self, uid):
        order = DBSession.query(Order).filter_by(uid=uid).first()
        if order.dispatched:
            for p in order.items:
                if p.product.stock and p.product.stock > -1:
                    p.product.stock += p.quantity
            order.dispatched = False
        else:
            order.payed = False
        return redirect(stroller_url('/manage/list_orders'))

    @expose('stroller.templates.manage.ordershow')
    def show_order(self, uid):
        order = DBSession.query(Order).filter_by(uid=uid).first()
        return dict(order=order)

    
    @expose('stroller.templates.manage.orderedit')
    def edit_order(self, uid, **kw):
        order = DBSession.query(Order).filter_by(uid=uid).first()
        kw['fname'] = order.get_data_string('first_name')
        kw['lname'] = order.get_data_string('last_name')
        kw['email'] = order.get_data_string('email')
        kw['shname'] = order.get_data_string('ship_name')
        kw['shaddr'] = order.get_data_string('ship_address')
        kw['shzip'] = order.get_data_string('ship_zip')
        kw['shcity'] = order.get_data_string('ship_city')
        kw['shstate'] = order.get_data_string('ship_state')
        kw['shcountry'] = order.get_data_string('ship_country')
        return dict(values=kw, form=edit_order_form, order=order)
    
    @expose()
    def do_edit_order(self, uid, **kw):
        order = DBSession.query(Order).filter_by(uid=uid).first()
        order.set_data('first_name', kw['fname'])
        order.set_data('last_name', kw['lname'])
        order.set_data('email', kw['email'])
        order.set_data('ship_name', kw['shname'])
        order.set_data('ship_address', kw['shaddr'])
        order.set_data('ship_zip', kw['shzip'])
        order.set_data('ship_city', kw['shcity'])
        order.set_data('ship_state', kw['shstate'])
        order.set_data('ship_country', kw['shcountry'])
        return redirect(stroller_url('/manage/list_orders'))
