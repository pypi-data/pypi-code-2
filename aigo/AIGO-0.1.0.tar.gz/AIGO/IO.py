"""
IO.py

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
import os, csv

from itertools import izip

from AIGO import logger
from AIGO.utils.File  import checkForZip, readFile

IOType={"GO Annotation File":"GAF", "Blast2GO":"B2G", "Affymetrix":"AFFY", "ArrayIDer":"AID", "Mapping GPid GOids": "GP2GO"}

#-------------------------------------------------------
def extract_COPSA(fileName, G, refSet=None):
    """
    Read a functional annotation from the COPSA pipeline including provenance information and COPSA internal weights
    Gene_ID sep1 GO_ID,GO_ID sep1 [Prov, Prov] sep1 w1 sep1 w2 .... w16
    """

    fileName= str(checkForZip(fileName))
    if (not os.path.exists(fileName)):
        raise IOError(fileName + " does not exist and is required ")

    hasRef=None
    if refSet:
        hasRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene , = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()

    AnnotationtoProvenance, ProvenancetoAnnotation = dict(), dict()
    for aspect in G.aspect:
        AnnotationtoProvenance[aspect], ProvenancetoAnnotation[aspect] =dict(), dict()

    f=open(fileName, "r")

    import re

    for row in f:

        data=row.replace("\r", "").replace("\n", "").split("\t")
        g=data[0]
        
        go=data[1].split(",")
        
        #provenance=data[2].split(",")
        provenance=re.split('\],\ +\[|^\[|\]$', data[2])[1:-1]
        
        weights=data[3:]

        if not hasRef is None and not hasRef.has_key(g):
            logger.handleWarning("gene product %s is not in the reference set, skip it " % g)
            continue
            
        for term, prov in zip(go, provenance):
            term = term.strip();
            prov = ','.join(sort(prov.replace(" ", "").split(',')))
            #prov = ','.join(prov.replace(" ", "").split(','))
            
            if not term.find('GO:')==0:
                continue

            #Get the alternative term if any and its GO aspect
            term, aspect=G.get_GOAlternative(term, nameSpace=True)

            if not aspect:
                logger.handleWarning("%s: term %s is not in GO graph, skip it " % (g, term))
                continue

            GenetoGO[aspect].setdefault(g, set([])).add(term)
            GOtoGene[aspect].setdefault(term, set([])).add(g)

            AnnotationtoProvenance[aspect].setdefault((g,term), []).append(prov)
            ProvenancetoAnnotation[aspect].setdefault(prov, set([])).add((g,term))

    f.close()
            
    return GenetoGO, GOtoGene, AnnotationtoProvenance, ProvenancetoAnnotation

def extract_GP2GO(fileName, G, refSet=None, sep1='\t', sep2=',', comments='#', skiprows=0):
    """
    Read a functional annotation mapping file of the form
    Gene_ID sep GO_ID,GO_ID
    sep is \t by default
    """

    fileName= str(checkForZip(fileName))
    if (not os.path.exists(fileName)):
        raise IOError(fileName + " does not exist and is required ")

    hasRef=None
    if refSet:
        hasRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()


    data= loadtxt(fileName, dtype="S", usecols=[0,1],
                        delimiter=sep1, comments=comments, skiprows=skiprows)

    for g,go in data:

        if not hasRef is None and not hasRef.has_key(g):
            logger.handleWarning("gene product %s is not in the reference set, skip it " % g)
            continue
            
        for term in go.split(sep2):
            term = term.strip();
            
            if not term.find('GO:')==0:
                continue

            #Get the alternative term if any and its GO aspect
            term, aspect=G.get_GOAlternative(term, nameSpace=True)

            if not aspect:
                logger.handleWarning("%s: term %s is not in GO graph, skip it " % (g, term))
                continue

            GenetoGO[aspect].setdefault(g, set([])).add(term)
            GOtoGene[aspect].setdefault(term, set([])).add(g)
            
    return GenetoGO, GOtoGene


def extract_GO2GP(fileName, G, refSet=None, sep1='\t', sep2=',', comments='#', skiprows=0):
    """
    Read a functional annotation mapping file of the form
    GO_ID sep Gene_ID,Gene_ID
    sep is \t by default
    """

    fileName= str(checkForZip(fileName))
    if (not os.path.exists(fileName)):
        raise IOError(fileName + " does not exist and is required ")

    hasRef=None
    if refSet:
        hasRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()


    data= loadtxt(fileName, dtype="S", usecols=[0,1],
                  delimiter=sep1, comments=comments, skiprows=skiprows)

    for go,GP in data:

        if not go.find('GO:')==0:
                continue

        #Get the alternative term if any and its GO aspect
        term, aspect=G.get_GOAlternative(go, nameSpace=True)

        if not aspect:
            logger.handleWarning("term %s is not in GO graph, skip it " % (term))
            continue

        for gp in GP.split(sep2):
            gp = gp.strip();

            if not hasRef is None and not hasRef.has_key(gp):
                logger.handleWarning("gene product %s is not in the reference set, skip it " % gp)
                continue

            GenetoGO[aspect].setdefault(gp, set([])).add(go)
            GOtoGene[aspect].setdefault(go, set([])).add(gp)
            
    return GenetoGO, GOtoGene



def extract_AID(fileName, G, refSet=None):
    fileName= checkForZip(fileName)
    if (not os.path.exists(fileName)):
        raise IOError(fileName+" does not exist and is required ")

    hasRef=None
    if refSet:
        hasRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()

    rd=csv.reader(readFile(fileName), delimiter="\t")
    header=rd.next()

    for row in rd:
        #Old format...
        #g=row[header.index('ProbesetID')]
        g=row[header.index('Probeset_id')]
        go=row[header.index('GO:ID')]

        if hasRef and not hasRef.has_key(g):
            logger.handleWarning("gene product %s is not in the reference set, skip it " % g)
            continue

        if go.find('GO:')==0:

            #Get the alternative term if any and its GO aspect
            go, aspect=G.get_GOAlternative(go, nameSpace=True)
            if not aspect:
                logger.handleWarning("term %s is not in GO graph, skip it " % go)
                continue

            GenetoGO[aspect].setdefault(g, set([])).add(go)
            GOtoGene[aspect].setdefault(go,set([])).add(g)

    return GenetoGO, GOtoGene


#Affymetrix TAF format
#http://www.affymetrix.com/support/technical/manual/taf_manual.affx
def extract_Affy(fileName, G, refSet=None, GO_columns=[30, 31, 32], filetype="Affy", delimiter=',', quoting=csv.QUOTE_ALL):
    fileName= checkForZip(fileName)
    if (not os.path.exists(fileName)):
        raise IOError(fileName+" does not exist and is required ")

    #sniff and seek dialect
    csvfile = readFile(fileName)

    hasRef=None
    if refSet:
        hasRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()

    #Skip comments
    row=csvfile.readline()
    while row[0] == '#':
        row=csvfile.readline()

    #Read Header
    header=row
    #rd=list(csv.reader(f))

    csv.register_dialect('format', delimiter=delimiter, quoting=quoting)    
    rd=csv.reader(csvfile, dialect='format')
    for row in rd:
        #Read gene product id
        g=row[0]

        if hasRef and not hasRef.has_key(g):
            logger.handleWarning("gene product %s is not in the reference set, skip it " % g)
            continue

        for aspect, i in zip(['biological_process', 'cellular_component', 'molecular_function'], GO_columns):
            for item in row[i].split('///'):
                if not item=="---" and not len(item.strip())==0:
                    go="GO:%07d" % int(item.split('//')[0].replace('/',''))

                    go, aspect=G.get_GOAlternative(go, nameSpace=True)
                    if not aspect:
                        logger.handleWarning("term %s is not in GO graph, skip it " % go)
                        continue
                    GenetoGO[aspect].setdefault(g, set([])).add(go)
                    GOtoGene[aspect].setdefault(go, set([])).add(g)

    return GenetoGO, GOtoGene


def readGAF_2(fileName):
    GAF_col=["DB","DB Object ID","DB Object Symbol","Qualifier",
             "GO ID","DB:Reference","Evidence Code","With (or) From",
             "Aspect","DB Object Name","DB Object Synonym","DB Object Type",
             "Taxon(|taxon)","Date","Assigned By","Annotation Extension","Gene Product Form ID"]
        
    #Read the entire file
    data=[row for row in csv.reader(readFile(fileName), delimiter="\t")]

    #Read the header
    seek=0
    GAF_OK=False
    while data[seek][0][0]=="!":
        if data[seek][0]=="!gaf-version: 2.0":
            GAF_OK=True
        seek=seek+1

    if not GAF_OK:
        raise Exception("Sorry, GAF format version 2.0 expected.")

    return iter(data[seek:]), GAF_col

def extract_GAF(fileName, G, refSet=None):
    
    fileName= checkForZip(fileName)
    if (not os.path.exists(fileName)):
        raise IOError(fileName+" does not exist and is required ")

    hasRef=None
    if refSet:
        refRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()

    data,GAF_col = readGAF_2(fileName)

    for row in data:
        #g=row[GAF_col.index("DB Object Symbol")]
        g=".".join([row[GAF_col.index("Taxon(|taxon)")][6:],row[GAF_col.index("DB Object Symbol")]])
        
        go=row[GAF_col.index('GO ID')]
        
        if not row[GAF_col.index('Qualifier')].find('NOT')==-1:
            logger.handleWarning("go term %s for gene product %s is qualified as NOT: ignored" % (go, g))
            continue

        if hasRef and not hasRef.has_key(g):
            logger.handleWarning("gene product %s is not in the reference set, skip it " % g)
            continue

        if go.find('GO:')==0:

            go, aspect=G.get_GOAlternative(go, nameSpace=True)

            if not aspect:
                logger.handleWarning("term %s is not in GO graph, skip it " % go)
                continue

            GenetoGO[aspect].setdefault(g, set([])).add(go)
            GOtoGene[aspect].setdefault(go,set([])).add(g)

    return GenetoGO, GOtoGene

    

def extract_SCOP(fileName, G, refSet=None):
    fileName= checkForZip(fileName)
    if (not os.path.exists(fileName)):
        raise IOError(fileName+" does not exist and is required ")

    hasRef=None
    if refSet:
        hasRef=dict(izip(refSet, refSet))

    GenetoGO, GOtoGene = dict(), dict()
    for aspect in G.aspect:
        GenetoGO[aspect], GOtoGene[aspect] =dict(), dict()

    rd=csv.reader(readFile(fileName), delimiter=";")
    header=rd.next()

    for row in rd:
         #Read gene product id
        g=row[0]

        g=row[header.index('domScop')]
        go=row[header.index('termGo')]

        if hasRef and not hasRef.has_key(g):
            logger.handleWarning("gene product %s is not in the reference set, skip it " % g)
            continue

        if go.find('GO:')==0:
            #Get the alternative term if any and its GO aspect
            go, aspect=G.get_GOAlternative(go, nameSpace=True)

            if not aspect:
                logger.handleWarning("term %s is not in GO graph, skip it " % term)
                continue

            GenetoGO[aspect].setdefault(g, set([])).add(go)
            GOtoGene[aspect].setdefault(go,set([])).add(g)

    return GenetoGO, GOtoGene

