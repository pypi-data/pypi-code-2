#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

"""
Define the default COLIN point type
"""

__all__ = ['MixedIntVars']

import re
import xml.dom.minidom
from pyutilib.misc import get_xml_text


class MixedIntVars(object):
    """
    A class that defines a commonly used domain type.
    """

    def __init__(self, node=None):
        self.reals = []
        self.ints = []
        self.bits = []
        if node is not None:
            self.process(node)

    def display(self):
        print "Reals",
        for val in self.reals:
            print val,
        print ""
        print "Integers",
        for val in self.ints:
            print val,
        print ""
        print "Binary",
        for val in self.bits:
            print val,
        print ""

    def process(self,node):
        for child in node.childNodes:
            if child.nodeType == node.ELEMENT_NODE:
                child_text = get_xml_text(child)
                if child_text == "":
                    continue
                if child.nodeName == "Real":
                    for val in re.split('[\t ]+',child_text):
                        self.reals.append(1.0*eval(val))
                elif child.nodeName == "Integer":
                    for val in re.split('[\t ]+',child_text):
                        self.ints.append(eval(val))
                elif child.nodeName == "Binary":
                    for val in child_text:
                        if val == '1':
                            self.bits.append(1)
                        elif val == '0':
                            self.bits.append(0)
        return self

        
