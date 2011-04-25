from zope.interface import Interface, Attribute
from zope import schema

from collective.imagetags import imagetagsMessageFactory as _

class IAddTag(Interface):
    """
    Form to add a new image tag
    """

    id = schema.TextLine(title=_(u"Id"),
                         required=False)
                         
    field = schema.Choice(title=_(u"Image field"),
                          description=_(u"Image field you want to add this tag"),
                          vocabulary='collective.imagetags.imagefields',
                          required=True)


    title = schema.TextLine(title=_(u"Title displayed in the tag"),
                            required=True)

    url = schema.URI(title=_(u"Link for the tag"),
                     required=False)

    x = schema.Float(title=_(u"X position"),
                     description=_(u"Position in the X axis of the center of the box (0-100%)"),
                     min=0.0,
                     max=100.0)

    y = schema.Float(title=_(u"Y position"),
                     description=_(u"Position in the Y axis of the center of the box (0-100%)"),
                     min=0.0,
                     max=100.0)
                     
class IImageTagsHelper(Interface):
    """
    imagetags-helper interface with helper methods for manage and image browser views
    """
    
    def image_fields():
        """ All the image fields available in current object """

    def image():
        """ The field to use with tags """
        
    def has_image_field():
        """ Has this content type an image field? """
        
    def plone_version():
        """ Returns major version number of Products.CMFPlone """
        

class IManageTags(Interface):
    """
    imagetags-manage view interface
    Tag management browser view
    """

    def get_tag(id, create_on_fail=True):
        """ Gets / creates a specific tag """

    def get_tags():
        """ Gets all the tags for the object """
        
    def get_sorted_tags():
        """ Sorted list of tags
        """
        
    def save_tag(data):
        """ Saves a tag with the passed data """
        
    def url():
        """ URL of the current view """
        
class IImageTagsImage(Interface):
    """
    imagetags-image view interface
    Used to display the tagged image (i.e., the image with all its tags)
    """
    
    embedded = Attribute("""The image is embedded inside another view or is this the manage view""")
    
    tags = Attribute("""A sorted list of tags""")
    
    default_image = Attribute("""Default image in case no specific image is defined""")
    
    iframes_enabled = Attribute("""iframes_enabled setting""")
    
    taglist_height = Attribute("""iframe_taglist_height setting""")
    
    def available_sizes(field_name):
        """ Available scale names for the given field in current object """

    def tag_box(data):
        """ A call to a page template file """

    def tag_title(id, data):
        """
        A call to a pagetemplate file
        """

    def portal_url():
        """ Returns portal_url """
        

