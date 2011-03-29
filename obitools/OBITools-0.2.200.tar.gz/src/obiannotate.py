#!/usr/local/bin/python


from obitools.options import getOptionManager
from obitools.options.bioseqfilter import addSequenceFilteringOptions
from obitools.options.bioseqfilter import filterGenerator
from obitools.options.bioseqedittag import addSequenceEditTagOptions
from obitools.options.bioseqedittag import sequenceTaggerGenerator
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
        
    
if __name__=='__main__':
    
    optionParser = getOptionManager([addSequenceFilteringOptions,
                                     addSequenceEditTagOptions,
                                     addInOutputOption])

    (options, entries) = optionParser()
    
    writer = sequenceWriterGenerator(options)
    
    sequenceTagger = sequenceTaggerGenerator(options)
    goodFasta = filterGenerator(options)
    
    for seq in entries:
        if goodFasta(seq):
            sequenceTagger(seq)
        writer(seq)
            
