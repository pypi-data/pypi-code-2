'''
Provides Boundary and Layer classes.  To access them use:
  import openTMM as tmm
  tmm.Boundary # Boundary class
  tmm.Layer # layer class

Boundary class -- Performs low-level calculations associated with the transfer matrix method (TMM).
Layer class -- Performs high-level calculations such as computing the time-averaged 
               electric/magnetic energy density, the transverse component of the electric field,
               and the transmission and reflection coefficients.

For details, see Table 1 and 2 in A. J. Yuffa, J. A. Scales, Object-oriented electrodynamic transfer
matrix code with modern applications,  preprint submitted to Computer Physics Communications (CPC).
The preprint is distributed with the source code, see openTMMpreprint.pdf

If you want to access the modules where the two classes are implemented you must explicitly 
import them, i.e. :
  from openTMM.mods import boundary, layer

To test the two classes as described in the paper use:
  from openTMM.tests import main
  main.run()
'''
__version__ = '0.0.1'
from mods.boundary import Boundary
from mods.layer import Layer
del mods

