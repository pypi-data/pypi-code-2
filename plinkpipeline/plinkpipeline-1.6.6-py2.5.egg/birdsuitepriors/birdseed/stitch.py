
import sys
import os
import optparse
import mpgutils.utils as utils

def threecluster_reformat(line):
    line = line.split()
    line[0] = line[0].replace('"','')
    clust_aa = ' '.join(line[1:7])
    clust_ab = ' '.join(line[7:13])
    clust_bb = ' '.join(line[13:19])
    line = ';'.join([line[0],clust_aa,clust_ab,clust_bb]) + '\n'
    return line

def fivecluster_reformat(line):
    line = line.split()
    line[0] = line[0].replace('"','')
    clust_ao = ' '.join(line[1:7])
    clust_bo = ' '.join(line[7:13])
    clust_aa = ' '.join(line[13:19])
    clust_ab = ' '.join(line[19:25])
    clust_bb = ' '.join(line[25:31])
    line1 = ';'.join([line[0] + 'm',clust_ao,clust_bo]) + '\n'
    line2 = ';'.join([line[0],clust_aa,clust_ab,clust_bb]) + '\n'
    return line1 + line2

def twocluster_reformat(line,add_m):
    if add_m:
        append = 'm'
    else:
        append = ''
    line = line.split()
    line[0] = line[0].replace('"','') + append
    clust_ao = ' '.join(line[1:7])
    clust_bo = ' '.join(line[7:13])
    line = ';'.join([line[0],clust_ao,clust_bo]) + '\n'
    return line



def stitch(inDirectory, outputFile):
    f1_name = inDirectory+ '/' + 'auto_snps.seeds'
    f2_name = inDirectory+ '/' + 'xchr_snps.seeds'
    f3_name = inDirectory+ '/' + 'ychr_snps.seeds'
    f4_name = inDirectory+ '/' + 'mito_snps.seeds'
    g_name = outputFile
    g = open(outputFile,'w')

    if os.path.exists(f1_name):
        f = open(f1_name,'r')
        for line in f:
            g.write(threecluster_reformat(line))
        f.close()

    if os.path.exists(f2_name):
        f = open(f2_name,'r')
        for line in f:
            g.write(fivecluster_reformat(line))
        f.close()

    if os.path.exists(f3_name):
        f = open(f3_name,'r')
        for line in f:
            g.write(twocluster_reformat(line,1))
        f.close()
        
    if os.path.exists(f4_name):
        f = open(f4_name,'r')
        for line in f:
            g.write(twocluster_reformat(line,0))
        f.close()

    g.close()
    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-o", "--output", dest="outputFile",
                      help="""Where to write output.  Default: stdout""")
    
    parser.add_option("-i", "--inDirectory", dest="inDirectory",
                      help="""Where the files to be stiched together reside.""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=['outputFile', 'inDirectory']
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    print ("final output being assembled")        
    stitch(dctOptions.inDirectory, dctOptions.outputFile)
    print ("final output assembled at " + dctOptions.outputFile)
    
if __name__ == "__main__":
    sys.exit(main())

