from zope.interface import Interface
from zope.interface import Attribute
from zope import schema

from collective.customizablePersonalizeForm import CollectiveCustomizablePFMessageFactory as _

from plone.app.users.userdataschema import IUserDataSchema

from Products.CMFDefault.formlib.schema import FileUpload
from Products.PlonePAS.utils import scale_image

from OFS.Image import Image

class IExtendedUserDataSchema(Interface):

    def getSchema(self,):
        """ 
        """

class IExtendedUserDataPanel(Interface):
    
    def getProperties(self,):
        """
        """

class IExtendedUserDataWidgets(Interface):
    
    def getWidgets(self,):
        """
        """

def validateImage(value):
    return 'image' in value.headers.dict['content-type'] 

DefaultUserDataSchema = IUserDataSchema
DefaultUserDataSchema._InterfaceClass__attrs['portrait'].constraint = validateImage

class IExtendedUserDataSchema(DefaultUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """    

