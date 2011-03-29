#!/usr/local/bin/python


from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
import math


def addDistributeOptions(optionManager):
    
    optionManager.add_option('-p','--prefix',
                             action="store", dest="prefix",
                             metavar="<PREFIX FILENAME>",
                             type="string",
                             default="",
                             help="prefix added at each file name")

    optionManager.add_option('-n','--number',
                             action="store", dest="number",
                             metavar="###",
                             type="int",
                             default=None,
                             help="Number of parts")
    
if __name__=='__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addDistributeOptions,addInOutputOption])
    
    (options, entries) = optionParser()
    
    assert options.number is not None, "You must specify the number of parts"
    
    digit = math.ceil(math.log10(options.number))
    out=[]

    template = "%s_%%0%dd.%s" % (options.prefix,digit,options.outputFormat)
    out=[sequenceWriterGenerator(options,
                                 open(template % (i+1),"w"))
         for i in xrange(options.number)
        ]
    
    i = 0
    for seq in entries:
        out[i](seq)
        i+=1
        i%=options.number
        
    del out
    
            
    
