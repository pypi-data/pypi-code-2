"""
Analysis.py

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

from AIGO import logger, logFun

from AIGO.Similarity import GOSet_Similarity, GO_Similarity

class AnalyseFA(dict):
    """
    This class provides methods to compute statistis about functional annotations.
    """    

    def __init__(self, **args):
            
        # set any keyword valued parameters
        for k,v in args.items():
            self[k] = v


    @logFun("Searching for the largest sets")
    def largestSet(self, allFA):
        """
        This method search for the largest sets of annoation per GO aspect.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            largestSet=dict()
            for aspect in FA.G.aspect:
                l=[len(FA.GPtoGO[aspect][gp]) for gp in FA.GPtoGO[aspect]]
                idx=argmax(l)
                k=FA.GPtoGO[aspect].keys()[idx]
                largestSet[aspect]=(k, l[idx])

            largestSet['All_aspects_of_GO']= max([ largestSet[aspect][1] for aspect in FA.G.aspect])

            FA['largestSet']=largestSet

    @logFun("Computing Obsolescence")
    def obsolete(self, allFA):
        """
        This method computes the percentage of obsolete annotations and
        the percentage obsolete GO term in GO aspect.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            #Compute the percentage of obsolete annotations
            allObsAnnot=dict()

            obs=sum([len(FA.GOtoGP[a][goid]) for a in FA.G.aspect for goid in FA.GOtoGP[a] if FA.G.isObsolete(goid)])
            total=sum([len(FA.GOtoGP[a][goid]) for a in FA.G.aspect for goid in FA.GOtoGP[a] ])
            allObsAnnot['All_aspects_of_GO'] = 100.* obs / total

            for a in FA.G.aspect:
                obs=sum([len(FA.GOtoGP[a][goid]) for goid in FA.GOtoGP[a] if FA.G.isObsolete(goid)])
                total=sum([len(FA.GOtoGP[a][goid]) for goid in FA.GOtoGP[a] ])            
                allObsAnnot[a]=100.* obs / total

            FA['obsolete']=allObsAnnot

            #Compute the percentage of obsolete GO terms
            allObsTerm=dict()
                
            obs=sum([1 for a in FA.G.aspect for goid in FA.GOtoGP[a] if FA.G.isObsolete(goid)])
            total=sum([1 for a in FA.G.aspect for goid in FA.GOtoGP[a] ])
            allObsTerm['All_aspects_of_GO']  = 100.* obs / total

            for a in FA.G.aspect:
                obs=sum([1 for goid in FA.GOtoGP[a] if FA.G.isObsolete(goid)])
                total=sum([1 for goid in FA.GOtoGP[a] ])
                allObsTerm[a]= 100. * obs / total

            FA['obsTerm']=allObsTerm

    @logFun("Computing Obsolescence")
    def unconnected(self, allFA):
        """
        This method computes the percentage of unconnected annotations and
        the percentage of unconnected GO terms in GO aspect.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            #Compute the percentage of obsolete annotations
            allUnconnected=dict()

            unconnected=sum(
                    [len(FA.GOtoGP[a][goid]) for a in FA.G.aspect for goid in FA.GOtoGP[a] if FA.G.isUnconnected(goid)]
                    )
            total=sum([len(FA.GOtoGP[a][goid]) for a in FA.G.aspect for goid in FA.GOtoGP[a] ])
            allUnconnected['All_aspects_of_GO'] = 100.* unconnected / total

            for a in FA.G.aspect:
                unconnected=sum([len(FA.GOtoGP[a][goid]) for goid in FA.GOtoGP[a] if FA.G.isUnconnected(goid)])
                total=sum([len(FA.GOtoGP[a][goid]) for goid in FA.GOtoGP[a] ])            
                allUnconnected[a]=100.* unconnected / total

            FA['unconnected']=allUnconnected

    @logFun("Removing obsolete annotations with no alternative")
    def removeUnconnected(self, allFA):
        """
        This method removes all obsolete annotations with no alternative.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)
            
            for a in FA.G.aspect:
                lgoid=FA.GOtoGP[a].keys()
                for goid in lgoid:
                    if FA.G.isUnconnected(goid): del FA.GOtoGP[a][goid]

                lgp=FA.GPtoGO[a].keys()
                for g in lgp:
                    FA.GPtoGO[a][g]  = set(filter (lambda(goid): not FA.G.isUnconnected(goid), FA.GPtoGO[a][g]))

                    if len(FA.GPtoGO[a][g])==0: del FA.GPtoGO[a][g]

            #Find the set of annotated gene products
            FA['GA']=set()
            for a in  FA.G.aspect:
                FA['GA']=FA['GA']  | set(FA.GPtoGO[a].keys())

    @logFun("Removing redundancy")
    def removeRedundancy(self, allFA):
        """
        This method removes redundant annotations from FA, where rundancy is within each FA.GPtoGO[a][g].
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)
            
            for a in FA.G.aspect:
                for g in FA.GPtoGO[a].keys():
                    redundant=FA.G.get_Redundant(FA.GPtoGO[a][g])
                    FA.GPtoGO[a][g] = FA.GPtoGO[a][g].difference(redundant)

                    for goid in redundant:
                        FA.GOtoGP[a][goid].remove(g)
                        if len(FA.GOtoGP[a][goid])==0: del FA.GOtoGP[a][goid]

    @logFun("Computing redundancy")
    def redundancy(self, allFA):
        """
        This method computes the percentage of redundant annotations.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            allRedundancy=dict()
            for a in FA.G.aspect:
                nbAnnot = sum([ len(FA.GPtoGO[a][g]) for g in FA.GPtoGO[a]])
                nbRed= 0
                for g in FA.GPtoGO[a]:
                    nbRed = nbRed + len(FA.G.get_Redundant(FA.GPtoGO[a][g]))

                allRedundancy[a]= (100.0 * nbRed / nbAnnot )

            allRedundancy['All_aspects_of_GO'] = mean([allRedundancy[a] for a in FA.G.aspect])
            FA['redundancy']=allRedundancy


    @logFun("Computing coverage")
    def coverage(self, allFA):
        """
        This method computes the percentage of annotated gene products.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            coverage= (100.0 * len(FA['GA']) / len(FA.refSet))
            allCoverage=dict()
            for a in FA.G.aspect:
                allCoverage[a]= (100.0 * len(FA.GPtoGO[a]) / len(FA.refSet) )

            allCoverage['All_aspects_of_GO'] = coverage
            FA['coverage']=allCoverage

    @logFun("Computing richness")
    def richness(self, allFA):
        """
        This method computes the number of annotations per annotated gene products.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            At=set()
            GO=set()
            for a in FA.G.aspect:
                At= At | set(FA.GOtoGP[a])
                GO= GO | set([FA.G.GOAlt.get(t,t) for t in FA.G.N if FA.G.GONameSpace[t] == a])
            richness=100.* len(At)/len(GO)

            allRichness=dict()
            for a in FA.G.aspect:
                At=set(FA.GOtoGP[a])
                GO=set([FA.G.GOAlt.get(t,t) for t in FA.G.N if FA.G.GONameSpace[t] == a])
                allRichness[a]=100.0*len(At)/len(GO)

            allRichness['All_aspects_of_GO'] =richness
            FA['richness']=allRichness


    @logFun("Computing the number of annotations per set")
    def numberAnnot(self, allFA):
        """
        This method computes the number of annotations per annotated gene products.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)
                        
            numberAnnot=mean([ len(FA.GPtoGO[a][g]) for a in FA.GPtoGO for g in FA.GPtoGO[a]])
            allNumberAnnot=dict()
            for a in FA.G.aspect:
                allNumberAnnot[a]= [ len(FA.GPtoGO[a][g]) for g in FA.GPtoGO[a]]

            allNumberAnnot['All_aspects_of_GO'] = numberAnnot
            FA['numberAnnot'] = allNumberAnnot


    @logFun("Computing the functional coherence")
    def coherence(self, allFA):
        """
        This method computes the semantic similarity between the annotations of each gene product.
        """
        
        for FA in allFA:
            logger.info("\t%s" % FA.name)

            allCoherence=dict()
            for a in FA.G.aspect:
                allCoherence[a]= [GOSet_Similarity(FA.G, FA.GPtoGO[a][g])[0] for g in FA.GPtoGO[a] ]

            allCoherence['All_aspects_of_GO'] = mean([mean(allCoherence[a]) for a in FA.G.aspect])
            FA['coherence']= allCoherence


    @logFun("Computing the compactness")
    def compactness(self, allFA):
        """
        This method computes the semantic similarity between the gene products.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            allCompactness=dict()
            for a in FA.G.aspect:
                sim, l = GO_Similarity(FA.G, FA.GPtoGO[a].values())
                allCompactness[a]=l

            allCompactness['All_aspects_of_GO'] = mean([mean(allCompactness[a]) for a in FA.G.aspect])
            FA['compactness']=allCompactness


    @logFun("Computing the specificity")
    def specificity(self, allFA):
        """
        This method computes mean number of ancestor annotations per annotated gene product.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            allSpecificity=dict()
            for a in FA.G.aspect:
                allGO=[FA.G.GOtoInt(FA.GPtoGO[a][g]) for g in FA.GPtoGO[a]]
                allSpecificity[a] = [ mean([len(FA.G.ancestors(gsid)) for gsid in GO ]) for GO in allGO ] 

            allSpecificity['All_aspects_of_GO'] = mean([mean(allSpecificity[a]) for a in FA.G.aspect])
            FA['specificity']=allSpecificity


    @logFun("Computing the information content")
    def informationContent(self, allFA):
        """
        This method computes the infotrmation content.
        """

        for FA in allFA:
            logger.info("\t%s" % FA.name)

            IC=dict()
            for a in FA.G.aspect:
                IC[a]=dict()
                for go in FA.GOtoGP[a]:
                    n=len(FA.GOtoGP[a][go])
                    for ans in FA.G.InttoGO(FA.G.ancestors(FA.G.get_intid(go))):
                        IC[a][ans]=IC[a].get(ans, 0) + n

            for a in FA.G.aspect:
                if len(IC[a].values())==0:
                    continue
                m=max(IC[a].values())
                for go in IC[a]:
                    IC[a][go]=-1. * log(1.*IC[a][go]/m)

            allInformationContent=dict()
            for a in FA.G.aspect:
                allInformationContent[a]=[mean([IC[a][go] for go in FA.GPtoGO[a][g] ]) for g in FA.GPtoGO[a] ]

            allInformationContent['All_aspects_of_GO'] = mean([mean(allInformationContent[a]) for a in FA.G.aspect])
            FA['informationContent']=allInformationContent


#------------------------------------------------------------------------------
