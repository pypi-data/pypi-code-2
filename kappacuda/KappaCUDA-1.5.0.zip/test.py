#!/usr/bin/env python

"""
test.py file for SWIG KappaCUDA

this file needs the TestModule and the cuda/matrixMUL* files
"""

import KappaCUDA

kappa = KappaCUDA.Kappa_Instance("","",0)
process = kappa.GetProcess(0,0);
filename = "k/modules.k"
process.ExecuteFile (filename);
kappa.WaitForAll();

