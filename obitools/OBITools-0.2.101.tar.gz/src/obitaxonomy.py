#!/usr/local/bin/python
'''
Created on 13 oct. 2009

@author: coissac
'''

from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.options import getOptionManager



if __name__ == '__main__':
    
    optionParser = getOptionManager([addTaxonomyDBOptions])

    (options, entries) = optionParser()
    
    loadTaxonomyDatabase(options)
    
    