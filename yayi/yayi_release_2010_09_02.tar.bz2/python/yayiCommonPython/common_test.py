#  -*- coding=UTF-8 -*-
#  -:- LICENCE -:- 
# Copyright Raffi Enficiaud 2007-2010
# 
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file ../../LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# 
#  -:- LICENCE -:- 
#

#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-
# export DYLD_LIBRARY_PATH=~/ThirdParties/install__Darwin_i386/lib/


import os, sys, unittest, tempfile
print 'ARGV', sys.argv

if(len(sys.argv) > 1):
  sys.path.insert(0, os.path.abspath(sys.argv[1]))
  print 'path', sys.path
  print 'current directory', os.path.abspath(os.curdir)
else:
  root_dir = os.path.join(os.path.split(__file__)[0], os.pardir, os.pardir, os.pardir, "Tmp")
  l = [i for i in os.listdir(root_dir) if i.find('YAYI_SVN') != -1].sort()
  sys.path.insert(0, l[-1])
import YayiCommonPython as YAC


test_data_path = os.path.abspath(os.path.join(os.path.split(__file__)[0], os.pardir, os.pardir, "coreTests", "yayiTestData"))

print 'Current build version is', YAC.current_build_version()

#print dir(YAC)
class CommonTypeTestCase(unittest.TestCase):

  def testType(self):
    t = YAC.type()
    t.s_type, t.c_type = YAC.s_double, YAC.c_3
    self.assert_(t == YAC.type(YAC.c_3, YAC.s_double), 'bad "type" equality :' + str(t) + " != " + str(YAC.type(YAC.c_scalar, YAC.s_double)))

  def testCoord(self):
    t = (1, -3, 5)
    self.assert_(YAC.Transpose(t) == (-1, 3, -5), 'bad transposition :' + str(YAC.Transpose(t)) + " != " + str( (-1, 3, -5)))
    # test sur les listes de coordonnées

  def testHyperrectangle(self):
    rect = YAC.HyperRectangle()
    #self.assert_(rect.Size == (), 'bad returned size' + str(rect.Size) + " != " + str(()))
    rect.Origin = (5, 7, 3)
    rect.SetSize((5, 2, 7))
    self.assert_(rect.Size == (5, 2, 7), 'bad returned size' + str(rect.Size) + " != " + str((5, 2, 7)))
    rect.Size = (5, 3, 7)
    self.assert_(rect.Size == (5, 3, 7), 'bad returned size' + str(rect.Size) + " != " + str((5, 3, 7)))
    print rect
    self.assert_(rect.Origin == (5, 7, 3), 'bad returned origin' + str(rect.Origin) + " != " + str((5, 7, 3)))
    print rect.upper_right
    
    self.assert_(rect.upper_right == (10, 10, 10), 'bad returned upper_right corner' + str(rect.upper_right) + " != " + str((10, 10, 10)))
    
    rect2 = YAC.HyperRectangle(rect)
    self.assert_(rect == rect2, 'hyperrectangles are not equal (should be)')
    self.assert_(rect2.Size == (5, 3, 7), 'bad returned size' + str(rect2.Size) + " != " + str((5, 3, 7)))
    
    self.assert_(rect2.IsInside((5,7,3)), 'pixel (5,7,3) is not inside')
    self.assert_(not rect.IsInside((0,7,3)), 'pixel (0,7,3) is inside')

    rect3 = YAC.HyperRectangle((5, 7, 3),(5, 3, 7))
    self.assert_(rect == rect3, 'hyperrectangles are not equal (should be)')
    for i in range(100):
      rect4 = YAC.HyperRectangle((5, 5, 3),(5, 3, 7))
      self.assert_(rect != rect4, 'hyperrectangles are equal (should not be)')


class GraphTestCase(unittest.TestCase):

  def test1(self):
    t = YAC.Graph()
    self.assert_(t.num_vertices() == 0, 'bad number of vertices: ' + str(t.num_vertices()) + " != 0")
    self.assert_(t.num_edges() == 0, 'bad number of edges: ' + str(t.num_edges()) + " != 0")
    self.assert_(not t.is_directed, 'the graph is directed while it should not be')

    i1 = t.add_vertex("toto1")
    self.assert_(t.num_vertices() == 1, 'bad number of vertices: ' + str(t.num_vertices()) + " != 1")
    self.assert_(t.num_edges() == 0, 'bad number of edges: ' + str(t.num_edges()) + " != 0")
    self.assert_(t.get_vertex_data(i1) == "toto1", 'bad data associated to vertex i1: ' + str(t.get_vertex_data(i1)) + " != toto1")
    #self.assert_(t.vertex_data(i1) == "toto1", 'bad data associated to vertex i1: ' + str(t.get_vertex_data(i1)) + " != toto1")
  
  
    i2 = t.add_vertex("toto2")
    self.assert_(t.num_vertices() == 2, 'bad number of vertices: ' + str(t.num_vertices()) + " != 2")
    self.assert_(t.num_edges() == 0, 'bad number of edges: ' + str(t.num_edges()) + " != 0")
    self.assert_(t.get_vertex_data(i1) == "toto1", 'bad data associated to vertex i1: ' + str(t.get_vertex_data(i1)) + " != toto1")
    #self.assert_(t.vertex_data(i1) == "toto1", 'bad data associated to vertex i1: ' + str(t.get_vertex_data(i1)) + " != toto1")
    self.assert_(t.get_vertex_data(i2) == "toto2", 'bad data associated to vertex i2: ' + str(t.get_vertex_data(i2)) + " != toto2")
    #self.assert_(t.vertex_data(i2) == "toto2", 'bad data associated to vertex i2: ' + str(t.get_vertex_data(i2)) + " != toto2")
    
    self.assert_(t.are_vertices_adjacent(i1, i2) == False, 'vertices i1 and i2 seem to be adjacent while they should not be')
    self.assert_(t.are_vertices_adjacent(i2, i1) == False, 'vertices i1 and i2 seem to be adjacent while they should not be')

    e1 = t.add_edge(i1, i2, 10)
    self.assert_(t.num_vertices() == 2, 'bad number of vertices: ' + str(t.num_vertices()) + " != 2")
    self.assert_(t.num_edges() == 1, 'bad number of edges: ' + str(t.num_edges()) + " != 1")
    self.assert_(t.get_edge_data(e1) == 10, 'bad data associated to edge e1: ' + str(t.get_edge_data(e1)) + " != 10")

    self.assert_(t.are_vertices_adjacent(i1, i2) == True, 'vertices i1 and i2 seem not to be adjacent while they should be')
    self.assert_(t.are_vertices_adjacent(i2, i1) == (not t.is_directed), 'vertices i1 and i2 should be adjacent if the graph is not directed')


def suite():
  suite = unittest.TestSuite()
  suite.addTest(CommonTypeTestCase('testType'))
  suite.addTest(CommonTypeTestCase('testCoord'))
  suite.addTest(CommonTypeTestCase('testHyperrectangle'))
  suite.addTest(GraphTestCase('test1'))
  return suite

if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
