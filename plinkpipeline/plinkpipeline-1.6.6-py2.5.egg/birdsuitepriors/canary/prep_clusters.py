#!/usr/bin/env python

from __future__ import division
import sys
import mpgutils.fk_utils as fk
import mpgutils.utils as utils
import optparse

min_variance = 0.0001

def float_format(x):
    return "%2.4f" % x

def convertNA(x):
    return "-1" if x=="NA" else x
    
def readMaxtix(file, bVerbose=False):
    f = open(file)
    header = f.readline().split()
    header.pop(0)
    header = [fk.extract_na(e) for e in header]
    result={}
    for line in f:
        fields = line.split()
        fields=[convertNA(x) for x in fields]
        result[fields[0]] = [float(e) for e in fields[1:]]

    f.close()
    if (bVerbose):
        print header,len(header)
        
    return (header, result)

def processCNVs(intensities_header, genotypes_header, dctIntensities, dctGenotypes, outFile):
    out = open(outFile,'w')
    
    matchup = [intensities_header.index(e) for e in genotypes_header]
    cluster_intensities = {}
    cnvNames=dctGenotypes.keys()
    for cnv in cnvNames:
        genotypes=dctGenotypes[cnv]
        genotypes=[int(x) for x in genotypes]
        
        print cnv
        unique_genotypes = fk.unique(genotypes)
        unique_genotypes.sort()
        if unique_genotypes[0] == -1:
            unique_genotypes.pop(0)
        if len(unique_genotypes) == 0:
            continue
        total_genotypes = 0
        if cnv not in dctIntensities:
            print "cnv " + cnv + " not found in intensities"
            continue
        for genotype in unique_genotypes:
            genotype_indices = fk.indices(genotypes,genotype)
            relevant_intensities_indices = fk.arbslice(matchup,genotype_indices)
            relevant_intensities = fk.arbslice(dctIntensities[cnv],
                                               relevant_intensities_indices)
            cluster_intensities[genotype] = relevant_intensities
            total_genotypes += len(relevant_intensities)
        out.write(cnv)
        out.write(' ' + str(len(unique_genotypes)))
        for genotype in unique_genotypes:
            out.write(' ' + str (genotype))
        for genotype in unique_genotypes:
            out.write(' ' + float_format(len(cluster_intensities[genotype]) /
                                       total_genotypes))
        for genotype in unique_genotypes:
            out.write(' ' + float_format(fk.mean(cluster_intensities[genotype])))
        for genotype in unique_genotypes:
            var = fk.variance(cluster_intensities[genotype])
            if (var < min_variance):
                var = min_variance
            if str(var) == 'NaN':
                var = min_variance
            out.write(' ' + float_format(var))
        out.write('\n')

    out.close()
    
def main (argv=None):
    if argv is None:
        argv = sys.argv
        
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-i", "--intensities", default=None, dest="intensities",
                      help="""intensities file, with the same samples/regions as the genotypes file.""")
    
    parser.add_option("-g", "--genotypes", default=None, dest="genotypes", 
                      help="""genotypes file, with the same samples/regions as the intensities file.""")
   
    parser.add_option("-o", "--output", default=".", dest="output", 
                      help="""Where to write the cluster file.""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=["intensities", "genotypes", "output"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    intensities_fname=dctOptions.intensities
    genotypes_fname=dctOptions.genotypes
    outFile=dctOptions.output
    
    intensities_header, dctIntensities = readMaxtix(intensities_fname)
    genotypes_header, dctGenotypes = readMaxtix (genotypes_fname)
    
    processCNVs(intensities_header, genotypes_header, dctIntensities, dctGenotypes, outFile)
    print "Done"

if __name__ == "__main__":
    sys.exit(main())
