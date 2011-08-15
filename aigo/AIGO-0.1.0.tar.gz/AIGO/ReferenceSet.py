
"""
ReferenceSet.py

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

import os,csv

from AIGO import logger, logFun
from AIGO.utils.File  import checkForZip, readFile


class RefSet(set):

    def __init__(self,  *args, **kargs):

        self.update(*args)

        self.organism = kargs.get('organism', 'platypus')
        self.fileName = ''
        self.refType  = ''
        
        fileName = kargs.get('fileName', '')
        refType  = kargs.get('refType', 'Fasta')

        if not fileName == '':        
            self.add(fileName, refType)

    @logFun("Creating reference set")
    def add(self, fileName, refType="Fasta"):

        if self.fileName=='':
            self.fileName=fileName
            self.refType=refType
        else:
            if type(self.fileName)==list:
                self.fileName.append(fileName)
                self.refType.append(refType)
            else:
                self.fileName=[self.fileName,fileName]
                self.refType=[self.refType,refType]

        fileName= checkForZip(fileName)
        if (not os.path.exists(fileName)):
            logger.handleFatal(fileName+" does not exist and is required ")

        logger.info("Organism :\t%s" % self.organism)
        
        logger.info("%s file :\t%s " % (refType, fileName ) )

        try:
            
            #Use fasta file to define the reference set
            if refType=="Fasta":
                from Bio import SeqIO
                allID=set([rec.name.split(";")[0].split(":")[-1] for rec in SeqIO.parse(readFile(fileName), "fasta")])
                self.update(allID)

            #Use a simple text file to define the reference set, first column is chosen by default
            elif refType=="Text":
                allID=set([r[0] for r in csv.reader(readFile(fileName), delimiter=";")])
                self.update(allID)

            #Use a GO annotation file to define the reference set
            elif refType=="GAF":
                from AIGO.IO import readGAF_2
                data, GAF_col=readGAF_2(fileName)

                allID=set([".".join([row[GAF_col.index("Taxon(|taxon)")][6:],row[GAF_col.index("DB Object Symbol")]]) for row in data])
                self.update(allID)

            #Use a Affymetrix annotation file to define the reference set
            elif refType=="AFFY":
                f = readFile(fileName)
                row=f.readline()
                while row[0] == '#':
                    row=f.readline()

                header=row
                rd=csv.reader(f)
                allID=set()
                for row in rd:
                #Read gene product id if not control sequence
                    if ("Control sequence".upper() != row[4].upper()):
                        allID.add(row[0])

                self.update(allID)
            else:
                print "Sorry, unknown file type !!"
                self.extend([])
                raise Exception


            if len(self)==0:
                logger.handleWarning("No gene products loaded")
        
        except Exception, e:
            logger.handleFatal("Unable to read file %s: %s" % (fileName, str(e)))



