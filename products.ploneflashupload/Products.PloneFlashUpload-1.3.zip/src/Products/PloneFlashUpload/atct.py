from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from zope.component import adapts
from zope.filerepresentation.interfaces import IFileFactory
from zope.interface import implements
from zope.interface import Interface
from zope.i18n.interfaces import IUserPreferredCharsets

from Acquisition import aq_inner
from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS
from Products.CMFCore.utils import getToolByName

from Products.PloneFlashUpload.interfaces import IFlashUploadSettings
from Products.PloneFlashUpload.interfaces import IUploadingCapable


class UploadingCapableFileFactory(object):
    implements(IFileFactory)
    adapts(IUploadingCapable)

    DEFAULT_TYPE = 'File'

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data, request=None):
        context = aq_inner(self.context)
        ctr = getToolByName(context, 'content_type_registry')
        type_ = ctr.findTypeName(name, '', '') or self.DEFAULT_TYPE
        settings = PortalFlashUploadSettings(context)
        if type_ not in settings.valid_types:
            type_ = self.DEFAULT_TYPE

        if request is not None:
            try:
                encoding = IUserPreferredCharsets(request).\
                    getPreferredCharsets()[0]
            except IndexError:
                encoding = 'utf-8'
            name = name.decode(encoding)
            name = IUserPreferredFileNameNormalizer(request).normalize(name)
        name = self._findUniqueId(name)

        name = context.invokeFactory(type_, name, title=name)
        obj = context[name]
        obj.update_data(data, content_type)
        obj.processForm()
        return obj

    def _findUniqueId(self, name):
        """Find a unique id in this context.

        This is based on the given id, by appending -n, where n is a
        number between 1 and the constant
        RENAME_AFTER_CREATION_ATTEMPTS, set in
        Archetypes/config.py. If no id can be found, return None.

        Method is slightly adapted from Archetypes/BaseObject.py

        Most important changes:

        - Do not rename image.jpg to image.jpg-1 but image-1.jpg

        - If no good id can be found, just return the original id;
          that way the same errors happens as would without any
          renaming.
        """
        context = aq_inner(self.context)

        ids = context.objectIds()
        def valid_id(name):
            return name not in ids

        if valid_id(name):
            return name

        # 'image.name.gif'.rsplit('.', 1) -> ['image.name', 'gif']
        splitted = name.rsplit('.', 1)
        if len(splitted) == 1:
            splitted.append('')
        head, tail = splitted

        idx = 1
        while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
            if tail:
                new_id = '%s-%d.%s' % (head, idx, tail)
            else:
                new_id = '%s-%d' % (head, idx)
            if valid_id(new_id):
                return new_id
            idx += 1

        # Just return the id.
        return name


class PortalFlashUploadSettings(object):
    implements(IFlashUploadSettings)
    adapts(Interface)

    COMPLETION_PROPERTY = 'flashupload_completion_url'
    VALID_TYPES_PROPERTY = 'flashupload_valid_types'

    def __init__(self, context):
        pt = getToolByName(context, 'portal_properties')
        self.site_props = pt.site_properties

    def _get_completion_url(self):
        default = IFlashUploadSettings['completion_url'].default
        return self.site_props.getProperty(self.COMPLETION_PROPERTY, default)

    def _set_completion_url(self, v):
        if not self.site_props.hasProperty(self.COMPLETION_PROPERTY):
            self.site_props.manage_addProperty(self.COMPLETION_PROPERTY,
                                               v, 'string')
        else:
            kwargs = {self.COMPLETION_PROPERTY: v}
            self.site_props.manage_changeProperties(**kwargs)

    completion_url = property(_get_completion_url, _set_completion_url)

    def _get_valid_types(self):
        """Return the valid types as a tuple.

        Whether the property is a string or a tuple, it ought to be returned
        as a string.

        >>> class MockSomething:
        ...     _dict = {}
        ...     def getProperty(self, id, default):
        ...         return self._dict.get(id, default)
        ...     def hasProperty(self, id):
        ...         return id in self._dict.keys()
        ...     def manage_addProperty(self, id, value, type_):
        ...         self._dict[id] = tuple(value.split('\\n'))
        >>> portal = MockSomething()
        >>> class MockPortalTool:
        ...     def getPortalObject(self):
        ...         return portal
        >>> portal.portal_url = MockPortalTool()
        >>> portal.portal_properties = MockSomething()
        >>> portal.portal_properties.site_properties = MockSomething()
        >>> settings = PortalFlashUploadSettings(portal)

        When we set it, it should be stored as a string.
        >>> settings.valid_types = u"Reinout\\nvan\\nRees"
        >>> settings.valid_types
        u'Reinout\\nvan\\nRees'

        The default as passed by the interface is a string with \n,
        though. Ought to stay a string.

        >>> portal.portal_properties.site_properties._dict = {}
        >>> settings.valid_types
        u'Image\\nFile'

        """
        default = IFlashUploadSettings['valid_types'].default
        value = self.site_props.getProperty(self.VALID_TYPES_PROPERTY,
                                            default)
        if isinstance(value, tuple):
            value = '\n'.join(value)
        return value

    def _set_valid_types(self, v):
        if not self.site_props.hasProperty(self.VALID_TYPES_PROPERTY):
            self.site_props.manage_addProperty(self.VALID_TYPES_PROPERTY,
                                               v, 'lines')
        else:
            kwargs = {self.VALID_TYPES_PROPERTY: v}
            self.site_props.manage_changeProperties(**kwargs)

    valid_types = property(_get_valid_types, _set_valid_types)
