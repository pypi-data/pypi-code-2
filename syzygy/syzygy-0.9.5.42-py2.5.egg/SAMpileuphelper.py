#!/usr/bin/python

from __future__ import division


# Written by Manuel A. Rivas
# Updated 07.13.2009

# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2009 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$



from optparse import OptionParser;                                                                                                                                                                                                       

import sys,re

from string import *
from rpy2.rpy_classic import *
import numpy

set_default_mode(BASIC_CONVERSION)  
        
        
        
def getmeavgmapping(mappinglist):
    avgmap = numpy.mean(mappinglist)
    return avgmap

def returnbool2ndbestref(intensitylist,integerallelecall,referenceinteger):
    intensitysort = intensitylist
    intensitysort.sort(reverse=True)
    if intensitysort[referenceinteger] == intensitysort[1]:
        bool2ndbest = 1
    else:
        bool2ndbest = 0
    return bool2ndbest


def pmisspower(problist):
    probmiss = 100 - numpy.mean(problist)
    return probmiss

def return_LRT_assoc(casechroms,controlchroms,weightsarraycase,weightsarraycontrol,popfreq,casefreq,controlfreq):
    LOD = 0
    for i in range(0,len(weightsarraycase[0])):
        if r.dbinom(i,casechroms,casefreq)[0] == 0:
            LOD += 0
        else:
            LOD += weightsarraycase[0][i]*r.log(r.dbinom(i,casechroms,casefreq)[0])[0]
    for i in range(0,len(weightsarraycontrol[0])):
        if r.dbinom(i,controlchroms,controlfreq)[0] == 0:
            LOD += 0 
        else:
            LOD += weightsarraycontrol[0][i]*r.log(r.dbinom(i,controlchroms,controlfreq)[0])[0]
    for i in range(0,len(weightsarraycase[0])):
        if r.dbinom(i,casechroms,popfreq)[0] == 0:
            LOD += 0
        else:
            LOD -= weightsarraycase[0][i]*r.log(r.dbinom(i,casechroms,popfreq)[0])[0]
    for i in range(0,len(weightsarraycontrol[0])):
        if r.dbinom(i,controlchroms,popfreq)[0] == 0:
            LOD += 0
        else:
            LOD -= weightsarraycontrol[0][i]*r.log(r.dbinom(i,controlchroms,popfreq)[0])[0]
    return LOD

## Edited such that statistic wont be inflated when coverage is really low

def return_LRT_assocConservative(casechroms,controlchroms,weightsarraycase,weightsarraycontrol,popfreq,casefreq,controlfreq):
    LOD = 0
    for i in range(0,len(weightsarraycase[0])):
        if r.dbinom(i,casechroms,casefreq)[0] == 0:
            LOD += 0
        else:
            LOD += weightsarraycase[0][i]*r.log(r.dbinom(i,casechroms,casefreq)[0])[0]
    for i in range(0,len(weightsarraycontrol[0])):
        if r.dbinom(i,controlchroms,controlfreq)[0] == 0:
            LOD += 0 
        else:
            LOD += weightsarraycontrol[0][i]*r.log(r.dbinom(i,controlchroms,controlfreq)[0])[0]
    for i in range(0,len(weightsarraycase[0])):
        if r.dbinom(i,casechroms,popfreq)[0] == 0:
            LOD += 0
        else:
            LOD -= weightsarraycase[0][i]*r.log(r.dbinom(i,casechroms,popfreq)[0])[0]
    for i in range(0,len(weightsarraycontrol[0])):
        if r.dbinom(i,controlchroms,popfreq)[0] == 0:
            LOD += 0
        else:
            LOD -= weightsarraycontrol[0][i]*r.log(r.dbinom(i,controlchroms,popfreq)[0])[0]
    return LOD



def checktransitiontransversion(alleles):
    change = str(alleles)
    if "AG" in change or "GA" in change or "CT" in change or "TC" in change:
        return 1
    else:
        return 0
    
def return_prob_weights(snp,probvector,datadictionary,map):
    probveckeys = [(k,v) for k,v in probvector.keys() if k == snp]
    probveckeys.sort()
    if len(probveckeys) == 0:
        probarray = []
        return probarray
    elif len(probveckeys) == 1:
        probarray = probvector[probveckeys[0]]
        return probarray
    else:
        for j in range(0,len(probveckeys)):
            if probveckeys[j] in probvector:
                if len(probveckeys) > 1:
                    if j == 0:
                        probarray = numpy.zeros((1,len(probvector[probveckeys[j]][0]) + len(probvector[probveckeys[j+1]][0])-1))
                        columnvector = numpy.transpose(probvector[probveckeys[j]])
                        matrixinit = columnvector[::-1]*probvector[probveckeys[j+1]]
                        tmp = -1
                        for i in range(-len(columnvector) + 1,len(probvector[probveckeys[j+1]][0])):
                            tmp += 1
                            probarray[0][tmp] += numpy.trace(matrixinit,i)          
                        probarraytemp = probarray
                    elif j < (len(probveckeys) - 1) and j > 0:
                        probarray = numpy.zeros((1,len(probarraytemp[0]) + len(probvector[probveckeys[j+1]][0]) -1))
                        columnvector = numpy.transpose(probarraytemp)
                        matrixnew = columnvector[::-1]*probvector[probveckeys[j+1]]
                        tmp = -1
                        for i in range(-len(columnvector) + 1,len(probvector[probveckeys[j+1]][0])):
                            tmp += 1
                            probarray[0][tmp] += numpy.trace(matrixnew,i)
                            
                        probarraytemp = probarray
                    
                    else:
                        return probarray
            else:
                pass





def set_ref_index(ref_all):
    if ref_all == 'A':
        ref_ind = 0
    elif ref_all == 'C':
        ref_ind = 1
    elif ref_all == 'G':
        ref_ind = 2
    elif ref_all == 'T':
        ref_ind = 3
    elif ref_all == 'N':
        ref_ind = 0
    elif ref_all == 'D':
        ref_ind = 4
    elif ref_all == 'I':
        ref_ind = 5
    return ref_ind

def return_best_2nd_best(ref_index,acgtdad,acgtmom,acgtchild):
    finallist = numpy.add(acgtdad,acgtmom,acgtchild)
    blah = [finallist[0]  + finallist[6],finallist[1] + finallist[7],finallist[2] + finallist[8],finallist[3] + finallist[9],finallist[4] + finallist[10], finallist[5] + finallist[11]]
    blahsort = sorted(blah,reverse=True)
    if blah[0] == blahsort[0]:
        best = 0
    elif blah[1] == blahsort[0]:
        best = 1
    elif blah[2] == blahsort[0]:
        best = 2
    elif blah[3] == blahsort[0]:
        best = 3
    if blah[0] == blahsort[1]:
        secondbest = 0
    elif blah[1] == blahsort[1]:
        secondbest = 1
    elif blah[2] == blahsort[1]:
        secondbest = 2
    elif blah[3] == blahsort[1]:
        secondbest = 3
    else:
        secondbest = best + 1
    return (best,secondbest)

def return_allele_counts_calls(line):
    afwdcnt = line[2]                                                                                                                                                                                                                                     
    cfwdcnt = line[3]                                                                                                                                                                                                                                     
    gfwdcnt = line[4]                                                                                                                                                                                                                                     
    tfwdcnt = line[5]                                                                                                                                                                                                                                     
    dfwdcnt = line[6]                                                                                                                                                                                                                                     
    ifwdcnt = line[7]                                                                                                                                                                                                                                     
    coveragefwd = line[8]                                                                                                                                                                                                                                 
    arevcnt = line[9]                                                                                                                                                                                                                                     
    crevcnt = line[10]                                                                                                                                                                                                                                    
    grevcnt = line[11]                                                                                                                                                                                                                                    
    trevcnt = line[12]                                                                                                                                                                                                                                    
    drevcnt = line[13]                                                                                                                                                                                                                                    
    irevcnt = line[14] 
    afwd = afwdcnt.split(':')
    cfwd = cfwdcnt.split(':')
    gfwd = gfwdcnt.split(':')
    tfwd = tfwdcnt.split(':') 
    dfwd = dfwdcnt.split(':')
    ifwd = ifwdcnt.split(':')
    arev = arevcnt.split(':')
    crev = crevcnt.split(':')
    grev = grevcnt.split(':')
    trev = trevcnt.split(':')
    drev = drevcnt.split(':')
    irev = irevcnt.split(':')   
    listcnts = [(int(afwd[1]) + int(arev[1])),(int(cfwd[1]) + int(crev[1])),(int(gfwd[1]) + int(grev[1])),(int(tfwd[1]) + int(trev[1])), (int(dfwd[1]) + int(drev[1])), (int(ifwd[1]) + int(irev[1]))]
    return listcnts



def return_allele_counts_callsrev(line):                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    arevcnt = line[9]                                                                                                                                                                                                                                     
    crevcnt = line[10]                                                                                                                                                                                                                                    
    grevcnt = line[11]                                                                                                                                                                                                                                    
    trevcnt = line[12]                                                                                                                                                                                                                                    
    drevcnt = line[13]                                                                                                                                                                                                                                    
    irevcnt = line[14] 
    arev = arevcnt.split(':')
    crev = crevcnt.split(':')
    grev = grevcnt.split(':')
    trev = trevcnt.split(':')  
    drev = drevcnt.split(':')
    irev = irevcnt.split(':') 
    listcnts = [(int(arev[1])),(int(crev[1])),(int(grev[1])),(int(trev[1])), (int(drev[1])), int(irev[1])]
    return listcnts



def return_allele_counts_callsfwd(line):
    afwdcnt = line[2]                                                                                                                                                                                                                                     
    cfwdcnt = line[3]                                                                                                                                                                                                                                     
    gfwdcnt = line[4]                                                                                                                                                                                                                                     
    tfwdcnt = line[5]                                                                                                                                                                                                                                     
    dfwdcnt = line[6]                                                                                                                                                                                                                                     
    ifwdcnt = line[7]                                                                                                                                                                                                                                     
    coveragefwd = line[8]                                                                                                                                                                                                                                 
    afwd = afwdcnt.split(':')
    cfwd = cfwdcnt.split(':')
    gfwd = gfwdcnt.split(':')
    tfwd = tfwdcnt.split(':') 
    dfwd = dfwdcnt.split(':')
    ifwd = ifwdcnt.split(':')
    listcnts = [(int(afwd[1])),(int(cfwd[1])),(int(gfwd[1])),(int(tfwd[1]) ), int(dfwd[1]), int(ifwd[1])]
    return listcnts

def getsum(listints):
    a = 0
    for i in listints:
        a += int(i)
    return a
def returnintlist(liststring): 
    return [int(x) for x in liststring]
def complement(seq):  
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}  
    complseq = [complement[base] for base in seq]  
    return complseq 
def return_ref_index(allele):
    reference_dict = {'A': 0,'C': 1, 'G': 2, 'T': 3,'D':4,'I':5}
    return reference_dict[allele]
def reverse_complement(seq):
    seq = list(seq)
    seq.reverse()
    return ''.join(complement(seq))

def computeaveragemcrate(mcratelist):
    listmcrate = [ mcrate  for mcrate in mcratelist ]
    return listmcrate

def ascii_list(s):
    return [ ord(c) - 33 for c in s]

def return_acgtdi_list(ref_idx,allele_list_threshold):
    counts = [0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,len(allele_list_threshold)):
        if allele_list_threshold[i] == '.':
            counts[ref_idx + 6] += 1
        elif allele_list_threshold[i] == ',':
            counts[ref_idx] += 1
        elif allele_list_threshold[i] == 'a':
            counts[6] += 1
        elif allele_list_threshold[i] == 'c':
            counts[7] += 1
        elif allele_list_threshold[i] == 'g':
            counts[8] += 1
        elif allele_list_threshold[i] == 't':
            counts[9] += 1
        elif allele_list_threshold[i] == 'A':
            counts[0] += 1 
        elif allele_list_threshold[i] == 'C':
            counts[1] += 1
        elif allele_list_threshold[i] == 'G':
            counts[2] += 1
        elif allele_list_threshold[i] == 'T':
            counts[3] += 1
    return counts
def hello_world(a):
    return "hello"
def return_mapqlistref_SAM(qthreshold,qlist,mapqlist,allele_list,mapqdist):
    allele_list_threshold = []
    index = 0
    indexbases = 0
    while index < len(allele_list):
        if indexbases >= len(qlist):
            index += 1
        else:
            if allele_list[index] == '+':            
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    allele_list_threshold.append('I')
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    allele_list_threshold.append('i')
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '-':
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    allele_list_threshold.append('D')
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    allele_list_threshold.append('d')
                indexold = index 
                index += int(allele_list[indexold +1]) + 2
            elif allele_list[index] == '$':
                index += 1
            elif allele_list[index] == '^':
                index += 2
            elif allele_list[index] == '.':
                if qlist[indexbases] >= qthreshold:
                    allele_list_threshold.append(allele_list[index])
                    mapqdist.append(mapqlist[indexbases])
                index += 1
                indexbases += 1
            elif allele_list[index] == ',':
                if qlist[indexbases] >= qthreshold:
                    allele_list_threshold.append(allele_list[index])
                    mapqdist.append(mapqlist[indexbases])
                index += 1
                indexbases += 1
            else:
                indexbases += 1
                index += 1
    return mapqdist

def fltpts(numberin,floatnum):
    floatnum = int(floatnum)
    numberout = str(float(int(math.pow(10,floatnum)*float(numberin)))/math.pow(10,floatnum))
    return floatnum 

def return_mapqlist_SAM(qthreshold,qlist,mapqlist,allele_list,mapqdist):
    allele_list_threshold = []
    index = 0
    indexbases = 0
    while index < len(allele_list):
        if indexbases >= len(qlist):
            index += 1
        else:
            if allele_list[index] == '+':            
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    allele_list_threshold.append('I')
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    allele_list_threshold.append('i')
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '-':
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    allele_list_threshold.append('D')
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    allele_list_threshold.append('d')
                indexold = index
                index += int(allele_list[indexold +1]) + 2
            elif allele_list[index] == '$':
                index += 1
            elif allele_list[index] == '^':
                index += 2
            elif allele_list[index] == '.':
                index += 1
                indexbases += 1
            elif allele_list[index] == ',':
                index += 1
                indexbases += 1
            else:
                if qlist[indexbases] >= qthreshold:
                    allele_list_threshold.append(allele_list[index])
                    mapqdist.append(mapqlist[indexbases])
                indexbases += 1
                index += 1
    return mapqdist

def return_snd_list_SAM(mapqval,qval,qlist,mapqlist,allele_list,sndlist):
    sndlist_threshold = []
    allele_threshold = [] 
    index = 0
    indexbases = 0
    while index < len(allele_list):
        if indexbases >= len(qlist):
            index += 1
        else:
            if allele_list[index] == '+':
                if allele_list[index + 2] == 'A' or allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    pass
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    pass
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '-':
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    pass
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    pass
                indexold = index
                index += int(allele_list[indexold +1]) + 2
            elif allele_list[index] == '$':
                index += 1
            elif allele_list[index] == '^':
                index += 2
            else:
                if qlist[indexbases] >= qval and mapqlist[indexbases] >= mapqval:
                    allele_threshold.append(allele_list[index])
                    sndlist_threshold.append(sndlist[indexbases])
                indexbases += 1
                index += 1
    return (allele_threshold,sndlist_threshold)

def computesndLODfwd(allelethreshold,sndthreshold,snpsndlodfwd,ref,alt):
    refbstfwd = 0
    altsndfwd = 0
    altbstfwd = 0
    refsndfwd = 0
    alt = alt.upper()
    
    for i in range(0,len(allelethreshold)):
        if allelethreshold[i] == '.':
            refbstfwd += 1
            if sndthreshold[i] == alt:
                altsndfwd += 1
        elif allelethreshold[i] == alt:
            altbstfwd += 1
            if sndthreshold[i] == ref:
                refsndfwd += 1
                
    snpsndlodfwd -= return_loglr(r.log10(r.dbinom(altsndfwd,refbstfwd,.42)[0])[0])
    snpsndlodfwd -= return_loglr(r.log10(r.dbinom(refsndfwd,altbstfwd,.42)[0])[0])
    snpsndlodfwd += return_loglr(r.log10(r.dbinom(altsndfwd,refbstfwd,.75)[0])[0])
    snpsndlodfwd += return_loglr(r.log10(r.dbinom(refsndfwd,altbstfwd,.75)[0])[0])
    return snpsndlodfwd
    
def return_loglr(a):
    out = a
    if a == float('-inf'):
        out = -1000
    elif a == float('inf'):
        out = 1000
    else:
        out = a
    return out

def computesndLODrev(allelethreshold,sndthreshold,snpsndlodrev,ref,alt):
    refbstrev = 0
    altsndrev = 0
    altbstrev = 0
    refsndrev = 0
    refrc = reverse_complement(ref)
    refrcup = refrc[0]
    altrc = reverse_complement(alt)[0]
    
    altlow = alt.lower()
    altup = alt.upper()
    
    for i in range(0,len(allelethreshold)):
        if allelethreshold[i] == ',':
            refbstrev += 1
            if sndthreshold[i] == altup:
                altsndrev += 1
        elif allelethreshold[i] == altlow:
            altbstrev += 1
            if sndthreshold[i] == ref:
                refsndrev += 1
        
    snpsndlodrev -= return_loglr(r.log10(r.dbinom(altsndrev,refbstrev,.42)[0])[0])
    snpsndlodrev -= return_loglr(r.log10(r.dbinom(refsndrev,altbstrev,.42)[0])[0])
    snpsndlodrev += return_loglr(r.log10(r.dbinom(altsndrev,refbstrev,.75)[0])[0])
    snpsndlodrev += return_loglr(r.log10(r.dbinom(refsndrev,altbstrev,.75)[0])[0])
    return snpsndlodrev
    
def computecombLOD(sndLODfwd,sndLODrev):
    combinedsndLOD = sndLODfwd + sndLODrev
    return combinedsndLOD

##### Check Cluster Function

def checkcluster(chroffset,snpdict,clusterdict):
    (chr,pos) = chroffset.split(':')
    position = int(pos)
    check = 'false'
    for i in range(position - 2,position + 3):
        chroffsetcheck = str(chr) + ':' + str(i)
        if chroffsetcheck in snpdict and chroffsetcheck != chroffset:
            check = 'true'
            clusterdict[chroffsetcheck] = chroffsetcheck
        else:
            pass
    return check



def return_alleleq_list_SAM(mapqval,qval,qlist,mapqlist,allele_list):
    allele_list_threshold = []
    index = 0
    indexbases = 0
    while index < len(allele_list):
        if indexbases >= len(qlist):
            index += 1
        else:
            if allele_list[index] == '+':            
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    allele_list_threshold.append('I')
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    allele_list_threshold.append('i')
                indexold  = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '-':
                if allele_list[index + 2] == 'A' or  allele_list[index + 2] == 'C' or allele_list[index + 2] == 'G' or allele_list[index + 2] == 'T' or allele_list[index + 2] == 'N':
                    allele_list_threshold.append('D')
                elif allele_list[index + 2] == 'a' or allele_list[index + 2] == 'c' or allele_list[index + 2] == 'g' or allele_list[index + 2] == 't' or allele_list[index + 2] == 'n':
                    allele_list_threshold.append('d')
                indexold = index
                index += int(allele_list[indexold +1]) + 2
            elif allele_list[index] == '$':
                index += 1
            elif allele_list[index] == '^':
                index += 2
            else:
                if qlist[indexbases] >= qval and mapqlist[indexbases] >= mapqval:
                    allele_list_threshold.append(allele_list[index])
                indexbases += 1
                index += 1
    return allele_list_threshold



def return_acgtdi_list_SAM(ref_idx,allele_list_threshold):
    counts = [0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,len(allele_list_threshold)):
        if allele_list_threshold[i] == '.':
            counts[ref_idx] += 1
        elif allele_list_threshold[i] == ',':
            counts[ref_idx+6] += 1
        elif allele_list_threshold[i] == 'a':
            counts[6] += 1
        elif allele_list_threshold[i] == 'c':
            counts[7] += 1
        elif allele_list_threshold[i] == 'g':
            counts[8] += 1
        elif allele_list_threshold[i] == 't':
            counts[9] += 1
        elif allele_list_threshold[i] == 'd':
            counts[10] += 1
        elif allele_list_threshold[i] == 'i':
            counts[11] += 1
        elif allele_list_threshold[i] == 'A':
            counts[0] += 1 
        elif allele_list_threshold[i] == 'C':
            counts[1] += 1
        elif allele_list_threshold[i] == 'G':
            counts[2] += 1
        elif allele_list_threshold[i] == 'T':
            counts[3] += 1
        elif allele_list_threshold[i] == 'D':
            counts[4] += 1
        elif allele_list_threshold[i] == 'I':
            counts[5] += 1
    return counts






def return_alleleq_list_nonref_SAM(qlist,allele_list):
    allele_list_threshold = [0]*50
    index = 0
    indexbases = 0
    while index < len(allele_list):
        if indexbases >= len(qlist):
            index += 1
        elif qlist[indexbases] < 1 or qlist[indexbases] > 50:
            index += 1
            indexbases += 1
        else:
            if allele_list[index] == '+':
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '-':
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '^':
                index += 2
            elif allele_list[index] == '$':
                index += 1
            elif allele_list[index] == ',':
                allele_list_threshold[int(qlist[indexbases]) - 1] += 0
                index += 1
                indexbases += 1
            elif allele_list[index] == '.':
                allele_list_threshold[int(qlist[indexbases])-1] += 0
                index += 1
                indexbases += 1
            else:
                allele_list_threshold[int(qlist[indexbases]) - 1] += 1
                index += 1
                indexbases += 1
    return allele_list_threshold





def return_alleleq_list_ref_SAM(qlist,allele_list):
    allele_list_threshold = [0]*50
    index = 0
    indexbases = 0
    while index < len(allele_list):
        if indexbases >= len(qlist):
            index += 1
        elif qlist[indexbases] < 1 or qlist[indexbases] > 50:
            index += 1
            indexbases += 1
        else:
            if allele_list[index] == '+':
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '-':
                indexold = index
                index += int(allele_list[indexold + 1]) + 2
            elif allele_list[index] == '^':
                index += 2
            elif allele_list[index] == '$':
                index += 1
            elif allele_list[index] == ',':
                allele_list_threshold[int(qlist[indexbases]) - 1] += 1
                index += 1
                indexbases += 1
            elif allele_list[index] == '.':
                allele_list_threshold[int(qlist[indexbases])-1] += 1
                index += 1
                indexbases += 1
            else:
                allele_list_threshold[int(qlist[indexbases]) - 1] += 0
                index += 1
                indexbases += 1
    return allele_list_threshold





######################




def return_q_list(qval,qlist):
    return [q for q in qlist if q >= qval]


def return_alleleq_list(qval,qlist,allele_list):
    allele_list_threshold = []
    for i in range(0,len(qlist) ):
        if qlist[i] >= qval:
            allele_list_threshold.append(allele_list[i])
    return allele_list_threshold

def return_alleleq_list_ref(qlist,allele_list):
    allele_list_threshold = [0]*50
    for i in range(0,len(allele_list)):
        if allele_list[i] == ',':
            allele_list_threshold[int(qlist[i]) - 1] += 1
        elif allele_list[i] == '.':
            allele_list_threshold[int(qlist[i])-1] += 1
        else:
            allele_list_threshold[int(qlist[i]) - 1] += 0
    return allele_list_threshold

def return_alleleq_list_nonref(qlist,allele_list):
    allele_list_threshold = [0]*50
    for i in range(0,len(allele_list)):
        if allele_list[i] == ',':
            allele_list_threshold[int(qlist[i]) - 1] += 0
        elif allele_list[i] == '.':
            allele_list_threshold[int(qlist[i])-1] += 0
        else:
            allele_list_threshold[int(qlist[i]) - 1] += 1
    return allele_list_threshold


def returnnonrefcountqlist(qlist,allele_list):
    nonrefqlist = []
    for i in range(0,len(allele_list)):
        if allele_list[i] == ',':
            pass
        elif allele_list[i] == '.':
            pass
        else:
            nonrefqlist.append(qlist[i])
    return nonrefqlist


def returnrefcountqlist(qlist,allele_list):
    refqlist = []
    for i in range(0,len(allele_list)):
        if allele_list[i] == ',':
            refqlist.append(qlist[i])
        elif allele_list[i] == '.':
            refqlist.append(qlist[i])
        else:
            pass
    return refqlist


def returnnonrefcount(allele_list):
    nonrefcount = 0
    for i in range(0,len(allele_list)):
        if allele_list[i] == ',':
            nonrefcount += 0
        elif allele_list[i] == '.':
            nonrefcount += 0
        else:
            nonrefcount += 1
    return nonrefcount

def assign_ref_index(reference_allele_id):
    if reference_allele_id == 'A':                                                                                                                                                                     
        ref_index_strat = 0                                                                                                                                                                               
    elif reference_allele_id == 'C':                                                                                                                                                                   
        ref_index_strat = 1                                                                                                                                                                               
    elif reference_allele_id == 'G':                                                                                                                                                                   
        ref_index_strat = 2                                                                                                                                                                               
    elif reference_allele_id == 'T':                                                                                                                                                                   
        ref_index_strat = 3  
    else:
        ref_index_strat = 0
    return ref_index_strat

def populate_dbsnp_dictionary(dictdbsnp,filedbsnp):
    dbsnpf = open(filedbsnp,'r')
    for line in dbsnpf:
        snp = line.split()
        dictdbsnp[snp[0]] = snp[0]
    return dictdbsnp


def get_miscallrate_list(reflist,nonreflist):
    if len(reflist) == len(nonreflist):
        miscallrates = [0]*len(reflist)
        for i in range(0,len(reflist) ):
            miscallrates[i] = nonreflist[i]/(reflist[i] + nonreflist[i])
    else:
        pass
    return miscallrates


def return_qlist_updates(qlistupdate,qlist):
    for i in range(0,len(qlist)):
        qlistupdate[qlist[i]] += 1
    return qlistupdate
