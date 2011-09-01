from zope import interface
from zope import schema

class IUploadingCapable(interface.Interface):
    """Any container/object that is supported for uploading into.
    """

class IFlashUploadSettings(interface.Interface):
    completion_url = schema.TextLine(
        title=u'Completion URL',
        description=u'URL to redirect upon successful upload of files',
        required=True,
        default=u'flashupload')
    valid_types = schema.Text(
        title=u'Valid Portal Types',
        description=u'PloneFlashUpload ordinarily uses the content type '
                    u'registry tool to determine what type of content to '
                    u'create.  This list of portal types is the only ones '
                    u'it can choose from once it\'s asked the registry.  '
                    u'If the type the registry returns is not in this list, '
                    u'then the standard File type is used.',
        required=True,
        default=u'Image\nFile')
