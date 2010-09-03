##!/util/bin/python
#
#############################################################
## Assemble whole sample CNV calls                          #
##                                                          #
##   Arguments:                                             #
##     1) Birdseye file (<PLATE>.birdseye_calls)            #
##     2) output file (e.g. <PLATE>.cnvs)                   #
##     3) LOD score cutoff (e.g. 5)                         #
##     4) size cutoff (e.g. 10000)                          #
##                                                          #
#############################################################
#
#import sys
#import numpy
#from numpy import *
##import scipy
##import pylab
#
#
#def main(argv = None):  
#    if not argv:
#        argv = sys.argv
#    
#    lstRequiredOptions=["plateroot"]
#    parser = optparse.OptionParser(usage=__doc__)
#    
#    #OPTION PARSING!
#    global output_root, output_name
#
#    #REQUIRED
#    parser.add_option("-p", "--plateroot",
#                      help ="(Required) Define the directory where the data plate info resides")
#    #OPTIONAL
#    parser.add_option("-o", "--outputdir",
#                      help ="Define the directory for output files")
#    parser.add_option("-n", "--outputname", default="Output",
#                      help="define the file name root for the output files")
#    parser.add_option("-l", "--lodcut", default=5,
#                      help ="define a cutoff for confidence data")
#    parser.add_option("-m", "--sizecut", 
#                      help="CNV size cutoff")
#    parser.add_option("-q", "--quiet",
#                      action="store_true", dest="quiet")
#    
#    dctOptions, lstArgs = parser.parse_args(argv)
#    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
#        parser.print_help()
#        return 1
#        
#    #VALIDATE OUTPUT
#    if not dctOptions.outputdir:
#        setattr(dctOptions, 'outputdir', sys.path[0])
#    #VALIDATE PATHS
#    lstOptionsToCheck = ['familyfile', 'plateroot', 'outputdir']
#    if dctOptions.celmap:
#        lstOptionsToCheck.append("celmap")
#    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
#    
#    
#    LOD_cutoff = float(sys.argv[3])
#    size_cutoff = float(sys.argv[4])
#    
#    remainingsegments = pylab.load(sys.argv[1],delimiter='\t',skiprows=1, usecols=range(1,10))
#    outfile = sys.argv[2]
#    fileout = open(outfile,'w')
#    
#    num2id = {}
#    f = open(sys.argv[1],'r')
#    f.readline()
#    for line in f:
#        values = line.split()
#        num2id[int(values[1])] = values[0]
#    f.close()
#    
#    format = ['%d','%d','%d','%d','%d','%0.2f','%d','%d','%0.2f']
#    
#    #chunk segments file into sample-chromosomes
#    numsegsleft = size(remainingsegments,0)
#    while(numsegsleft>0):
#        i=1
#        while(i<numsegsleft and remainingsegments[i,0]==remainingsegments[i-1,0] and remainingsegments[i,2]==remainingsegments[i-1,2]):
#            i+=1
#    
#        segments = remainingsegments[0:i,:]
#        remainingsegments = remainingsegments[i:numsegsleft,:]
#        numsegsleft = size(remainingsegments,0)
#    
#        normal = 2
#        if(segments[0,2]==23): #then it's the X chromosome
#            if(sum(segments[segments[:,1]==1,6]) >
#               sum(segments[segments[:,1]==2,6])): #then it's a male
#                normal = 1
#    
#        # while there are segments that do not pass the lod score cutoff:
#        #  remove the segment with the lowest lod
#        #  merge segments on either side of the removed segment if possible (they are from the same sample and chromosome, and have the same copy number)
#        
#        segind = argmin(segments[:,8])
#        while(segments[segind,8]<LOD_cutoff):
#            prevind = segind - 1
#            nextind = segind + 1
#            if((prevind>=0) and (nextind<size(segments,0))):
#                if((segments[prevind,(0,1,2)]==segments[nextind,(0,1,2)]).all()):
#                    # mergable
#                    # print "merging"
#                    segments[prevind,:] = mergesegments(segments[(prevind,segind,nextind),:])
#                    segments = segments[r_[arange(0,segind), arange(nextind+1,size(segments,0))],:]
#                else:
#                    # print "not merging"
#                    segments = segments[r_[arange(0,segind), arange(nextind,size(segments,0))],:]
#            else:
#                segments = segments[r_[arange(0,segind), arange(nextind,size(segments,0))],:]
#            if(size(segments,0)==0):
#                break
#            segind = argmin(segments[:,8])
#        # print `segind` + "\t" + `segments[segind,8]`
#        # print segments[:,8]
#        # pylab.save('test.tmp', segments, fmt="%d%d%d%d%d%0.2f%d%d%0.2f")
#        # format = ['%d','%d','%d','%d','%d','%0.2f','%d','%d','%0.2f']
#        # print2darray(segments, format)
#    
#        # once all segments pass the lod cutoff, need to merge based on size
#        # for each copy-variant event that is smaller than the size cutoff, if it borders a copy-normal event that is also smaller than that the size cutoff, and after that copy-normal event is a segment that could be merged (that results in a copy-variable event with lod greater than the cutoff), then do the merge.
#        
#        # since only care about reporting copy-variable segments, pop every segment of normal copy number with size<cutoff, and merge segments on either side if resulting LOD will be positive.  The order of popping should be done by lowest LOD first.
#        # need special method to deal with males on chrX, where normal == 1; it is set above
#        
#        if(size(segments,0)==0):
#            continue
#    
#        temp = where((segments[:,6]<size_cutoff) & (segments[:,1]==normal))
#        poppablesegments = temp[0]
#        while(size(poppablesegments)>0):
#            segind = poppablesegments[argmin(segments[poppablesegments,8])]
#            prevind = segind - 1
#            nextind = segind + 1
#            if((prevind>=0) and (nextind<size(segments,0))):
#                if((segments[prevind,(0,1,2)]==segments[nextind,(0,1,2)]).all() and (segments[prevind,8]+segments[nextind,8]-segments[segind,8])>=LOD_cutoff):
#                    # mergable
#                    segments[prevind,:] = mergesegments(segments[(prevind,segind,nextind),:])
#                    segments = segments[r_[arange(0,segind), arange(nextind+1,size(segments,0))],:]
#                else:
#                    segments = segments[r_[arange(0,segind), arange(nextind,size(segments,0))],:]
#            else:
#                segments = segments[r_[arange(0,segind), arange(nextind,size(segments,0))],:]
#            temp = where((segments[:,6]<size_cutoff) & (segments[:,1]==normal))
#            poppablesegments = temp[0]
#            
#        if(size(segments,0)==0):
#            continue
#        
#        # print
#        # print2darray(segments, format)
#        #
#        # print
#        
#        temp = where((segments[:,6]>=size_cutoff) & (segments[:,1]!=normal))
#        segments = segments[temp[0],:]
#        
#        # print segments
#        # print2darray(segments,format)
#        
#        print2darraytofile(fileout, segments, format)
#    
#    fileout.close()
#        
#def mergesegments(segments):
#    newsegment = zeros(size(segments,1))
#    newsegment[0:3] = segments[0,0:3] #id, cn, chr
#    newsegment[3] = segments[0,3] #start
#    newsegment[4] = segments[2,4] #end
#    newsegment[6] = newsegment[4]-newsegment[3] #size
#    newsegment[7] = sum(segments[0:3,7]) #numprobes
#    if(newsegment[7]>=1000):
#        newsegment[8] = newsegment[7] #"LOD"
#        newsegment[5] = newsegment[7] #"perprobe LOD"
#    else:
#        newsegment[8] = segments[0,8]+segments[2,8]-segments[1,8] #LOD
#        newsegment[5] = 10**(newsegment[8]/newsegment[7]) #perprobe LOD
#    return newsegment
#
#def print1darraytofile(fileout, row, format):
#    assert size(row)==size(format)
#    outstring = num2id[row[0]]
#    for i in range(0,numcols):
#        outstring = outstring + "\t" + format[i] % row[i]
#    print >> fileout, outstring
#
#def print2darraytofile(fileout, segments, format):
#    if(size(shape(array))==1):
#        print1darraytofile(fileout, segments, format)
#        return
#    numcols = size(segments,1)
#    assert numcols==size(format)
#    for row in segments:
#        outstring = num2id[row[0]]
#        for i in range(0,numcols):
#            outstring = outstring + "\t" + format[i] % row[i]
#        print >> fileout, outstring
#
#def print1darray(row, format):
#    assert size(row)==size(format)
#    outstring = num2id[row[0]]
#    for i in range(0,numcols):
#        outstring = outstring + "\t" + format[i] % row[i]
#    print outstring
#
#def print2darray(segments, format):
#    if(size(shape(segments))==1):
#        print1darray(segments, format)
#        return
#    numcols = size(segments,1)
#    assert numcols==size(format)
#    for row in segments:
#        outstring = num2id[row[0]]
#        for i in range(0,numcols):
#            outstring = outstring + "\t" + format[i] % row[i]
#        print outstring
#
#if __name__ == "__main__":
#    main() 
