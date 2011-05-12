from Products.Archetypes.public import BaseSchema, Schema
from Products.Archetypes.public import FileField
from Products.Archetypes.public import BaseContent, registerType

from Products.ExternalStorage.ExternalStorage import ExternalStorage

from Products.ExternalExample.config import PROJECTNAME

schema = BaseSchema + Schema((

    FileField('file_normal',
    ),

    FileField('file_external1',
        accessor = 'getFileExternal1',
        storage = ExternalStorage(
            prefix = 'files',
        ),
    ),

    FileField('file_external2',
        accessor = 'getFileExternal2',
        storage = ExternalStorage(
            prefix = 'files',
        ),
    ),

    FileField('file_external3',
        storage = ExternalStorage(
            prefix = 'misc',
        ),
    ),

))


class ComplexSample(BaseContent):

    """This is a complex sample to demonstrate ES features."""

    schema = schema

registerType(ComplexSample, PROJECTNAME)
