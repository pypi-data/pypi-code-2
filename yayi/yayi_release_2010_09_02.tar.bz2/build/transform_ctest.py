#  -*- coding=UTF-8 -*-
#  -:- LICENCE -:- 
# Copyright Raffi Enficiaud 2007-2010
# 
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file ../LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# 
#  -:- LICENCE -:- 
#

import os, sys

depth = 2
subdirs_cmd = "subdirs("

current_path 	= os.path.realpath(os.path.split(__file__)[0])
#print current_path
parent_path   = current_path
replace_path	= ''

#print __file__
#print os.path.realpath(__file__)
#print os.path.realpath(os.path.curdir)

for i in range(depth):
  parent_path		= os.path.realpath(os.path.join(parent_path, os.path.pardir))
  replace_path += os.path.pardir + os.path.sep

#print 'replace', parent_path + os.path.sep, 'with', replace_path

def transform_file(filename):
  f = file(filename, "ra")
  lines = f.readlines()
  del f

  new_file = []

  for l in lines:
    s = l.replace(parent_path + os.path.sep, replace_path)
    #print s, l, s == l
    
    if (l == s) and (l.lower().find(subdirs_cmd) > -1):
      i = l.lower().find(subdirs_cmd)
      test = l[(i + len(subdirs_cmd)):l.find(")")]

      if(os.path.exists(test)):
        s = l[:len(subdirs_cmd)] + os.path.realpath(test) + l[l.rfind(")"):]
        s = s.replace(parent_path + os.path.sep, replace_path)
      
    new_file.append(s)

  f = file(filename + 'new', "w")
  f.writelines(new_file)
  f.close()


  print 'Transformation done'

if __name__ == '__main__':
  transform_file("CTestTestfile.cmake")