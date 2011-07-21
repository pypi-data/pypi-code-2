from AccessControl import ClassSecurityInfo
from config import ManageProperties
from Globals import InitializeClass
from node import Node
from Products.Archetypes.utils import DisplayList

class TreeManager(Node):
    meta_type = 'TreeManager'
    
    security = ClassSecurityInfo()
    
    security.declareProtected(ManageProperties, 'getTreeList')
    def getTreeList(self):
        """Return a list containing the whole tree.

        Paths are represented by id's seperated with slashes."""
        return self.buildTreeList([], '', self)
    

    security.declareProtected(ManageProperties, 'buildTreeList')
    def buildTreeList(self, treeList, path, node):
        """Append the children of node to the displaylist as subnodes of path."""
        for (i, child) in node.objectItems():
            childPath = "/".join([path, str(i)])
            childLabel = child.title_or_id()
            treeList.append({'path':childPath, 'name':childLabel})
            self.buildTreeList(treeList, childPath, child)
        return treeList
    
    security.declareProtected(ManageProperties, 'addNodeAtPath')
    def addNodeAtPath(self, name, path, id=None):
        """Create a node at the specified path."""
        if not path:
            return self.addChild(name, id)
        else:
            return self.getNodeAtPath(path).addChild(name, id)
            
    security.declarePrivate('getNodeAtPath')
    def getNodeAtPath(self, path):
        """Return the node at path."""
        nodeIds = path.split("/")[1:]
        node = self
        for i in nodeIds:
            node = node[i]
        return node
            
    security.declarePublic('treeURL')
    def treeURL(self):
        """Return the absolute url for this tree."""
        return self.absolute_url()
            
    security.declarePrivate('getPathsWithName')
    def getPathsWithName(self, name):
        """Return the paths which match the given name."""
        return [node['path'] for node in self.getTreeList() if
                node['name']==name]

    security.declarePrivate('searchForPaths')
    def searchForPaths(self, query):
        query = query.lower()
        results = []
        for node in self.getTreeList():
            if not [p for p in query.split(' ') if
                    node['name'].lower().find(p)!=-1]:
                continue
            results.append(node['path'])
        return results

            
        
InitializeClass(TreeManager)
