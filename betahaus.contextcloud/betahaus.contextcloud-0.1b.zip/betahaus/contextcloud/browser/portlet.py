from zope.formlib import form
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import IFolderish
from plone.app.portlets.portlets import base
from plone.memoize.view import memoize

from betahaus.contextcloud.interfaces import IContextCloud
from betahaus.contextcloud.interfaces import IContextCloudPortlet
from betahaus.contextcloud import ContextCloudMessageFactory as _


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    title = _(u"Context cloud portlet") #Title for the assignment page itself.
    implements(IContextCloudPortlet)

    def __init__(self, portlet_title=u'', catalog_index='Subject', layout='cloud', cloud_levels=5):
        self.portlet_title = portlet_title
        self.catalog_index = catalog_index
        self.layout = layout
        self.cloud_levels = cloud_levels


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('portlet.pt')

    @property
    def available(self):
        """ Should only be available if context is folder-like (I.e. IFolderish)
            and the method _tags produces some result.
        """
        if not IFolderish.providedBy(self.context):
            return False
        if self._tags(hash(self)):
            return True
        return False

    @memoize
    def _tags(self, key):
        """ The tag objects. Note that memoize is very important here, otherwise
            it will be run again and new objects will be created.
            Key must be a unique key for this instance during render - it doesn't
            fill any other function than making sure that memoize is unique per portlet.
        """
        return self._cloud.getResults(index=self.data.catalog_index)

    @property
    @memoize
    def _cloud(self):
        """ The tag cloud adapter. """
        return IContextCloud(self.context)

    def title(self):
        """ Portlet title """
        return self.data.portlet_title

    def getResults(self):
        if self.data.layout == 'cloud':
            return self._cloud.addCloud(self._tags(hash(self)), self.data.cloud_levels)
        return self._tags(hash(self))


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContextCloudPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContextCloudPortlet)
