import basemodel
import metamodel
import dynamicmeta
import datasources
import properties

from basemodel import SubscribableModel
from properties import Property, SingleChoice, Color, Color4, Vector2, Vector3, Vector4, Link, Password, File
from datasources import DataSource, Folder
from meta import ClassRegistry

class TestClass(SubscribableModel):
    name = Property(str, 'name')
    testprop = Property(str, '')
    testprop2 = Property(str, '')



