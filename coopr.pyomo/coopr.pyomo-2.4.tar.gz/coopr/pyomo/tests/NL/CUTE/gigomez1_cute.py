#  _________________________________________________________________________                                                                                \
#                                                                                                                                                           \
#  Coopr: A COmmon Optimization Python Repository                                                                                                           \
#  Copyright (c) 2010 Sandia Corporation.                                                                                                                   \
#  This software is distributed under the BSD License.                                                                                                      \
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,                                                                                   \
#  the U.S. Government retains certain rights in this software.                                                                                             \
#  For more information, see the Coopr README.txt file.                                                                                                     \
#  _________________________________________________________________________                                                                                \
                                                                                                                                                             
# Formulated in Pyomo by Carl D. Laird, Daniel P. Word, and Brandon C. Barrera                                                                
# Taken from:      

# AMPL Model by Hande Y. Benson
#
# Copyright (C) 2001 Princeton University
# All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that the copyright notice and this
# permission notice appear in all supporting documentation.                     

#   Source:
#   C. Gigola and S. Gomez,
#   "A Regularization Method for Solving the Finite Convex Min-Max Problem",
#   SINUM 27(6), pp. 1621-1634, 1990.

#   SIF input: Ph. Toint, August 1993.

#   classification LQR2-AN-3-3

from coopr.pyomo import *
model = Model()

var x{1..2} := 2.0;
var z:=2.0;

model.f = Objective(rule=f,sense=minimize)
minimize f:
	z;
subject to cons1:
	z+5.0*x[1]-x[2] >= 0;
subject to cons2:
	z-4*x[2]-x[1]^2-x[2]^2 >= 0;
subject to cons3:
	z-5*x[1]-x[2] >= 0;

solve;
display f;
display x;
display z;

