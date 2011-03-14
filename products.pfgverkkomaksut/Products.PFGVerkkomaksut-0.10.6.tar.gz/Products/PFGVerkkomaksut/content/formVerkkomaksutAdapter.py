"""An adapter content type for Verkkmaksut payment in Finland."""

__author__  = 'Taito Horiuchi <taito.horiuchi@abita.fi>'
__docformat__ = 'plaintext'

try:
    import hashlib
except ImportError:
    import md5
import re
from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from Acquisition import aq_chain, aq_inner,aq_parent
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.public import (
    DisplayList,
    Schema,
)
from Products.CMFCore.permissions import ModifyPortalContent
#from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder

from Products.ATContentTypes.content.document import finalizeATCTSchema

from Products.PloneFormGen.content.actionAdapter import (
    ATFieldProperty,
    registerType,
    AnnotationStorage,
    BooleanField,
    IntegerField,
    LinesField,
    StringField,
    BooleanWidget,
    IntegerWidget,
    LinesWidget,
    MultiSelectionWidget,
    SelectionWidget,
    StringWidget,
)
from Products.PloneFormGen.content.formMailerAdapter import formMailerAdapterSchema, FormMailerAdapter
from Products.PloneFormGen.content.fieldsBase import BaseFormField
from Products.PloneFormGen.content.thanksPage import FormThanksPage, ThanksPageSchema
from Products.PFGVerkkomaksut import PFGVerkkomaksutMessageFactory as _
from Products.PFGVerkkomaksut.config import PROJECTNAME
from Products.PFGVerkkomaksut.interfaces import IPFGVerkkomaksut

def check_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

PFGVerkkomaksutSchema = ATFolderSchema.copy() + formMailerAdapterSchema.copy() + ThanksPageSchema.copy() + Schema((

    BooleanField(
        name='msg_necessary',
        schemata='message',
        required=False,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        read_permission=ModifyPortalContent,
        widget=BooleanWidget(
            label=_(u'Message Necessary'),
            description=_(u'If message after success of form input is necessary to send, please check this box.'),
        ),
    ),

    LinesField(
        name='msg_attachments',
        schemata='message',
        required=False,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        read_permission=ModifyPortalContent,
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
        read_permission=ModifyPortalContent,
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
        read_permission=ModifyPortalContent,
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
        read_permission=ModifyPortalContent,
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
        read_permission=ModifyPortalContent,
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
        read_permission=ModifyPortalContent,
        widget=LinesWidget(
            label=_(u'Order Description'),
            description=_(u'Please line up the ID of the field to be added to the ORDER_DESCRIPTION for verkkomaksut.'),
            cols=20,
        ),
        default_method='field_ids',
    ),

    StringField(
        name='cancel_message',
        schemata='verkkomaksut',
        required=False,
        searchable=False,
        storage=AnnotationStorage(),
        read_permission=ModifyPortalContent,
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

finalizeATCTSchema(PFGVerkkomaksutSchema, folderish=True, moveDiscussion=False)

class PFGVerkkomaksut(ATFolder, FormMailerAdapter, FormThanksPage):
    """Verkkomaksut Payment Adapter"""

    portal_type = 'PFGVerkkomaksut'
    schema = PFGVerkkomaksutSchema
    _at_rename_after_creation = True
#    __implements__ = (ATFolder.__implements__, )
    implements(IPFGVerkkomaksut)

    next_order_number = ATFieldProperty('next_order_number')
    merchant_id = ATFieldProperty('merchant_id')
    price_field = ATFieldProperty('price_field')
    merchant_authentication_code = ATFieldProperty('merchant_authentication_code')
    cancel_message = ATFieldProperty('cancel_message')

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
        notify_url = '%s/@@verkkomaksut-notify' % (self.absolute_url())
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

#        m = md5.new()
        try:
            m = hashlib.md5()
        except:
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
        session.set('pfg.verkkomaksut.fields', self.displayInputs(REQUEST))


        url = '%s/verkkomaksut' % parent_url
        return self.REQUEST.RESPONSE.redirect(url)

    def order_description(self, fields, REQUEST=None):
        folder = aq_parent(self)
        obj_ids = [obj.id for obj in folder.contentValues() if isinstance(obj, BaseFormField)]
        ids = [id for id in self.getOrder_description() if id in obj_ids]
        labels = [folder[id].Title() for id in ids]
        items = {}
        for item in self.displayInputs(REQUEST):
            items.update({item.get('label'):item.get('value')})
        if len(items) == 0:
            return ''
        else:
            values = [safe_unicode(items.get(label)) for label in labels if items.get(label) is not None and items.get(label) != '']
            res = u','.join(values)
            res = remove_html_tags(res)
            res = res.replace('\r', ',')
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
#            if HAS_PLONE25 and not HAS_PLONE30:
#                dl.add(brain.getObject().UID(), brain.Title)
#            if HAS_PLONE30:
#                dl.add(brain.UID, brain.Title)
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
                selection_fields = [sf for sf in selection_fields if sf.id != field.id]
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
        folder = [obj for obj in aq_chain(aq_inner(self)) if hasattr(obj, 'portal_type') and obj.portal_type == 'FormFolder'][0]
        ids = [obj.id for obj in folder.contentValues() if isinstance(obj, BaseFormField)]
        return ids

#registerATCT(PFGVerkkomaksut, PROJECTNAME)
registerType(PFGVerkkomaksut, PROJECTNAME)
