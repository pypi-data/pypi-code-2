#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

# this module provides some basic functionality for generating labels from pyomo
# names, which often contain characters such as "[" and "]" (e.g., in my_var[1]).
# these characters generally cause issues with optimization input file formats,
# e.g., CPLEX LP files. the purpose of this module is to provide a simple remap
# function, that will satisfy broadly problematic symbols. if solver-specific 
# remaps are required, they should be handled either in a preprocessor or a solver
# plugin.

__all__ = ['label_from_name']

ignore = set(['"', "'", '`'])
remap = {}
# Remap as underscores
remap['-']='_'
remap['_']='_'
remap[' ']='_'
remap['(']='['
remap['{']='['
remap[')']=']'
remap['}']=']'
# Remap as Q+ASCII-Dec
remap['!']='_Q33_'
remap['#']='_Q35_'
remap['$']='_Q36_'
remap['%']='_Q37_'
remap['&']='_Q38_'
remap['*']='_Q42_'
remap['+']='_Q43_'
#remap[',']='_Q44_'
remap['.']='_Q46_'
remap['/']='_Q47_'
remap[';']='_Q59_'
remap['<']='_Q60_'
remap['=']='_Q61_'
remap['>']='_Q62_'
remap['?']='_Q63_'
remap['@']='_Q63_'
remap['\\']='_Q92_'
remap['^']='_Q94_'
remap['|']='_Q124_'
remap['~']='_Q126_'

def label_from_name(name):

   global ignore
   global remap

   if name is None:
      raise RuntimeError, "Illegal name=None supplied to label_from_name function"

   label=""
   for c in name:
      if c in remap:
         label += remap[c]
      elif not c in ignore:
         label += c
   return label
