#!/usr/local/bin/python
'''
Created on 15 dec. 2009

@author: coissac
'''
import sys
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager


def addHeadOptions(optionManager):
    optionManager.add_option('-n','--sequence-count',
                             action="store", dest="count",
                             metavar="###",
                             type="int",
                             default=10,
                             help="Count of first sequences to print")
    

if __name__ == '__main__':
    optionParser = getOptionManager([addHeadOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    i=0

    writer = sequenceWriterGenerator(options)
    
    for s in entries:
        if i < options.count:
            writer(s)
            i+=1
        else:
            sys.exit(0)
            
        

