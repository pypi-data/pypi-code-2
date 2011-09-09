from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from my315ok.store import storeMessageFactory as _

class Istore(Interface):
    """online store"""
    
    # -*- schema definition goes here -*-
    market_price = schema.Float(
        title=_(u"Market price"), 
        required=True,
        description=_(u"Market price"),
    )

    our_price = schema.Float(
        title=_(u"Our price"), 
        required=True,
        description=_(u"Our price"),
    )

    brand = schema.TextLine(
        title=_(u"Goods brand"), 
        required=True,
        description=_(u"the made factory of the goods"),
    )

    model = schema.TextLine(
        title=_(u"goods model"), 
        required=True,
        description=_(u"goods model"),
    )

    cash_gift = schema.Float(
        title=_(u"cash gift"), 
        required=False,
        description=_(u"cash gift"),
    )

    stock_status = schema.Bool(
        title=_(u"stock status"), 
        required=True,
        description=_(u"stock status of the goods"),
    )

    details = schema.Text(
        title=_(u"more details"), 
        required=True,
        description=_(u"a more details introduction of the goods"),
    )

