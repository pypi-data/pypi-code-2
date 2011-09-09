"""Definition of the store content type
"""
from Products.Archetypes.public import DisplayList   	


from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from my315ok.store import storeMessageFactory as _
from my315ok.store.interfaces import Istore
from my315ok.store.config import PROJECTNAME

listockst = DisplayList ((
	(_(u'have goods'),_(u'yes')),
		(_(u'have not goods'),_(u'no')),
		))
storeSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.FloatField(
        'market_price',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Market price"),
            description=_(u"Market price"),
        ),
        required=True,
        validators=('isDecimal'),
    ),


    atapi.FloatField(
        'our_price',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"Our price"),
            description=_(u"Our price"),
        ),
        required=True,
        validators=('isDecimal'),
    ),


    atapi.StringField(
        'brand',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Goods brand"),
            description=_(u"the made factory of the goods"),
        ),
        required=True,
    ),


    atapi.StringField(
        'model',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"goods model"),
            description=_(u"goods model"),
        ),
        required=True,
    ),


    atapi.FloatField(
        'cash_gift',
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u"cash gift"),
            description=_(u"cash gift"),
        ),
        default=0.00,
        validators=('isDecimal'),
    ),


    atapi.StringField(
        'stock_status',
	vocabulary=listockst,
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"stock status"),
            description=_(u"stock status of the goods"),
        ),
        required=True,
        default=True,
    ),


    atapi.TextField(
        'details',
        searchable=True,
        default_output_type = 'text/x-html-safe',
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"more details"),
            description=_(u"a more details introduction of the goods"),
        ),
        required=True,
    ),


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

storeSchema['title'].storage = atapi.AnnotationStorage()
storeSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    storeSchema,
    folderish=True,
    moveDiscussion=False
)

try:
    
    from Products.PloneGetPaid.interfaces import IDonatableMarker
    from Products.PloneGetPaid.interfaces import IShippableMarker
    from getpaid.core.interfaces import IBuyableContent
    class BuyableContentAdapter(object):
        implements(IBuyableContent)

        def __init__(self, context):

            self.context = context

            self.price = context.getOur_price()

            self.product_code = context.getModel()
except:
	pass

class store(folder.ATFolder):
    """online store"""
    try:
    	from Products.PloneGetPaid.interfaces import IBuyableMarker
    	implements(Istore,IBuyableMarker)   	 	       
    except:
    	implements(Istore)   	
    meta_type = "store"
    schema = storeSchema
    _at_rename_after_creation = True
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    market_price = atapi.ATFieldProperty('market_price')

    our_price = atapi.ATFieldProperty('our_price')

    brand = atapi.ATFieldProperty('brand')

    model = atapi.ATFieldProperty('model')

    cash_gift = atapi.ATFieldProperty('cash_gift')

    stock_status = atapi.ATFieldProperty('stock_status')

    details = atapi.ATFieldProperty('details')


atapi.registerType(store, PROJECTNAME)
