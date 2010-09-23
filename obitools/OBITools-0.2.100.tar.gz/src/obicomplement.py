#!/usr/local/bin/python


from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.format.options import addInOutputOption, printOutput


if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    
    goodFasta = filterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            printOutput(options,seq.complement())
        else:
            printOutput(options,seq)

            