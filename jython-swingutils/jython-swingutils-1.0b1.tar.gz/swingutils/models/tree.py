from javax.swing.tree import TreeModel as TreeModelInterface, TreeNode
from javax.swing.event import EventListenerList, TreeModelListener


class ListTreeModel(TreeModelInterface):
    def __init__(self, root=None):
        self.root = root
        self._listenerList = EventListenerList()

    def getRoot(self):
        return self.root

    def getChild(self, parent, index):
        return parent[index]

    def getChildCount(self, parent):
        if not isinstance(parent, (list, tuple)):
            return 0
        return len(parent)

    def isLeaf(self, node):
        return not isinstance(node, (list, tuple))

    def valueForPathChanged(self, path, newValue):
        pass

    def getIndexOfChild(self, parent, child):
        try:
            return parent.index(child)
        except ValueError:
            return -1

    def addTreeModelListener(self, l):
        self._listenerList.add(l, TreeModelListener)

    def removeTreeModelListener(self, l):
        self._listenerList.remove(TreeModelListener, l)


class TreeNodeProxy(TreeNode):
    pass