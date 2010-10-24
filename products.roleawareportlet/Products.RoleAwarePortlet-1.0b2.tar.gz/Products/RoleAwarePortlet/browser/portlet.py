from Acquisition import aq_parent, aq_inner

from zope import schema
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlet.static import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from z3c.form.interfaces import INPUT_MODE
from z3c.form import form, field
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.namedfile.interfaces import HAVE_BLOBS
from plone.namedfile.field import NamedImage, NamedBlobImage
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

class IRoleAwarePortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    text = schema.Text(
        title=_(u"Text"),
        description=_(u"The text to render"),
        required=True)
    if HAVE_BLOBS:
        image = NamedBlobImage(
            title=_(u"Image"),
            description=_(u""),
            required=False)
    else:
        image = NamedImage(
            title=_(u"Image"),
            description=_(u""),
            required=False)

    link_text = schema.TextLine(
        title=_(u"Link text"),
        description=_(u"Text to be shown for the link"),
        required=False)

    link_url = schema.ASCIILine(
        title=_(u"Details link"),
        description=_(u"If given, the header and footer "
                       "will link to this URL."),
        required=False)

    show_roles = schema.Set(
        title=_(u"Show portlet for members having one of the following roles"),
        required=False,
        value_type=schema.Choice(source='roles'))

    block_roles = schema.Set(
        title=_(u"Hide portlet for members having one of the following roles"),
        required=False,
        value_type=schema.Choice(source='roles'))

class Assignment(base.Assignment):
    implements(IRoleAwarePortlet)

    header = _(u"title_role_aware_portlet", default=u"Role aware portlet")
    text = u""
    link_url = ''
    link_text = u""
    show_roles = []
    block_roles = []
    parent_uid = None

    def __init__(self, context_uid=None, header=u"", text=u"", image='', link_url='', link_text='', show_roles=[], block_roles=[]):
        self.header = header
        self.text = text
        self.image = image
        self.link_url = link_url
        self.link_text = link_text
        self.show_roles = show_roles
        self.block_roles = block_roles
        self.parent_uid = context_uid

    @property
    def title(self):
        return self.header


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')

    @property
    def available(self):
        member = getMultiAdapter((self.context, self.request), name=u'plone_portal_state').member()
        show = 1
        if self.data.show_roles:
            show = 0
            for r in self.data.show_roles:
                if member.has_role(r):
                    show = 1
                    break
        if self.data.block_roles and show:
            for r in self.data.block_roles:
                if member.has_role(r):
                    return 0
        return show
    
    @property
    def header(self):
        return self.data.header
    
    @property
    def text(self):
        return self.data.text

    @property
    def image(self):
        return self.data.image

    @property
    def tag(self):
        if bool(self.data.image):
            context = aq_inner(self.context)
            props = getToolByName(context, 'portal_properties').roleawareportlet_properties
            base = ''
            if self.data.parent_uid is None:
                base = getToolByName(context, 'portal_url')()
            else:
                reference_catalog = getToolByName(context, 'reference_catalog')
                obj = reference_catalog.lookupObject(self.data.parent_uid)
                if obj is not None:
                    base = obj.absolute_url()
            url = "%s/++contextportlets++%s/%s/@@image?w=%s&h=%s" % (base,
                                                                     self.manager.__name__,
                                                                     self.data.__name__,
                                                                     props.getProperty('thumbWidth', 128),
                                                                     props.getProperty('thumbHeight', 128))
            return '<img src="%s" alt="" class="image" />' % url
        return ''
    
    @property
    def link_url(self):
        if self.data.link_url.startswith('/'):
            return '%s%s' % (getMultiAdapter((self.context, self.request), name=u'plone_portal_state').portal_url(),
                             self.data.link_url)
        return self.data.link_url
    
    @property
    def link_text(self):
        return self.data.link_text
    
    @property
    def has_link(self):
        return bool(self.data.link_url)


class AddForm(form.AddForm):
    fields = field.Fields(IRoleAwarePortlet)
    fields['text'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
    fields['show_roles'].widgetFactory[INPUT_MODE] = CheckBoxFieldWidget
    fields['block_roles'].widgetFactory[INPUT_MODE] = CheckBoxFieldWidget
    label = _(u"title_add_role_aware_portlet",
              default=u"Add role aware portlet")
    description = _(u"description_role_aware_portlet",
                    default=u"A portlet whichs availability is role dependent.")

    def create(self, data):
        context = aq_parent(aq_inner(aq_parent(aq_inner(self.context))))
        context_uid = None
        if not IPloneSiteRoot.providedBy(context):
            context_uid = context.UID()
        return Assignment(context_uid, **data)

    def nextURL(self):
        referer = self.request.form.get('referer')
        if referer:
            return referer
        else:
            addview = aq_parent(aq_inner(self.context))
            context = aq_parent(aq_inner(addview))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            return url + '/@@manage-portlets'

    def add(self, object):
        ob = self.context.add(object)
        return ob


class EditForm(form.EditForm):
    fields = field.Fields(IRoleAwarePortlet)
    fields['text'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
    fields['show_roles'].widgetFactory[INPUT_MODE] = CheckBoxFieldWidget
    fields['block_roles'].widgetFactory[INPUT_MODE] = CheckBoxFieldWidget
    label = _(u"title_edit_role_aware_portlet",
              default=u"Edit role aware portlet")
    description = _(u"description_role_aware_portlet",
                    default=u"A portlet whichs availability is role dependent.")
    
    def applyChanges(self, data):
        self.request.response.redirect(self.nextURL())
        return super(EditForm, self).applyChanges(data)

    def nextURL(self):
        referer = self.request.form.get('referer')
        if referer:
            return referer
        else:
            addview = aq_parent(aq_inner(self.context))
            context = aq_parent(aq_inner(addview))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            return url + '/@@manage-portlets'
