from archetypes.schemaextender.field import ExtensionField
from raptus.multilanguagefields import fields

class StringField(ExtensionField, fields.StringField):
    """ StringField
    """

class LinesField(ExtensionField, fields.LinesField):
    """ LinesField
    """

class TextField(ExtensionField, fields.TextField):
    """ TextField
    """

class FileField(ExtensionField, fields.FileField):
    """ FileField
    """

class ImageField(ExtensionField, fields.ImageField):
    """ FileField
    """

try:
    class BlobField(ExtensionField, fields.BlobField):
        """ BlobField
        """
except:
    pass