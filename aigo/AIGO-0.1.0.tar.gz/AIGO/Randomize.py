"""
Randomize.py

AIGO is a python library for
the Analysis and Inter-comparison of Gene Ontology functional annotations.
see (http://code.google.com/p/aigo).
        
Created by Michael Defoin-Platel on 21/02/2010.
Copyright (c) 2010. All rights reserved.

AIGO is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pylab import *

from random import shuffle
from itertools import groupby, repeat

from AIGO import logger, logFun
from AIGO import allAspect

class RandomizeFA(dict):
    """
    This class provides methods to compute randomize a functional annotations.
    """

    def __init__(self, **args):
        
        # set any keyword valued parameters
        for k,v in args.items():
            self.__dict__[k] = v

    @logFun("Computing permutation of functional annotations")
    def shuffleAnnotation(self, allFA, t=10):
        """
        This method randomly re-shuffle annotation accross annotation sets.
        The coherence of the annotation sets should change.
        The size might affected if two identical indentation are assinged one set
        The other stats should remain unchanged or be marginally affected.
        """
        
        for FA in allFA:

            logger.info("\t%s" % (FA.name))

            for aspect in allAspect:
                if aspect=='All_aspects_of_GO':
                    continue

                iterKeys=flatten([list(repeat(k,len(FA.GPtoGO[aspect][k]))) for k in FA.GPtoGO[aspect].keys()])
                iterValues=list(flatten(FA.GPtoGO[aspect].values()))
                shuffle(iterValues)

                GPtoGO, GOtoGP=dict(), dict()
                for k,v in groupby(iterValues, lambda x: iterKeys.next()):
                    GPtoGO[k]= set(v)

                    for go in GPtoGO[k]:
                        if not GOtoGP.has_key(go):
                            GOtoGP[go]=set()
                        GOtoGP[go].add(k)

                FA.GPtoGO[aspect]=GPtoGO
                FA.GOtoGP[aspect]=GOtoGP

    @logFun("Computing resampling of functional annotations")
    def sampleAnnotation(self, allFA):
        """
        This method randomly sample GO annotations  keep the size of annotation sets unchange.
        """

        for FA in allFA:

            logger.info("\t%s" % (FA.name))

            for aspect in allAspect:
                if aspect=='All_aspects_of_GO':
                    continue
                
                iterKeys=flatten([list(repeat(k,len(FA.GPtoGO[aspect][k]))) for k in FA.GPtoGO[aspect].keys()])
                nbValues=len(list(flatten(FA.GPtoGO[aspect].values())))
                allNodes=FA.G.get_NodesfromAspect(aspect)
                iterValues=take(allNodes, randint(0,len(allNodes), nbValues))

                GPtoGO, GOtoGP=dict(), dict()
                for k,v in groupby(iterValues, lambda x: iterKeys.next()):
                    GPtoGO[k]= set(v)

                    for go in GPtoGO[k]:
                        if not GOtoGP.has_key(go):
                            GOtoGP[go]=set()
                        GOtoGP[go].add(k)

                FA.GPtoGO[aspect]=GPtoGO
                FA.GOtoGP[aspect]=GOtoGP
