#!/usr/local/bin/python
'''
Created on 15 janv. 2010

@author: coissac
'''
from obitools import NucSequence
from string import lower


import math

from obitools.options import getOptionManager
from obitools.utils import ColumnFile
from obitools.align import FreeEndGap
from obitools.format.options import addInOutputOption, sequenceWriterGenerator



def addNGSOptions(optionManager):
    
    optionManager.add_option('-d','--direct',
                             action="store", dest="direct",
                             metavar="<PRIMER SEQUENCE>",
                             type="string",
                             default=None,
                             help="sequence of the direct primer")

    optionManager.add_option('-r','--reverse',
                             action="store", dest="reverse",
                             metavar="<PRIMER SEQUENCE>",
                             type="string",
                             default=None,
                             help="sequence of the reverse primer")

    optionManager.add_option('-l','--tag-length',
                             action="store", dest="taglength",
                             metavar="###",
                             type="int",
                             default=None,
                             help="length of the tag")

    optionManager.add_option('-t','--tag-list',
                             action="store", dest="taglist",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file containing tag used")
    
    optionManager.add_option('-1','--one-tag',
                             action="store_true", dest="onetag",
                             default=False,
                             help="Assert than only one tag in present on the direct primer")
    
    optionManager.add_option('-u','--unidentified',
                             action="store", dest="unidentified",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store unidentified sequences")
    

def readTagfile(filename):
    """
    data file describing tags and primers for each sample
    is a space separated tabular file following this format
    
    manip sample tag direct reverse partial
    
    
    reverse primer can be specified as - if necessary
    """
    
 
    tab=ColumnFile(filename,strip=True,
                            types=(str,str,lower,lower,lower,bool),
                            skip="#",
                            extra="@")
    primers = {}
    
    
    for p in tab:
        if len(p)==7:
            extra = p.pop()
        else:
            extra =None
        
        direct = p[3]
        tag    = p[2]
        
        if tag=='-':
            tag=None
            ltag=0
        else:
            ltag=len(tag)
            
        if direct not in primers:
            primers[direct]=(ltag,{})
        else:
            assert primers[direct][0]==ltag, \
            'Several tag length are associated for primer : %s' % direct
            
        reverse=p[4]
        if reverse not in primers[direct][1]:
            primers[direct][1][reverse]={}
            
        manip  = p[0]
        sample = p[1]
        
        assert tag not in primers[direct][1][reverse],'Same tag : %s used twice with primer %s' %(tag,direct)

        primers[direct][1][reverse][tag]=(manip,sample,True,extra)

        partial=p[5]
        
        if partial:
            if reverse not in primers:
                primers[reverse]=(ltag,{})
            else:
                assert primers[reverse][0]==ltag, \
                'Several tag length are associated for primer : %s' % direct
                
            if '-' not in primers[reverse][1]:
                primers[reverse][1]['-']={}
            
            assert tag not in primers[reverse][1]['-']
            
            primers[reverse][1]['-'][tag]=(manip,sample,False,extra)
            
    return primers   
        

def locatePrimer(sequence,finder):
    if len(sequence) > len(finder.seqB):
        finder.seqA=sequence
        ali=finder()
    #    print ali
        if ali.score >= len(finder.seqB)*4-4:
            return ali.score,ali[1].gaps[0][1],len(ali[1])-ali[1].gaps[-1][1]
    return None 

def annotate(sequence,options):
    
    alid,alir=None,None
    pdirect,preverse=None,None
    direct,reverse=None,None
    ltag=None
    tdirect,treverse=None,None
    fragment = None
    warning=[]
    good=True
    
    if hasattr(sequence, "quality"):
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality),0)/len(sequence.quality)*10
        sequence['avg_quality']=q
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[0:10]),0)
        sequence['head_quality']=q
        if len(sequence.quality[10:-10]) :
            q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[10:-10]),0)/len(sequence.quality[10:-10])*10
            sequence['mid_quality']=q
        q = -reduce(lambda x,y:x+y,(math.log10(z) for z in sequence.quality[-10:]),0)
        sequence['tail_quality']=q
        
        
    ip = iter(options.finder)
    
                    #
                    # Iterate over the direct primers
                    # until one match on direct or reverse strand
                    #
                    
    while direct is None:
        try:
            alid,alir=ip.next()
            strand=True
            direct = locatePrimer(sequence, alid)
            if direct is None:
                strand = False
                direct = locatePrimer(sequence, alir)
        except StopIteration:
            break 
        
                    # If a direct primer match
                    # look for corresponding reverse primer
                    # on the ooposite strand
                    
    if direct is not None:
        pdirect=str(alid.seqB)
        
        reverse=None
        ip = iter(options.primers[pdirect][1])
        while reverse is None:
            try:
                alid,alir=options.rfinder[ip.next()]
                if strand:
                    alig=alir
                else:
                    alig=alid
                reverse=locatePrimer(sequence, alig)
            except StopIteration:
                break
        
                # if direct and reverse primers are found then 
                # compute the length of the applicon
        
        if reverse is not None:
            preverse=str(alid.seqB)
            if strand :
                lampli = reverse[1]-direct[2]
            else:
                lampli = direct[1]-reverse[2]
        
                # Check for tags if present
            
        ltag = options.primers[pdirect][0]
        
        if ltag :
            if strand:
                endtag = direct[1]
                starttag=endtag - ltag 
                tdirect = str(sequence[starttag:endtag])
            else:
                starttag=direct[2]
                endtag=starttag + ltag
                tdirect = str(sequence[starttag:endtag].complement())
                
            if tdirect is not None and len(tdirect)!=ltag:
                tdirect=None

            if reverse is not None:
                if strand:
                    starttag=reverse[2]
                    endtag=starttag + ltag
                    treverse = str(sequence[starttag:endtag].complement())
                else:
                    endtag = reverse[1]
                    starttag=endtag - ltag 
                    treverse = str(sequence[starttag:endtag])
                    
                if treverse is not None and len(treverse)!=ltag:
                    treverse=None
                    
                    
                # both primers are found
                
    if direct is not None and reverse is not None:
        if strand:
            fragment = sequence[direct[2]:reverse[1]]
        else:
            fragment = sequence[reverse[2]:direct[1]].complement()
            
        if hasattr(sequence, 'quality'):
            if strand:
                quality = sequence.quality[direct[2]:reverse[1]]
            else:
                quality = sequence.quality[reverse[2]:direct[1]]
                quality.reverse()
        else:
            quality=None
            
                # Only direct primer is found
                
    elif direct is not None and reverse is None:
        if strand:
            print "direct partial"
            fragment = sequence[direct[2]:]
        else:
            print "reverse partial"
            fragment = sequence[0:direct[1]].complement()
        if hasattr(sequence, 'quality'):
            if strand:
                quality = sequence.quality[direct[2]:]
            else:
                quality = sequence.quality[0:direct[1]]
                quality.reverse()
                
    
        
    if fragment is not None:
        if len(fragment) > 0:
            if quality is not None:
                fragment.quality=quality
                        
            if direct is not None:
                fragment['direct_primer']=pdirect
                
                if strand:
                    fragment['direct_match']=str(sequence[direct[1]:direct[2]])
                else:
                    fragment['direct_match']=str(sequence[direct[1]:direct[2]].complement())
            
                fragment['direct_score']=direct[0]
                
                if ltag:
                    fragment['tag_length']=ltag
                    if tdirect is not None:
                        fragment['direct_tag']=tdirect
                    else:
                        warning.append('No direct tag')
                        
            if reverse is not None:
                fragment['reverse_primer']=preverse
                
                if strand:
                    fragment['reverse_match']=str(sequence[reverse[1]:reverse[2]].complement())
                else:
                    fragment['reverse_match']=str(sequence[reverse[1]:reverse[2]])
            
                fragment['reverse_score']=reverse[0]
    
                if ltag:
                    if treverse is not None:
                        fragment['reverse_tag']=treverse
                    else:
                        warning.append('No reverse tag')
                        
                        
                    if (tdirect is not None and 
                        (treverse is not None or options.onetag)) :
                        if tdirect!=treverse and not options.onetag:
                            warning.append('discrepancy between tags')
                        elif tdirect in options.primers[pdirect][1][preverse]:
                            fragment['experiment']=options.primers[pdirect][1][preverse][tdirect][0]
                            fragment['sample']=options.primers[pdirect][1][preverse][tdirect][1]
                            extra=options.primers[pdirect][1][preverse][tdirect][3]
                            if extra is not None:
                                for k in extra:
                                    fragment[k]=extra[k]
                        else:
                            warning.append('unused sample tags')
                        
                        
            else:
                warning.append('No reverse primer match')
                
        else:
            fragment['error']="Overlapping Primers"
            good=False
    else:
        fragment=sequence
        fragment['error']="No primer match"
        good=False

    if warning:
        fragment['warning']=warning
        
    #print
    #print pdirect,preverse,strand,direct,reverse,lampli,tdirect,treverse
    return good,fragment
            


if __name__ == '__main__':
    
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    optionParser = getOptionManager([addNGSOptions,addInOutputOption])
                                    
    
    (options, entries) = optionParser()

    assert options.direct is not None or options.taglist is not None, \
         "you must specify option -d ou -t"
         
    if options.taglist is not None:
        primers=readTagfile(options.taglist)
    else:
        options.direct=options.direct.lower()
        options.reverse=options.reverse.lower()
        primers={options.direct:(options.taglength,{})}
        if options.reverse is not None:
            reverse = options.reverse
        else:
            reverse = '-'
        primers[options.direct][1][reverse]={'-':('-','-',True,None)}
        
    options.primers=primers

    direct=[]
    reverse={}
    
    for p in options.primers:
        alid = FreeEndGap()
        alir = FreeEndGap()
        alid.match=4
        alid.mismatch=-2
        alid.opengap=-2
        alid.extgap=-2
        alid.seqB=NucSequence('primer',p)
        alir.match=4
        alir.mismatch=-2
        alir.opengap=-2
        alir.extgap=-2
        alir.seqB=alid.seqB.complement()
        direct.append((alid,alir))
        for r in options.primers[p][1]:
            alid = FreeEndGap()
            alir = FreeEndGap()
            alid.match=4
            alid.mismatch=-2
            alid.opengap=-2
            alid.extgap=-2
            alid.seqB=NucSequence('primer',r)
            alir.match=4
            alir.mismatch=-2
            alir.opengap=-2
            alir.extgap=-2
            alir.seqB=alid.seqB.complement()
            reverse[r]=(alid,alir)
            
    
    options.finder=direct
    options.rfinder=reverse
        
    if options.unidentified is not None:
        unidentified = open(options.unidentified,"w")
    
    writer = sequenceWriterGenerator(options)
    if options.unidentified is not None:
        unidentified = sequenceWriterGenerator(options,open(options.unidentified,"w"))
    else :
        unidentified = None
        
    for seq in entries:
        good,seq = annotate(seq,options)
        if good:
            writer(seq)
        elif unidentified is not None:
            unidentified(seq)
            
    
    