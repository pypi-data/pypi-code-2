"""AIGO -- Analysis and Inter-comparison of Gene Ontology functional annotations
__init__.py

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

__author__ =  'Michael Defoin-Platel'
__version__=  '0.1.0'

#__all__ = [ ]

from functools import wraps

allAspect=["All_aspects_of_GO", 'biological_process', 'molecular_function', 'cellular_component']

from AIGO.utils.Logger import Logger
logger=Logger(loglevel=Logger.INFO)

def logFun(msg):
    def wrap(f):  
        @wraps(f)  
        def decorator(*args, **kwargs):  
            logger.info("=================================================")
            logger.info(msg)
            
            value = f(*args, **kwargs)  
            
            logger.info("Done")
            return value  
        return decorator  
    return wrap  
