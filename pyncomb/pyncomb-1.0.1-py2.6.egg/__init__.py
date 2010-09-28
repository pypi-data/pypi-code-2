#!/usr/bin/env python
#
# Copyright 2009 Sebastian Raaphorst.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The pyncomb (PYthoN COMBinatorics) library is a collection of
functions to work with basic combinatorial objects (e.g. permutations,
subsets, tuples), and provides algorithms for ranking, unranking, and
iterating over all objects in a specified class.

* combfuncs
     General functions independent of any other module, including a number
     of convenience routines to simplify working with the other modules.


ALL SUBSETS:
-----------
* subsetgc
     Operations over all subsets of a base set, using a minimal change
     order based on a binary-reflected Gray code.

* subsetlex
     Operations over all subsets of a base set, using lexicographic order.


K-SUBSETS:
---------
* ksubsetcolex
     Operations for k-subsets over a base set, using colex order.

* ksubsetlex
     Operations for k-subsets over a base set, using lexicographic order.

* ksubsetrevdoor
     Operations for k-subsets over a base set, using a minimal change
     revolving door order.


PERMUTATIONS:
------------
* permlex
     Operations for permutations over Sn, using lexicographic order.

* permtj
     Operations for permutations over Sn, using a minimal change order
     as per the Trotter-Johnson algorithm.


TUPLES:
------
* mbtuplelex
     Operations for tuples over mixed bases, using lexicographic order.
     Example: generate all tuples in [0,1,2]X['a','b']X[11,22,33,44].

* tuplelex
     Operations for tuples over a fixed base, using lexicographic order.
     Example: generate all 4-tuples over [0,1,2].

By Sebastian Raaphorst, 2009.

The algorithms herein are from:

Kreher, Donald and Stinson, Douglas. Combinatorial Algorithms: Generation,
   Enumeration, and Search. CRC Press, 1999.

I have tried to Pythonize them, but there is likely still considerable room
for improvement. Please e-mail all suggestions to srcoding@gmail.com, and they
will be incorporated in the next version of pyncomb."""

import combfuncs
import ksubsetcolex
import ksubsetlex
import ksubsetrevdoor
import mbtuplelex
import permlex
import permtj
import subsetgc
import subsetlex
