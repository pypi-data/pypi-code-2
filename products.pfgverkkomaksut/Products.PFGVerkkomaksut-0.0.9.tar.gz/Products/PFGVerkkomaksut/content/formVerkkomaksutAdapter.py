"""An adapter content type for Verkkmaksut payment in Finland."""

__author__  = 'Taito Horiuchi <taito.horiuchi@abita.fi>'
__docformat__ = 'plaintext'

import md5
from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import DisplayList, registerType, Schema
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.public import RFC822Marshaller


from Products.ATContentTypes.content.document import finalizeATCTSchema

from Products.PloneFormGen.content.actionAdapter import (
    AnnotationStorage,
    FormActionAdapter,
    FormAdapterSchema,
    IntegerField,
    StringField,
    TextField,
    IntegerWidget,
    RichWidget,
    SelectionWidget,
    StringWidget,
    TextAreaWidget,
)
from Products.PloneFormGen.content.formMailerAdapter import FormMailerAdapter, formMailerAdapterSchema
from Products.PFGVerkkomaksut import PFGVerkkomaksutMessageFactory as _

def check_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

#PFGVerkkomaksutSchema = FormAdapterSchema.copy() + Schema((
PFGVerkkomaksutSchema = formMailerAdapterSchema + Schema((
    IntegerField(
        name='merchant_id',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
        widget=IntegerWidget(
            label=_(u'Merchant ID'),
            description=_(u'Please imput MERCHANT_ID here.'),
            maxlength=11,
        ),
        size=11,
        default=13466,
    ),

    StringField(
        name='merchant_authentication_code',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
            widget=StringWidget(
                label=_(u'Merchant Authentication Code'),
                description=_(u''),
                maxlength=32,
            ),
        default='6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ'
        ),

    IntegerField(
        name='next_order_number',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
        widget=IntegerWidget(
            label=_(u'Next Order Number'),
            description=_(u'Please imput the next order number here. The incremental numbers are used.'),
            maxlength=64,
        ),
        size=10,
        default=1,
    ),

    StringField(
        name='price_field',
        required=True,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        widget=SelectionWidget(
            label=_(u'Price Field'),
            description=_(u'Please select the price field.'),
        ),
        vocabulary='price_fields',
        enforceVocabulary=True,
    ),

    TextField('thanks_text',
              required=False,
              searchable=True,
#              primary=True,
              storage = AnnotationStorage(),
#              validators = ('isTidyHtmlWithCleanup',),
#              default_output_type = 'text/x-html-safe',
              widget = TextAreaWidget(
#              widget = RichWidget(
                        label = _(u'Thanks Text which will be displayed when payment is successful.'),
                        rows = 5,
              ),
    ),

#    TextField('thanks_text',
##        schemata='decoration',
#        required=False,
#        searchable=False,
#        primary=False,
#        validators = ('isTidyHtmlWithCleanup',),
##        default_content_type = zconf.ATDocument.default_content_type,
#        default_output_type = 'text/x-html-safe',
##        allowable_content_types = zconf.ATDocument.allowed_content_types,
#        widget = RichWidget(
#            label = "Thanks Text",
##            label_msgid = "label_thanksepilogue_text",
#            description = "Thanks Text which will be displayed when payment is successful.",
##            description_msgid = "help_thanksepilogue_text",
#            rows = 8,
#            i18n_domain = "pfg.verkkomaksut",
##            allow_file_upload = zconf.ATDocument.allow_document_upload,
#            ),
#        ),

#    TextField('text',
#              required=True,
#              searchable=True,
#              primary=True,
#              storage = AnnotationStorage(migrate=True),
#              validators = ('isTidyHtmlWithCleanup',),
#              #validators = ('isTidyHtml',),
#              default_content_type = zconf.ATDocument.default_content_type,
#              default_output_type = 'text/x-html-safe',
#              allowable_content_types = zconf.ATDocument.allowed_content_types,
#              widget = RichWidget(
#                        description = "",
#                        description_msgid = "help_body_text",
#                        label = "Body Text",
#                        label_msgid = "label_body_text",
#                        rows = 25,
#                        i18n_domain = "plone",
#                        allow_file_upload = zconf.ATDocument.allow_document_upload)),

    ),)

finalizeATCTSchema(PFGVerkkomaksutSchema)

class PFGVerkkomaksut(FormActionAdapter, FormMailerAdapter):
    """Verkkomaksut Payment Adapter"""

    # Standard content type setup
    portal_type = meta_type = 'PFGVerkkomaksut'
    archetype_name = 'Verkkomaksut Payment Adapter'
    schema = PFGVerkkomaksutSchema
    typeDescription = 'A document which can contain rich text, images and attachments'
    typeDescMsgId = 'PFGVerkkomaksut_description_edit'

    _at_rename_after_creation = True

    def canSetDefaultPage(self):
        return False

    def onSuccess(self, fields, REQUEST=None):
        field = self.selected_price_field()
        form = self.REQUEST.form
        price = form.get(field)
        MERCHANT_ID = str(self.getMerchant_id())
        AMOUNT = price
        order_number = self.getNext_order_number()
        ORDER_NUMBER = str(order_number)
        # Increase next_order_number by one.
        self.setNext_order_number(order_number + 1)
        ORDER_DESCRIPTION = 'Payment from PloneFormGen Verkkomaksut Adapter'
        CURRENCY = 'EUR'
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_url = portal.absolute_url()
        parent = aq_parent(self)
#        ids = parent.objectIds()
#        ids = [id for id in ids if id in form.keys()]
#        queries = ['&'+id+'='+form.get(id) for id in ids if form.get(id) is not None][1:]
#        query = '?'+ids[0]+'='+form.get(ids[0])+''.join(queries)
        parent_url = parent.absolute_url()
        return_url = '%s/verkkomaksut-thanks' % (self.absolute_url())
        cancel_url = '%s?portal_status_message=You have canceled'% parent_url
        notify_url = '%s/verkkomaksutnotify' % (self.absolute_url())
#        notify_url = '%s/verkkomaksutnotify%s' % (self.absolute_url(), query)
        RETURN_ADDRESS = return_url
        CANCEL_ADDRESS = cancel_url
        NOTIFY_ADDRESS = notify_url
        TYPE = 'S1'
        CULTURE = 'fi_FI'
        MODE = '1'

        ADAPTER_UID = self.UID()

        sdm = getToolByName(self, 'session_data_manager')
        session = sdm.getSessionData(create=True)

        m = md5.new()
        m.update(self.getMerchant_authentication_code())
        ## For TYPE S1
        m.update('|' + MERCHANT_ID)
        m.update('|' + AMOUNT)
        m.update('|' + ORDER_NUMBER)
        m.update('||' + ORDER_DESCRIPTION)
        m.update('|' + CURRENCY)
        m.update('|' + RETURN_ADDRESS)
        m.update('|' + CANCEL_ADDRESS)
        m.update('||' + NOTIFY_ADDRESS)
        m.update('|' + TYPE)
        m.update('|' + CULTURE)
        m.update('||' + MODE + '||')
        auth_code = m.hexdigest()
        AUTHCODE = auth_code.upper()

        value = dict(
            MERCHANT_ID = MERCHANT_ID,
            AMOUNT = AMOUNT,
            ORDER_NUMBER = ORDER_NUMBER,
            ORDER_DESCRIPTION = ORDER_DESCRIPTION,
            CURRENCY = CURRENCY,
            RETURN_ADDRESS = RETURN_ADDRESS,
            CANCEL_ADDRESS = CANCEL_ADDRESS,
            NOTIFY_ADDRESS = NOTIFY_ADDRESS,
            TYPE = TYPE,
            CULTURE = CULTURE,
            MODE = MODE,
            AUTHCODE = AUTHCODE,
            ADAPTER_UID = ADAPTER_UID,
        )

        session.set('pfg.verkkomaksut', value)
        res = [
            dict(
                title=field.Title(),
                description=form.get(field.getId()),
            ) for field in fields
        ]
#        for field in fields:
#            id = field.getId()
#            res.update({id:form.get(id)})
        session.set('pfg.verkkomaksut.fields', res)


        url = '%s/verkkomaksut' % parent_url
        return self.REQUEST.RESPONSE.redirect(url)

    def price_fields(self):
        dl = DisplayList()
        catalog = getToolByName(self, 'portal_catalog')
        path = '/'.join(aq_parent(self).getPhysicalPath())
        fixed_point_fields = catalog(
            portal_type=('FormFixedPointField',),
            path=dict(query=path, depth=1),
        )
        selection_fields = catalog(
            portal_type=('FormSelectionField', 'PFGSelectionStringField'),
            path=dict(query=path, depth=1),
        )
        fixed_point_fields = [(brain.getObject().UID(), brain.Title) for brain in fixed_point_fields if brain.getObject().getRequired()]
        selection_fields = [brain for brain in selection_fields if brain.getObject().getRequired()]
        for field in selection_fields:
            items = [item[:item.find('|')] for item in field.getObject().getFgVocabulary()]
            filtered_items = [item for item in items if check_float(item)]
            if items != filtered_items or len(items) == len(filtered_items) == 0:
                selection_fields.remove(field)
        selection_fields = [(brain.getObject().UID(), brain.Title) for brain in selection_fields]
        fields = fixed_point_fields + selection_fields
        for field in fields:
            dl.add(field[0], field[1])
        return dl

    def selected_price_field(self):
        uid = self.getPrice_field()
        reference_catalog = getToolByName(self, 'reference_catalog')
        obj = reference_catalog.lookupObject(uid)
        return obj.getId()

    def success(self):
        return 'AA'

registerType(PFGVerkkomaksut)
