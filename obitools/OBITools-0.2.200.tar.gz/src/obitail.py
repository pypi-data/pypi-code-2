#!/usr/local/bin/python
'''
Created on 15 dec. 2009

@author: coissac
'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
import collections

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
    
    queue = collections.deque(entries,options.count)

    writer = sequenceWriterGenerator(options)
   
    while queue:
        writer(queue.popleft())
        
        
        

