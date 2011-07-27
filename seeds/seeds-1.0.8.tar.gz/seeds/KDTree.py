# -*- coding: utf-8 -*-
""" k-d tree implementation

In SEEDS, a k-d tree is used by Topologies to efficiently find nodes closest to
a given point.

Some inspiration provided by http://en.wikipedia.org/wiki/K-d_tree

"""

__author__ = "Brian Connelly <bdc@msu.edu>"
__credits__ = "Brian Connelly"

from util import square_distance, euclidean_distance


class KDTreeNode:
    """A KDTree is made up of KDTreeNode objects.  Each object represent a node
    on the tree.

    Properties:

    id
        A unique ID for this point (corresponds to node id)
    point
        A tuple containing the coordinates of the point
    left
        A pointer to the left subtree (KDTree)
    right
        A pointer to the right subtree (KDTree)

    """

    def __init__(self, id, point, left, right):
        """Initialize a KDTreeNode object.

        Parameters:

        *id*
            A unique ID for this point (corresponds to node id)
        *point*
            A tuple containing the coordinates of the point
        *left*
            A pointer to the left subtree (KDTree)
        *right*
            A pointer to the right subtree (KDTree)
        """

        self.id = id
        self.point = point
        self.left = left
        self.right = right

    def __str__(self):
        """Return a nice string when printed"""
        hasleft = self.left != None
        hasright = self.right != None
        return "KDTree Node [ID: %d][Point: %s][Left Child: %s][Right Subtree: %s]" % (self.id, self.point, hasleft, hasright)

    def is_leaf():
        """Return True if this is a leaf node (no children)"""
        return self.left == None and self.right == None

class KDTree:
    """A KDTree is tree of KDTreeNode objects.

    Properties:

    TODO

    """

    def __init__(self, points):
        def recursive_build(points, depth=0):
            if not points:
                return

            dimensions = len(points[0])
            sort_dim = depth % dimensions

            points.sort(key=lambda point: point[sort_dim])
            pivot = median = len(points) / 2

            return KDTreeNode(id=90210,
                              point=points[pivot],
                              left=recursive_build(points=points[:pivot], depth=depth+1),
                              right=recursive_build(points=points[pivot+1:], depth=depth+1))
        
        self.root = recursive_build(points)
        self.size = len(points)

    def num_nodes(self):
        return self.size

    def points(self):
        # TODO: function to get all points in tree
        pts = []
        return pts

    def add_node(self, node):
        #TODO
        pass

    def remove_node(self, node):
        #TODO
        pass

    def nearest_neighbors(self, point, n=1):
        if not point:
            return
        elif n > self.size:
            print "Error: Can not have more neighbors than there are points"

        print "Finding nearest neighbor for %s" % (point,)

        if self.root == None:
            return []

