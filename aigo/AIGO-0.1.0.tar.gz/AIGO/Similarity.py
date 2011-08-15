"""
Similarity.py

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

from AIGO import logger

def GOSet_Similarity(G, GO, metric="GS2", **kargs):
    """
    Calculates pairwise semantic similarity scores between GO terms in a given annotation set
    """
    
    if len(GO)<2:
        allD=list([1.])
    else:
        if metric=="GS2":
            allD=[ G.GS2([G.GOtoInt([g1]), G.GOtoInt([g2])])[0] for i,g1 in enumerate(GO) for j,g2 in enumerate(GO) if i <j ]
        elif metric=="CzekanowskiDice":
            allD=[ G.CzekanowskiDice(G.GOtoInt([g1]), G.GOtoInt([g2])) for i,g1 in enumerate(GO) for j,g2 in enumerate(GO) if i <j ]
        elif metric=="Resnik":
            allD=[ G.Resnik(G.GOtoInt([g1]), G.GOtoInt([g2]), kargs.get('IC', dict()))[0] for i,g1 in enumerate(GO) for j,g2 in enumerate(GO) if i <j ]
        else:
            logger.handleWarning ("Sorry, unknown semnatic similarity %s " % metric)
            allD=None

    return allD 
    

def GOSet_PWSimilarity(G, GO1, GO2, metric="GS2", **kargs):
    """
    Calculates pairwise semantic similarity scores between two given annotation sets
    """
    
    if metric=="GS2":
        sim, l=G.GS2([G.GOtoInt(GO1), G.GOtoInt(GO2)])
    elif metric=="CzekanowskiDice":
        sim = G.CzekanowskiDice(G.GOtoInt(GO1), G.GOtoInt(GO2))
        l=[sim,sim]
    elif metric=="Resnik":
        sim,l = G.Resnik(G.GOtoInt(GO1), G.GOtoInt(GO2), kargs.get('IC', dict()))
    else:
        logger.handleWarning ("Sorry, unknown semnatic similarity %s " % metric)
        sim,l=None,None
    
    return sim, l

def GO_Similarity(G, allGO, metric="GS2", **kargs):
    """
    Calculates pairwise semantic similarity scores in a list of annotation sets
    """
    
    if len(allGO)<2:
        sim=1.0
        l=[1.0]
    else:
        if metric=="GS2":
            sim,l=G.GS2( [G.GOtoInt(GO)  for GO in allGO ])
        elif metric=="CzekanowskiDice":
            allGO=[G.GOtoInt(GO)  for GO in allGO ]

            allD=dict()
            l=list()
            for i,GO1 in enumerate(allGO):
                foo=[allD.setdefault(sort([i,j])[0],dict()).setdefault(sort([i,j])[1], G.CzekanowskiDice(GO1, GO2)) for j,GO2 in enumerate(allGO) if not j==i]
                l.append(mean(foo))

            sim=mean(l)

        elif metric=="Resnik":
            allGO=[G.GOtoInt(GO)  for GO in allGO ]

            allD=dict()
            l=list()
            for i,GO1 in enumerate(allGO):
                foo=[allD.setdefault(sort([i,j])[0],dict()).setdefault(sort([i,j])[1], G.Resnik(GO1, GO2, kargs.get('IC', dict()))) for j,GO2 in enumerate(allGO) if not j==i]
                l.append(mean(foo))

            sim=mean(l)
            
        else:
            logger.handleWarning ("Sorry, unknown semnatic similarity %s " % metric)
            sim,l=None,None
    
    return sim,l
