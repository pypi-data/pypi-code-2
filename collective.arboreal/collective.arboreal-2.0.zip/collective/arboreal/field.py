from ExtensionClass import Base
from Products.Archetypes.Field import LinesField, Field, StringField
from Products.Archetypes.Field import ObjectField, encode, decode
from Products.Archetypes import config
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from types import StringType, UnicodeType, StringTypes
from Products.Archetypes.Registry import registerField

from Acquisition import aq_parent
from Acquisition import aq_inner

from treemanager import TreeManager

STRING_TYPES = [StringType, UnicodeType]

class ArborealField(Base):
    security = ClassSecurityInfo()

    def displayName(self, content_instance, fieldValue):
        """Return the label for a value"""
        return self._getArboreal(content_instance).getLabel(self.tree, fieldValue)

    def treeList(self, content_instance):
        """Return a list of the linked tree"""
        return self.getTree(content_instance).getTreeList()

    def _getArboreal(self, content_instance):
        return getToolByName(content_instance, 'portal_arboreal')

    def getTree(self, content_instance):
        """Return an Arboreal tree object."""
        # tree attribute can be a method
        # on parent
        parent = aq_parent(aq_inner(self))
        method = getattr(parent, self.tree, None)
        if callable(method):
            tree = method()
            if not tree:
                return TreeManager()
        else:
            tree  = self.tree
        return self._getArboreal(content_instance).getTree(tree)


class MultiArborealField(ArborealField, LinesField):
    _properties = LinesField._properties.copy()
    _properties.update({
        'storeCompletePath': False,
        'storeOnlyLeaves': False,
        'tree': ''
    })
    del _properties['vocabulary']

    security = ClassSecurityInfo()

    def __init__(self, name, **kwargs):
        """Make sure we get a tree name."""
        LinesField.__init__(self, name, **kwargs)
        if not self.tree:
            raise KeyError('Arboreal fields need a tree argument')

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        If passed-in value is a string, split at line breaks and
        remove leading and trailing white space before storing in object
        with rest of properties.

        When 'storeCompletePath' is set the field will store all parent path
        segements.
        """
        __traceback_info__ = value, type(value)
        if type(value) in STRING_TYPES:
            value =  value.split('\n')
        value = [decode(v.strip(), instance, **kwargs)
                 for v in value if v and v.strip()]

        # Expand tree
        if self.storeCompletePath:
            pathDict = dict([(item, True) for item in value])
            for val in value:
                pathSections = val.split('/')
                currentPath = ''
                for path in pathSections:
                    currentPath = "/".join([currentPath, path])
                    pathDict[currentPath] = True
            value = [item[1:] for item in pathDict.keys() if item[1:]] # Strip of leading .

        if self.storeOnlyLeaves:
            result = set()
            for v in value:
                if '/' in v:
                    v = v.split('/')[-1]
                result.add(v)
            value = list(result)

        if config.ZOPE_LINES_IS_TUPLE_TYPE:
            value = tuple(value)
        ObjectField.set(self, instance, value, **kwargs)

    def treeList(self, content_instance):
        tree = self.getTree(content_instance).getTreeList()
        if self.storeOnlyLeaves:
            value = self.get(content_instance)
            for t in tree:
                leave = t['path'].split('/')[-1]
                if leave in value:
                    t['selected'] = True
                else:
                    t['selected'] = False
        else:
            for t in tree:
                t['selected'] = True
        return tree


class SingleArborealField(ArborealField, StringField):
    _properties = StringField._properties.copy()
    del _properties['vocabulary']

    def __init__(self, name, **kwargs):
        """Make sure we get a tree name."""
        StringField.__init__(self, name, **kwargs)
        if not self.tree:
            raise KeyError('Arboreal fields need a tree argument')

class ArborealLabledField(ObjectField, ArborealField):
    _properties = ObjectField._properties.copy()
    _properties.update({
        'tree':'',
        'type' : 'arboreallabled',
    })

    security  = ClassSecurityInfo()

    def __init__(self, name=None, **kwargs):
        """Make sure we get a tree name."""
        ObjectField.__init__(self, name, **kwargs)
        if not self.tree:
            raise KeyError('Arboreal fields need a tree argument')

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        try:
            path, value = ObjectField.get(self, instance, **kwargs)
        except (TypeError, ValueError): # No value set yet
            return ('','')
        return path, encode(value, instance, **kwargs)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        kwargs['field']=self
        try:
            path, string_value = value
        except TypeError:
            path, string_value = '',''
        if not hasattr(path, 'split'):
            path = '/'.join(path)
        string_value = decode(string_value, instance, **kwargs)
        self.getStorage(instance).set(
            self.getName(), instance, (path, string_value), **kwargs)



registerField(MultiArborealField,
              title='MultiArborealField',
              description=('Used for storing multiple Arboreal paths.')
             )

registerField(SingleArborealField,
              title='SingleArborealField',
              description=('Used for storing an Arboreal path.')
             )

registerField(ArborealLabledField,
              title='ArborealLabledField',
              description=(
                  'Used for storing an Arboreal path and a piece of text.')
             )
