#!/usr/local/bin/python
'''
Created on 6 juil. 2010

@author: coissac
'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.format.sequence import autoSequenceIterator

def addSelectOptions(optionManager):
    
    optionManager.add_option('-i','--identifier',
                             action="store", dest="identifier",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file containing sample sequences to select on "
                                  "on the base of their identifier")

    optionManager.add_option('-v',
                             action="store_true", dest="invert",
                             default=False,
                             help="invert selection")




if __name__ == '__main__':
    optionParser = getOptionManager([addSelectOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    
    idset=set(x.strip() for x in  open(options.identifier))
    writer = sequenceWriterGenerator(options)
    
    def invert(x):
        if options.invert:
            return not x
        else:
            return x
    
    for seq in entries:
        if invert(seq.id in idset):
            writer(seq)
        
