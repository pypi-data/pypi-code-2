"""An adapter content type for Verkkmaksut payment in Finland."""

__author__  = 'Taito Horiuchi <taito.horiuchi@abita.fi>'
__docformat__ = 'plaintext'

import md5
from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from Acquisition import aq_inner,aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.public import (
#    ATFieldProperty,
    DisplayList,
    Schema,
#    registerType,
)
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.configuration import zconf
#from Products.Archetypes.public import RFC822Marshaller
from Products.statusmessages.interfaces import IStatusMessage

from Products.ATContentTypes.content.document import finalizeATCTSchema

from Products.PloneFormGen.content.actionAdapter import (
    AnnotationStorage,
#    FormActionAdapter,
#    FormAdapterSchema,
    BooleanField,
    IntegerField,
    LinesField,
    StringField,
    TextField,
    BooleanWidget,
    IntegerWidget,
    LinesWidget,
    MultiSelectionWidget,
    RichWidget,
    SelectionWidget,
    StringWidget,
#    TextAreaWidget,
)
from Products.PloneFormGen.content.formMailerAdapter import formMailerAdapterSchema, FormMailerAdapter
from Products.PloneFormGen import HAS_PLONE25, HAS_PLONE30
#from Products.PloneFormGen.interfaces import IPloneFormGenField
from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.thanksPage import FormThanksPage, ThanksPageSchema

from Products.PFGVerkkomaksut import PFGVerkkomaksutMessageFactory as _
from Products.PFGVerkkomaksut.config import PROJECTNAME

def check_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

PFGVerkkomaksutSchema = ATFolderSchema.copy() + formMailerAdapterSchema.copy() + ThanksPageSchema.copy() + Schema((

    BooleanField(
        name='msg_necessary',
        schemata='message',
        required=False,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        widget=BooleanWidget(
            label=_(u'Message Necessary'),
            description=_(u'If message after success of form input is necessary to send, please check this box.'),
        ),
    ),

    LinesField(
#        name='attachments_before_verkkomaksut',
        name='msg_attachments',
        schemata='message',
        required=False,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        widget=MultiSelectionWidget(
            label=_(u'E-mail attachments before Verkkomaksut'),
            description=_(u'Please select the attachments to be sent with email when one has successfully finished inputs of the form.'),
            format='checkbox',
        ),
        vocabulary='attachments',
        enforceVocabulary=True,
    ),

    IntegerField(
        name='merchant_id',
        schemata='verkkomaksut',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
        widget=IntegerWidget(
            label=_(u'Merchant ID'),
            description=_(u'Please input MERCHANT_ID provided by Verkkomaksut here. The default ID is for demo use which is 13466.'),
            maxlength=11,
        ),
        size=11,
        default=13466,
    ),

    StringField(
        name='merchant_authentication_code',
        schemata='verkkomaksut',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
            widget=StringWidget(
                label=_(u'Merchant Authentication Code'),
                description=_(u'Please input Merchant Authentication Code provided by Verkkomaksut here. The default ID is for demo use which is 6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ.'),
                maxlength=32,
            ),
        default='6pKF4jkv97zmqBJ3ZL8gUw5DfT2NMQ'
        ),

    IntegerField(
        name='next_order_number',
        schemata='verkkomaksut',
        required=True,
        searchable=False,
        storage=AnnotationStorage(),
        widget=IntegerWidget(
            label=_(u'Next Order Number'),
            description=_(u'Please input the next order number here. This number will be automatically increased by one for each transaction and will be sent to Verkkomksut.'),
            maxlength=64,
        ),
        size=10,
        default=1,
    ),

    StringField(
        name='price_field',
        schemata='verkkomaksut',
        required=True,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        widget=SelectionWidget(
            label=_(u'Price Field'),
            description=_(u'Please select the price field which will be used for Verkkomakusut. Remember to add fixed-point field or selection field with required option checked to the form folder first.'),
        ),
        vocabulary='price_fields',
        enforceVocabulary=True,
    ),

    LinesField(
        name='order_description',
        schemata='verkkomaksut',
        required=False,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        widget=LinesWidget(
            label=_(u'Order Description'),
            description=_(u'Please line up the ID of the field to be added to the ORDER_DESCRIPTION for verkkomaksut.'),
            cols=20,
        ),
        default_method='field_ids',
    ),

#    TextField(
#        name='thanks_text',
#        schemata='verkkomaksut',
#        required=False,
#        searchable=False,
#        storage = AnnotationStorage(),
#        primary=True,
#        validators = ('isTidyHtmlWithCleanup',),
#        default_output_type = 'text/x-html-safe',
##        widget = TextAreaWidget(
#        widget = RichWidget(
#            label = _(u'Thanks Text'),
#            description=_(u'This thanks text will be displayed when payment is successful.'),
#            rows = 25,
#            allow_file_upload = zconf.ATDocument.allow_document_upload,
#              ),
#    ),

    StringField(
        name='cancel_message',
        schemata='verkkomaksut',
        required=False,
        searchable=False,
        storage=AnnotationStorage(),
            widget=StringWidget(
                label=_(u'Cancel Message'),
                description=_(u'This message will be shown when one cancels Verkkomaksut payment.'),
                maxlength=255,
            ),
        ),

    ),)

PFGVerkkomaksutSchema.moveField('msg_necessary', pos='top')
PFGVerkkomaksutSchema.moveField('body_pt', before='body_pre')
PFGVerkkomaksutSchema['body_pt'].schemata='message'
PFGVerkkomaksutSchema['body_pt'].required=False
PFGVerkkomaksutSchema['thanksPrologue'].schemata='verkkomaksut'
PFGVerkkomaksutSchema['thanksPrologue'].widget.label=_(u'Thanks Text')
PFGVerkkomaksutSchema['thanksPrologue'].widget.description=_(u'This thanks text will be displayed when payment is successful.')
PFGVerkkomaksutSchema.moveField('thanksPrologue', before='cancel_message')


del PFGVerkkomaksutSchema['thanksEpilogue']
del PFGVerkkomaksutSchema['noSubmitMessage']

#finalizeATCTSchema(PFGVerkkomaksutSchema)
finalizeATCTSchema(PFGVerkkomaksutSchema, folderish=True, moveDiscussion=False)

#class PFGVerkkomaksut(FormActionAdapter, FormMailerAdapter):
#class PFGVerkkomaksut(FormMailerAdapter):
class PFGVerkkomaksut(ATFolder, FormMailerAdapter, FormThanksPage):
#class PFGVerkkomaksut(FormMailerAdapter, ATFolder):
    """Verkkomaksut Payment Adapter"""

    # Standard content type setup
    portal_type = meta_type = 'PFGVerkkomaksut'
    archetype_name = 'Verkkomaksut Payment Adapter'
    schema = PFGVerkkomaksutSchema
#    typeDescription = 'A document which can contain rich text, images and attachments'
#    typeDescMsgId = 'PFGVerkkomaksut_description_edit'

    default_view = immediate_view = 'base_view'

    _at_rename_after_creation = True

    __implements__ = (ATFolder.__implements__, )


#    merchant_id = ATFieldProperty('merchant_id')
#    merchant_authentication_code = ATFieldProperty('merchant_authentication_code')
#    next_order_number = ATFieldProperty('next_order_number')
#    price_field = ATFieldProperty('price_field')
#    thanks_text = ATFieldProperty('thanks_text')
#    cancel_message = ATFieldProperty('cancel_message')

    def canSetDefaultPage(self):
        return False

    def onSuccess(self, fields, REQUEST=None):
        order_number = self.getNext_order_number()
        ORDER_NUMBER = str(order_number)
        # Increase next_order_number by one.
        self.setNext_order_number(order_number + 1)
        REQUEST.set('ORDER_NUMBER', ORDER_NUMBER)
        if self.getMsg_necessary():
            self.send_form(fields, REQUEST)
        field = self.selected_price_field()
        form = self.REQUEST.form
        price = form.get(field)
        MERCHANT_ID = str(self.getMerchant_id())
        AMOUNT = price
        order_number = self.getNext_order_number()
        ORDER_NUMBER = str(order_number)
        # Increase next_order_number by one.
        self.setNext_order_number(order_number + 1)
        ORDER_DESCRIPTION = self.order_description(fields, REQUEST)
        CURRENCY = 'EUR'
#        portal = getToolByName(self, 'portal_url').getPortalObject()
#        portal_url = portal.absolute_url()
        parent = aq_parent(aq_inner(self))
#        ids = parent.objectIds()
#        ids = [id for id in ids if id in form.keys()]
#        queries = ['&'+id+'='+form.get(id) for id in ids if form.get(id) is not None][1:]
#        query = '?'+ids[0]+'='+form.get(ids[0])+''.join(queries)
        parent_url = parent.absolute_url()
        return_url = '%s/@@verkkomaksut-success' % (parent_url)
#        message = 'AAA'
#        IStatusMessage(REQUEST).addStatusMessage(message, type='info')
#        parent.plone_utils.addPortalMessage(_(u'AAA'))
#        cancel_url = '%s?portal_status_message=%s'%(parent_url, self.getCancel_message())
        cancel_url = '%s/@@verkkomaksut-canceled' %(self.absolute_url())
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
#        res = [
#            dict(
#                title=field.Title(),
#                description=form.get(field.getId()),
#            ) for field in fields
#        ]
##        for field in fields:
##            id = field.getId()
##            res.update({id:form.get(id)})
#        session.set('pfg.verkkomaksut.fields', res)
        session.set('pfg.verkkomaksut.fields', self.displayInputs(REQUEST))


        url = '%s/verkkomaksut' % parent_url
        return self.REQUEST.RESPONSE.redirect(url)

    def order_description(self, fields, REQUEST=None):
        self.displayInputs(REQUEST)
        values = [safe_unicode(item.get('value')) for item in self.displayInputs(REQUEST)]
#        form = self.REQUEST.form
#        values = [safe_unicode(form.get(key, '')) for key in self.getOrder_description()]
        res = u','.join(values)
#        res = safe_unicode(res)
#        return res[:65000]
        portal = getToolByName(self, 'portal_url').getPortalObject()
        charset = portal.getProperty('email_charset', 'utf-8')
        return res[:65000].encode(charset)


    def send_form(self, fields, request, **kwargs):
        """Send the form.
        """
        (headerinfo, additional_headers, body) = self.get_header_body_tuple(fields, request, **kwargs)
        if not isinstance(body, unicode):
            body = unicode(body, self._site_encoding())
        portal = getToolByName(self, 'portal_url').getPortalObject()
        email_charset = portal.getProperty('email_charset', 'utf-8')
        mime_text = MIMEText(body.encode(email_charset , 'replace'),
                _subtype=self.body_type or 'html', _charset=email_charset)

        attachments = self.get_attachments(fields, request)
        uids = self.getMsg_attachments()
        if uids:
            reference_catalog = getToolByName(self, 'reference_catalog')
            for uid in uids:
                obj = reference_catalog.lookupObject(uid)
                data = obj.data
                mimetype = obj.content_type
                filename = obj.getRawTitle()
                enc = None
                attachments.append((filename, mimetype, enc, data))

        if attachments:
            outer = MIMEMultipart()
            outer.attach(mime_text)
        else:
            outer = mime_text

        # write header
        for key, value in headerinfo.items():
            outer[key] = value

        # write additional header
        for a in additional_headers:
            key, value = a.split(':', 1)
            outer.add_header(key, value.strip())

        for attachment in attachments:
            filename = attachment[0]
            ctype = attachment[1]
            encoding = attachment[2]
            content = attachment[3]

            if ctype is None:
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1)

            if maintype == 'text':
                msg = MIMEText(content, _subtype=subtype)
            elif maintype == 'image':
                msg = MIMEImage(content, _subtype=subtype)
            elif maintype == 'audio':
                msg = MIMEAudio(content, _subtype=subtype)
            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(content)
                # Encode the payload using Base64
                Encoders.encode_base64(msg)

            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            outer.attach(msg)

        mailtext = outer.as_string()

        host = self.MailHost
        host.send(mailtext)


    def attachments(self):
        dl = DisplayList()
        catalog = getToolByName(self, 'portal_catalog')
        path = '/'.join(self.getPhysicalPath())
        brains = catalog(
            portal_type=('File','Image',),
            path=dict(query=path, depth=1),
        )
        for brain in brains:
            if HAS_PLONE25 and not HAS_PLONE30:
                dl.add(brain.getObject().UID(), brain.Title)
            if HAS_PLONE30:
                dl.add(brain.UID, brain.Title)
        return dl

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

    def field_ids(self):
        catalog = getToolByName(self, 'portal_catalog')
        parent = aq_parent(aq_inner(self))
        ids = [obj.id for obj in parent.contentValues() if isinstance(obj, BaseFormField)]
        return ids

#registerType(PFGVerkkomaksut)
registerATCT(PFGVerkkomaksut, PROJECTNAME)
