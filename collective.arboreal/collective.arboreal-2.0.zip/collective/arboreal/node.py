from Acquisition import aq_parent, aq_inner
from AccessControl import ClassSecurityInfo
from OFS.interfaces import IOrderedContainer
from OFS.OrderedFolder import OrderedFolder
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonStructuralFolder
from zope.component import getUtility
from zope.interface import implements

from config import ManageProperties


class Node(OrderedFolder):
    """A node in a tree. The node can contain its children"""

    implements(INonStructuralFolder, IOrderedContainer)
    meta_type = 'ArborealNode'
    security = ClassSecurityInfo()

    security.declareProtected(ManageProperties, 'setId')
    def setId(self, new_id):
        if new_id != self.getId():
            parent = aq_parent(aq_inner(self))
            old_id = self.getId()
            ob = parent[old_id]
            parent._delObject(old_id)
            ob._setId(new_id)
            parent._setObject(new_id, ob, set_owner=0)

    security.declarePublic("Title")
    def Title(self):
        """Return the node name."""
        return self.title
    
    security.declareProtected(ManageProperties, 'setTitle')
    def setTitle(self, title):
        """Set the title."""
        if not isinstance(title, unicode):
            title = title.decode(self._getCharset())
        self.title = title
    
    security.declareProtected(ManageProperties, 'addChild')
    def addChild(self, name, id=None):
        """Create a subnode of this node."""
        if not isinstance(name, unicode):
            name = name.decode(self._getCharset())
            
        if not id:
            # Generate a unique id based on the name of the node
            id = base = getUtility(IURLNormalizer).normalize(name)
            count = 1
            while id in self.objectIds():
                id = '%s-%d' % (base, count)
                count += 1
        node = Node(id)
        node.title = name
        self._setObject(id, node)
        return id
    
    security.declarePublic("getNodePath")
    def getNodePath(self):
        """Return the path of the node to the root of the tree."""
        current = self
        path = []
        while current.meta_type==self.meta_type:
            path.append(current.id)
            current = current.aq_parent
        path.reverse()
        return '/'+'/'.join(path)

    def _getCharset(self):
        properties = getToolByName(self, 'portal_properties', None)
        if properties is not None:
            site_properties = getattr(properties, 'site_properties', None)
            if site_properties is not None:
                return site_properties.getProperty('default_charset')
        return 'utf-8'       
