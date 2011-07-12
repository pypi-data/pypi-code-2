"""
A binary tree example ported from an example found in the Korat source code.
"""

from collections import deque

import inputgen


class BinaryTree(object):

    def __init__(self):
        self.root = None
        self.size = 0

    def repOK(self):
        if not self.root:
            return self.size == 0
        # checks that tree has no cycle
        visited = set()
        visited.add(self.root)
        worklist = deque()
        worklist.append(self.root)
        while worklist:
            current = worklist.popleft()
            if current.left:
                if current.left in visited:
                    return False
                visited.add(current.left)
                worklist.append(current.left)
            if current.right:
                if current.right in visited:
                    return False
                visited.add(current.right)
                worklist.append(current.right)
        # checks that size is consistent
        return len(visited) == self.size


class Node(object):

    def __init__(self, left=None, right=None):
        """
        Create a Node object.  left and right are optional and should be Node
        objects themselves.
        """
        self.left = left
        self.right = right



class BinaryTreeExample(inputgen.TestCase):

    @staticmethod
    def repOK(factory):
        return factory.tree.repOK()

    @staticmethod
    def fin(num_nodes=5, max_size=4):
        f = inputgen.Factory()
        tree = f.create(BinaryTree)
        f.set('tree', tree)

        nodes = f.create(Node, num_nodes, none=True)
        nodes.set('left', nodes)
        nodes.set('right', nodes)

        tree.set('root', nodes)
        sizes = range(0, max_size + 1)
        tree.set('size', sizes, all=True)
        return f

    def run_method(self, obj):
        pass


if __name__ == "__main__":
    import unittest
    unittest.main()
