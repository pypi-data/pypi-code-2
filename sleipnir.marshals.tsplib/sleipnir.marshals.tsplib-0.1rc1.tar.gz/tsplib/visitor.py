#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""A visitor (GOF94) for TSP Sections"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Add here required modules

# Sleipnir dependences
from sleipnir.core.visitor import Visitor

# Sleipnir tsp
from sleipnir.heuristics.sections import SectionTSP, SectionFactory

__all__ = ['HeaderVisitor', 'ContentVisitor']

# Local dependences


class TSPVisitor(Visitor):
    """
    A Visitor to unmarshal TSP header sections into TSPLIB compatible
    files
    """
    def visit_children(self, node, *args, **kwargs):
        """Visit node children if it's iterable"""
        for child in node:
            self.visit(child, *args, **kwargs)

    def visit_SectionTSP(self, node, *args, **kwargs):
        """write a SectionTSP file into stream"""
        # Process TSP comments
        self.visit_children(node.comments, *args, **kwargs)
        if len(node.comments):
            self.stream.write('\n')
        # Process headers
        self.visit_children(node.sections, *args, **kwargs)
        self.stream.write("EOF\n")
        # Process Section contents
        self.visit_children(node.contents, *args, **kwargs)
        self.stream.write("EOF")

    def visit_SectionComment(self, node, *args, **kwargs):
        """write a comment into file"""
        self.stream.write("# " + node.value + '\n')

    def visit_SectionHeader(self, node, *args, **kwargs):
        """Write a section type"""
        self.visit_children(node.comments, *args, **kwargs)
        self.stream.write(node.value + ": ")
        self.visit_children(node.values, *args, **kwargs)
        self.stream.write('\n')

    def visit_SectionValue(self, node, *args, **kwargs):
        """ Write a section value"""
        self.visit_children(node, *args, **kwargs)
        self.stream.write(node.value + '\n')

    def visit_SectionContent(self, node, *args, **kwargs):
        """Write a section type"""
        self.visit_children(node.comments, *args, **kwargs)
        self.stream.write(node.value + ":\n")
        self.visit_children(node.values, *args, **kwargs)
        self.stream.write('\n')
