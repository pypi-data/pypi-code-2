"""A PFGExtendedMailAdapter content type for Products.PloneFormGen"""

__author__  = 'Taito Horiuchi <taito.horiuchi@abita.fi>'
__docformat__ = 'plaintext'

#import md5
from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from Acquisition import aq_inner,aq_parent

from Products.CMFCore.utils import getToolByName
#from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.public import (
    DisplayList,
    Schema,
)
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
#from Products.ATContentTypes.configuration import zconf
#from Products.Archetypes.public import RFC822Marshaller

from Products.ATContentTypes.content.document import finalizeATCTSchema

from Products.PloneFormGen.content.actionAdapter import (
    AnnotationStorage,
#    BooleanField,
#    IntegerField,
    LinesField,
#    StringField,
#    TextField,
#    BooleanWidget,
#    IntegerWidget,
#    LinesWidget,
    MultiSelectionWidget,
#    RichWidget,
#    SelectionWidget,
#    StringWidget,
)
from Products.PloneFormGen.content.formMailerAdapter import formMailerAdapterSchema, FormMailerAdapter
from Products.PloneFormGen import HAS_PLONE25, HAS_PLONE30
from Products.PloneFormGen.content.fieldsBase import BaseFormField

from Products.PFGExtendedMailAdapter import PFGExtendedMailAdapterMessageFactory as _
from Products.PFGExtendedMailAdapter.config import PROJECTNAME

def check_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

PFGExtendedMailAdapterSchema = ATFolderSchema.copy() + formMailerAdapterSchema.copy() + Schema((

    LinesField(
        name='msg_attachments',
        schemata='message',
        required=False,
        searchable=False,
        languageIndependent=True,
        storage=AnnotationStorage(),
        widget=MultiSelectionWidget(
            label=_(u'E-mail Attachments'),
            description=_(u'Please select the attachments to be sent with email when one has successfully finished inputs of the form.'),
            format='checkbox',
        ),
        vocabulary='attachments',
        enforceVocabulary=True,
    ),

    ),)

#PFGExtendedMailAdapterSchema.moveField('msg_necessary', pos='top')
#PFGExtendedMailAdapterSchema.moveField('body_pt', before='body_pre')
#PFGExtendedMailAdapterSchema['body_pt'].schemata='message'
#PFGExtendedMailAdapterSchema['body_pt'].required=False
#PFGExtendedMailAdapterSchema['msg_subject'].storage=AnnotationStorage()

#finalizeATCTSchema(PFGExtendedMailAdapterSchema)
finalizeATCTSchema(PFGExtendedMailAdapterSchema, folderish=True, moveDiscussion=False)

#class PFGExtendedMailAdapter(FormActionAdapter, FormMailerAdapter):
#class PFGExtendedMailAdapter(FormMailerAdapter):
class PFGExtendedMailAdapter(ATFolder, FormMailerAdapter):
#class PFGExtendedMailAdapter(FormMailerAdapter, ATFolder):
    """Extended Mail Adapter"""

    # Standard content type setup
    portal_type = meta_type = 'PFGExtendedMailAdapter'
    archetype_name = 'Extended Mail Adapter'
    schema = PFGExtendedMailAdapterSchema

    default_view = immediate_view = 'base_view'

    _at_rename_after_creation = True

    __implements__ = (ATFolder.__implements__, )


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
#            encoding = attachment[2]
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

#    def price_fields(self):
#        dl = DisplayList()
#        catalog = getToolByName(self, 'portal_catalog')
#        path = '/'.join(aq_parent(self).getPhysicalPath())
#        fixed_point_fields = catalog(
#            portal_type=('FormFixedPointField',),
#            path=dict(query=path, depth=1),
#        )
#        selection_fields = catalog(
#            portal_type=('FormSelectionField', 'PFGSelectionStringField'),
#            path=dict(query=path, depth=1),
#        )
#        fixed_point_fields = [(brain.getObject().UID(), brain.Title) for brain in fixed_point_fields if brain.getObject().getRequired()]
#        selection_fields = [brain for brain in selection_fields if brain.getObject().getRequired()]
#        for field in selection_fields:
#            items = [item[:item.find('|')] for item in field.getObject().getFgVocabulary()]
#            filtered_items = [item for item in items if check_float(item)]
#            if items != filtered_items or len(items) == len(filtered_items) == 0:
#                selection_fields.remove(field)
#        selection_fields = [(brain.getObject().UID(), brain.Title) for brain in selection_fields]
#        fields = fixed_point_fields + selection_fields
#        for field in fields:
#            dl.add(field[0], field[1])
#        return dl

#    def selected_price_field(self):
#        uid = self.getPrice_field()
#        reference_catalog = getToolByName(self, 'reference_catalog')
#        obj = reference_catalog.lookupObject(uid)
#        return obj.getId()

    def field_ids(self):
#        catalog = getToolByName(self, 'portal_catalog')
        parent = aq_parent(aq_inner(self))
        ids = [obj.id for obj in parent.contentValues() if isinstance(obj, BaseFormField)]
        return ids

#    def selectFieldsDisplayList(self):
#        """ returns display list of selection fields """

#        return self.fgFieldsDisplayList(
#            withNone=True, 
#            noneValue='#NONE#',
#            objTypes=(
#                'FormSelectionField',
#                'FormMultiSelectionField',
#                'FormStringField',
#                )
#            )

registerATCT(PFGExtendedMailAdapter, PROJECTNAME)
