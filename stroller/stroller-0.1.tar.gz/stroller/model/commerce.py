
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import *
from sqlalchemy.orm import relation, synonym, backref

from stroller.model.core import DeclarativeBase, metadata, DBSession
from stroller.lib import language
from datetime import datetime

__all__ = ['Product', 'ProductInfo', 'Category', 'Order', 'OrderItem']

class ProductInfo(DeclarativeBase):
    __tablename__ = 'stroller_product_info'
    
    uid = Column(Integer, autoincrement=True, primary_key=True)
    lang = Column(Unicode(16), nullable=False)
    name = Column(Unicode(127), nullable=False)
    description = Column(Unicode(65535), nullable=False)  
    
    product_uid = Column(Integer, ForeignKey('stroller_product.uid'))
    product = relation('Product', backref=backref('info', cascade='all, delete-orphan'))
 
class Product(DeclarativeBase):
    __tablename__ = 'stroller_product'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    sku = Column(String(64), unique=True, nullable=False, index=True)
    price = Column(Numeric(scale=2), default=0)
    photo = Column(Binary(1024*1024), nullable=False)
    thumb = Column(Binary(255*1024), nullable=False)
    
    needs_shipping = Column(Boolean, default=0)
    featured = Column(Boolean, default=0)
    bought = Column(Integer, default=0, nullable=False)
    
    #Shipping time in number of days
    shiptime = Column(Integer)
    
    #None for non-stock items
    #int for stock-items
    stock = Column(Integer)

    category_uid = Column(Integer, ForeignKey('stroller_category.uid'))
    category = relation('Category', backref=backref('products'), uselist=False)
   
    @property
    def localized_info(self):
        langs = language()

        data = None
        for lang in langs:
            data = DBSession.query(ProductInfo).filter_by(product_uid=self.uid).filter_by(lang=lang).first()
            if data:
                return data
      
        if not data:
            data = DBSession.query(ProductInfo).filter_by(product_uid=self.uid).first()

        return data
    
    @property
    def name(self):
        return self.localized_info.name
        
    @property
    def description(self):
        return self.localized_info.description
    
    @property
    def ancestors(self):
        ancestor = self.category
        while ancestor:
            yield ancestor
            ancestor = ancestor.parent

    @staticmethod
    def get(uid):
        return DBSession.query(Product).filter_by(uid=uid).first()

class Category(DeclarativeBase):
    __tablename__ = 'stroller_category'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(99), default='unnamed')
    featured = Column(Boolean, default=0)
    icon = Column(Binary(1024*1024), nullable=True)
    show_subcategories = Column(Boolean, default=0)

    parent_uid = Column(Integer, ForeignKey('stroller_category.uid'))
    subcategories = relation('Category', backref=backref('parent', remote_side='Category.uid'))

    @property
    def ancestors(self):
        ancestor = self.parent
        while ancestor:
            yield ancestor
            ancestor = ancestor.parent
   
    @staticmethod
    def by_id(uid):
        return DBSession.query(Category).filter_by(uid=uid).first()
        
    @property
    def all_products(self):
        l = []
        l.extend(self.products)
        for cat in self.subcategories:
            l.extend(cat.all_products)
        return l

class Order(DeclarativeBase):
    __tablename__ = 'stroller_order'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(DateTime, default=datetime.now)
    payed = Column(Boolean, default=False)
    dispatched = Column(Boolean, default=False)

    @staticmethod
    def get(uid):
        return DBSession.query(Order).filter_by(uid=uid).first()

    @property
    def total_quantity(self):
        return sum((i.quantity for i in self.items))

    @property
    def total_price(self):
        return sum((i.total for i in self.items))
    
    @property
    def shiptime(self):
        s = 0
        for i in self.items:
            if i.product.shiptime > s:
                s = i.product.shiptime
        if s==0:
            return None
        return s

    def add_item(self, product, qnt=1):
        oi = DBSession.query(OrderItem).filter_by(order=self).filter_by(product=product).first()
        if not oi:
            oi = OrderItem(quantity=0, price=product.price, total=0, order=self, product=product)
            DBSession.add(oi)
        oi.quantity += qnt
        oi.total = oi.price * oi.quantity

    def set_data(self, name, value):
        data = self.get_data(name)
        if not data:
            data = OrderMetaData(order=self, name=name)
            DBSession.add(data)
        data.value = value

    def get_data(self, name):
        return DBSession.query(OrderMetaData).filter_by(order=self).filter_by(name=name).first()

    def get_data_string(self, name):
        data = self.get_data(name)
        if not data:
            return ''
        else:
            return data.value

class OrderItem(DeclarativeBase):
    __tablename__ = 'stroller_orderitem'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(scale=2), nullable=False)
    total = Column(Numeric(scale=2), nullable=False)

    order_uid = Column(Integer, ForeignKey('stroller_order.uid'))
    order = relation('Order', backref=backref('items', cascade='all, delete-orphan'), uselist=False)
    
    product_uid = Column(Integer, ForeignKey('stroller_product.uid'))
    product = relation('Product', backref=backref('orderitems', cascade='all, delete-orphan'), uselist=False)

class OrderMetaData(DeclarativeBase):
    __tablename__ = 'stroller_ordermetadata'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    value = Column(Unicode(2048), nullable=False)
    
    order_uid = Column(Integer, ForeignKey('stroller_order.uid'))
    order = relation('Order', backref=backref('meta', cascade='all, delete-orphan'), uselist=False)
