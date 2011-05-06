from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from interfaces import IESConfiguration

from OFS.SimpleItem import SimpleItem

class ESConfiguration(SimpleItem):
    implements(IESConfiguration)
    
    path = FieldProperty(IESConfiguration['path']) 

