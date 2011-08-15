"""
OBO.py

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


import os

from AIGO import logger, logFun
from AIGO.utils.File  import checkForZip, readFile
from AIGO.go.GOGraph import get_GOGraph

#------------------------------------------------------------------------------------
@logFun("Creating GO graph")
def readGOoboXML(fileName, force=False, prefix="GO"):
    import cPickle as pickle

    picName="%s.pic" % fileName
    if (not os.path.exists(picName)):
        force=True

    if not force:
        try:
            logger.info("Reading serialized OBO file : %s" % picName)
            with open(picName, "rb") as f:
                
                G = pickle.load(f)
                f.close()
        except IOError as (inst):
            print str(type(inst))+ " for "+picName
            force=True
        except EOFError as (inst):  ##its an empty file?
            print str(type(inst))+" for "+picName
            force=True

    try:
        if force:
            fileName= checkForZip(fileName)
            if (not os.path.exists(fileName)):
                raise IOError(fileName+" does not exist and is required ")

            logger.info("Reading OBO file : %s" % fileName)
            
            G = get_GOGraph(readFile(fileName, mode="r"), prefix=prefix)
            G.fileName=fileName

            with open(picName, "wb") as f:
                logger.info("Saving serialized OBO file")
                pickle.dump(G, f, -1)
            f.close()
    except Exception, e:
        logger.handleFatal("Unable to read file %s: %s" % (fileName, str(e)))
    
    return G
