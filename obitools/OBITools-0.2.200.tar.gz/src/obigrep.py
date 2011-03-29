#!/usr/local/bin/python
'''
Created on 27 avr. 2010

@author: coissac
'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import sequenceFilterIteratorGenerator


if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    goodSeq   = sequenceFilterIteratorGenerator(options)

    writer = sequenceWriterGenerator(options)
    
    for seq in goodSeq(entries):
        writer(seq)
            
