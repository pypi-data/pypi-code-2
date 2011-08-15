"""
Compare.py

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

from itertools import combinations


from AIGO import allAspect, logger, logFun
from AIGO.Similarity import GOSet_PWSimilarity

class CompareFA(dict):
    """
    This class provides methods to compare several functional annotations.
    """

    def __init__(self, **args):
            
        # set any keyword valued parameters
        for k,v in args.items():
            self[k] = v

    def getCommonGene(self, FA1, FA2, aspect):
        """
        Return the set of gene products commonly annotated by FA1 and FA2 with respect to a given aspect of GO
        """
        if aspect == "All_aspects_of_GO":
            commonGene=set()
            for a in allAspect:
                if a == "All_aspects_of_GO":
                    continue
                commonGene= commonGene  | set(FA1.GPtoGO[a].keys()).intersection(FA2.GPtoGO[a].keys())
        else:
            commonGene=set(FA1.GPtoGO[aspect].keys()).intersection(FA2.GPtoGO[aspect].keys())
        
        return commonGene

    @logFun("Computing Venn Diagrams")
    def venn2(self, allFA):
        venn = dict()
        for aspect in allAspect:

            venn[aspect]=dict()

            for FA in allFA:
                if aspect=="All_aspects_of_GO":
                    venn[aspect][FA.name]=FA['GA']
                else:
                    venn[aspect][FA.name]=set(FA.GPtoGO[aspect].keys())

        self['venn2'] = venn


    @logFun("Computing Venn Diagrams")
    def venn(self, allFA):
        """
        Compute a N-dimensional venn diagramm between the N FAs
        """
        venn = dict()
        for aspect in allAspect:

            venn[aspect]=dict()

            S=dict()
            for FA in allFA:
                if aspect=="All_aspects_of_GO":
                    S[FA.name]=FA['GA']
                else:
                    S[FA.name]=set(FA.GPtoGO[aspect].keys())

            for i in arange(1, pow(2,len(allFA))):
                n=list()
                pl=list()
                nl=list()
                
                for j,FA in enumerate(allFA):
                    b=int(i)>> j & int(1)
                    if b:
                        n.append(FA.name)
                        pl.append(S[FA.name])
                    else:
                        nl.append(S[FA.name])
                    

                if len(pl)==0:
                    Pl=set()
                else:
                    Pl=reduce(lambda x,y: x.intersection(y), pl)

                if len(nl)==0:
                    Nl=set()
                else:
                    Nl=reduce(lambda x,y: x.union(y), nl)

                venn[aspect]['@'.join(sorted(n))]=100.0 * len(Pl.difference(Nl)) / len(allFA[0].refSet)

        self['venn'] = venn


    @logFun("Computing Functional Similarity")        
    def funcSim(self, allFA):                
        """
        Compute Semantic Similarity between commonly annotated GP for all possible pairs of FA
        """
        
        funcSim=dict()
        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue
            
            funcSim[aspect]=dict()

            for twoFAs in combinations(allFA, 2):

                #Order the two FAs
                FA1,FA2=take(twoFAs,argsort([FA.name for FA in twoFAs]))
                
                logger.info("\tbetween %s and %s for %s" % (FA1.name, FA2.name, aspect))

                commonGene=self.getCommonGene(FA1, FA2, aspect)
                
                D=dict()
                for g in commonGene:
                    sim,l=GOSet_PWSimilarity(FA1.G, FA1.GPtoGO[aspect][g], FA2.GPtoGO[aspect][g])
                    D[g]=(l[0],l[1])

                funcSim[aspect][(FA1.name, FA2.name)] = D

        aspect="All_aspects_of_GO"

        funcSim[aspect]=dict()
        for twoFAs in combinations(allFA, 2):

            #Order the two FAs
            FA1,FA2=take(twoFAs,argsort([FA.name for FA in twoFAs]))

            logger.info("\tbetween %s and %s for %s" % (FA1.name, FA2.name, aspect))
                
            commonGene=self.getCommonGene(FA1, FA2, aspect)

            D=dict()
            for g in commonGene:
                D1=mean([ funcSim[a][(FA1.name, FA2.name)][g][0]  for a in allAspect if not a=="All_aspects_of_GO" if  funcSim[a][(FA1.name, FA2.name)].has_key(g) ])
                D2=mean([ funcSim[a][(FA1.name, FA2.name)][g][1]  for a in allAspect if not a=="All_aspects_of_GO" if  funcSim[a][(FA1.name, FA2.name)].has_key(g) ])
                D[g]=(D1,D2)
            
            funcSim[aspect][(FA1.name, FA2.name)] = D

        self['funcSim'] = funcSim


    @logFun("Computing Verspoor et al. (2006) hierarchical precision")
    def precision(self, allFA):
        """
        Verspoor et al. (2006) hierarchical precision
        """

        #The first FA is used as a Gold Standard
        GS=allFA[0]
        
        precision=dict()
        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue

            precision[aspect] = dict()
            for FA in allFA[1:]:
                precision[aspect][(FA.name, GS.name)]=dict()

                logger.info("\t%s vs %s for %s" % (FA.name, GS.name, aspect))

                commonGene=self.getCommonGene(FA, GS, aspect)
                for g in commonGene:
                    r=list()
                    for go in FA.GPtoGO[aspect][g]:
                        aGO = set(FA.G.get_Ancestors(go))
                        naGO = len(aGO)

                        maxSim = max([(1.0 * len(aGO.intersection(GS.G.get_Ancestors(gs))))/naGO for gs in GS.GPtoGO[aspect][g]])
                        r.append(maxSim)

                    precision[aspect][(FA.name, GS.name)][g]=mean(r)

        self['precision']=precision


    @logFun("Computing Verspoor et al. (2006) hierarchical recall")
    def recall(self, allFA):
        """
        Verspoor et al. (2006) hierarchical recall 
        """

        #The first FA is used as a Gold Standard
        GS=allFA[0]

        recall=dict()
        for aspect in allAspect:
            if aspect=="All_aspects_of_GO":
                continue
            
            recall[aspect] = dict()
            for FA in allFA[1:]:
                recall[aspect][(FA.name, GS.name)]=dict()
            
                logger.info("\t%s vs %s for %s" % (FA.name, GS.name, aspect))

                commonGene=self.getCommonGene(FA, GS, aspect)
                for g in commonGene:
                    r=list()
                    for gs in GS.GPtoGO[aspect][g]:
                        aGS = set(FA.G.get_Ancestors(gs))
                        naGS = len(aGS)

                        maxSim = max([(1.0 * len(aGS.intersection(FA.G.get_Ancestors(go))))/naGS for go in FA.GPtoGO[aspect][g]])
                        r.append(maxSim)

                    recall[aspect][(FA.name, GS.name)][g]=mean(r)

        self['recall']=recall



    
                



