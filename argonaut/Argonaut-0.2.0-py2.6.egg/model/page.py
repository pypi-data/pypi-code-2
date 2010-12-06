"""The page model"""
from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer

from argonaut.model.meta import Base, Session

class Page(Base):
    __tablename__ = 'pages'

    id   = Column(Integer, primary_key=True)
    name = Column(Unicode(30), nullable=False)
    status = Column(Integer, default = 1)
    order = Column(Integer, unique=True, nullable=False)
    url = Column(Unicode(200), nullable=False)
    
    def __init__(self, id=None, name=None, status=None, order=None, url=None):
        self.id = id
        self.name = name
        self.status = status
        self.order = order
        self.url = url
    
    def __unicode__(self):
        return self.name
        
    def __repr__(self):
        return "<Page('%s','%s','%s','%s','%s')>" % (self.id,self.name,self.status,self.order,self.url)

    __str__ = __unicode__
    
def get_title(id):
    from argonaut.model.config import Config
    return str(Session.query(Page).get(id).name)+' ['+str(Session.query(Config).get('site_title').value)+']'
    
def generate_title(name):
    from argonaut.model.config import Config
    return name+' ['+str(Session.query(Config).get('site_title').value)+']' 
    
def get_name(id):
    return str(Session.query(Page).get(id).name)
    
def get_all():
    return Session.query(Page).order_by(Page.order).all()    
