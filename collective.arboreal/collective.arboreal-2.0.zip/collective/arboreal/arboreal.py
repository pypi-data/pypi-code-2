from zope.interface import implements

from AccessControl import ClassSecurityInfo
from config import ManageProperties
from Globals import InitializeClass
from Products.Archetypes.utils import DisplayList
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.interfaces import INonStructuralFolder
from treemanager import TreeManager

class Arboreal(UniqueObject, BTreeFolder2):
    id = 'portal_arboreal'
    meta_type = 'Arboreal'
    
    implements(INonStructuralFolder)
    
    
    security = ClassSecurityInfo()
    
    def __init__(self):
        BTreeFolder2.__init__(self, id=self.id)
    
    security.declareProtected(ManageProperties, 'addTree')
    def addTree(self, id):
        """Add a tree node."""
        self._setOb(id, TreeManager(id))
        
    security.declareProtected(ManageProperties, 'delTree')
    def delTree(self, id):
        """ Delete a tree node. """
        self._delObject(id)

    security.declarePrivate('getTree')
    def getTree(self, id):
        """Return a contained tree, if the id does not exists create it."""
        tree = self.get(id)
        if tree is None:
            self.addTree(id)
            tree = self.get(id)
            assert tree is not None
        return tree

    security.declareProtected(ManageProperties, 'getTopLevelTreeNames')
    def getTopLevelTreeNames(self):
        " Get a list of the names of the toplevel trees "
        return [tree for tree in self.objectIds()]
    
    security.declarePrivate('getLabel')
    def getLabel(self, tree, path):
        """Return the label for the specific node at path within tree."""
        return self.getTree(tree).getNodeAtPath(path).Title()

    security.declarePrivate('getPathsWithName')
    def getPathsWithName(self, tree, name):
        """Return all node paths which match the given name."""
        return self.getTree(tree).getPathsWithName(name)
            

    security.declareProtected(ManageProperties, 'exportToXML')
    def exportToXML(self):
        """Export method """
        from utils import ArborealExporter
        exporter = ArborealExporter(self)
        return exporter.exportToXML()


    security.declareProtected(ManageProperties, 'delTrees')
    def delTrees(self):
        """Delete all tree managers."""
        for id in self.objectIds():
            self.delTree(id)

    security.declareProtected(ManageProperties, 'importFromXML')
    def importFromXML(self, preserve_ids=True):
        """Import from xml file arboreal.xml """
        from utils import ArborealImporter
        importer = ArborealImporter(self)
        self.delTrees()
        return importer.importFromXML()
            
            

InitializeClass(Arboreal)
