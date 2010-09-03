# Reads a summary file (output using the sumz option of apt-probeset-genotype),
# gets the answer from a hapmap lookup file, and rewrites the file in a more convenient format.
# Note that the NA descriptors must be contained in the columns of the input sumz file.
#
# Syntax: sumz_reformat.py [file names are all set as internal variables, see below]

import sys,re
import optparse
import mpgutils.utils as utils
from mpgutils import fk_utils

numlines_sample = 100000  # how many SNPs to sample to get an average intensity

key_begin = 1  # the column number (0-based numbering) in which the hapmap answers start in

#input_fname = '/humgen/cnp04/sandbox/SNP6.0/N270/270final/sumz/quant-norm.pm-only.sumz.plier.summary.txt'
#hapmap_answers_fname = '/humgen/cnp04/sandbox/SNP6.0/snp6_info/ref_tables/rerevised_GenomeWideSNP_6.HapMap270.txt'
    
# The older answer key was here: /humgen/cnp04/sandbox/SNP6.0/priors/reviser/answerkey.revised.txt

#output_fname = 'sumz_hapmap.txt'

na_get = re.compile('NA\d+',re.IGNORECASE)

def loadGender(genderFile):
     dctGender={}
     f = open(genderFile,'r')
     for strLine in f:
        if not strLine.startswith("sampleID"): #skip any lines with "#"
            line=strLine.split()
            dctGender[line[0]]=line[1]
     f.close()
     return (dctGender)
                       
def extract_na(colname):
    na_match = na_get.search(colname)
    if na_match:
        return na_match.group().upper()
    else:
        sys.exit("Could not extract NA # from %s!" % colname)

def get_answers(snp, hapmap_key, sample_hapmap_index):
    return [hapmap_key[snp][i] for i in sample_hapmap_index]

def floatformat(x):
    return "%2.4f" % x

# First figure out the average intensity so that you can divide by it, making your new average intensity = 1

def calculateAverageIntensity(inFile, strMissingValueLabel):
    print "Calculating the average intensity..."

    line = '#'
    f = open(inFile,'r')

    while line[0] == '#':
        line = f.readline()

    f.readline()  # discard the table header line

    total = 0
    probes_sampled = 0
    lines_sampled=0
    for line in f:
        if (lines_sampled >= numlines_sample): break
        line = line.split()
        num_cols = len(line)
        for k in range(1,num_cols):
            if line[k]!=strMissingValueLabel:
                total += float(line[k])
                probes_sampled += 1
        lines_sampled=lines_sampled+1
        
    f.close()

    average_intensity = total / probes_sampled
    print "The average intensity is: %2.2f" % average_intensity
    return (average_intensity)

def loadHapmapAnswers(hapmap_answers_fname):
    
    # Now load the hapmap priors

    print "Loading hapmap data..."

    f = open(hapmap_answers_fname,'r')

    line = '#'
    while line[0] == '#':
        line = f.readline()

    hapmap_header = line.split()
    hapmap_header = hapmap_header[key_begin:]
    #print hapmap_header

    hapmap_key = {}
    counter=0
    
    for line in f:
        line = line.split()
        hapmap_key[line[0]] = line[key_begin:]
        counter=counter+1
        if (counter%50000==0): print str(counter)
    
    f.close()
    return (hapmap_key, hapmap_header)

def processLine(a_line, b_line, hapmap_key, sample_hapmap_index, average_intensity, strMissingValueLabel, out):
    snp = a_line[0][0:-2]
    if snp != b_line[0][0:-2]:
        sys.exit("Mismatched SNPs!  %s %s Exiting" % (snp,b_line[0]))
    missingDataIndex=fk_utils.indices(a_line,  strMissingValueLabel)
    if len(missingDataIndex)>0:
        a_line= fk_utils.arbNegSlice(a_line, missingDataIndex)
    
    missingDataIndex=fk_utils.indices(b_line,  strMissingValueLabel)
    if len(missingDataIndex)>0:
        b_line= fk_utils.arbNegSlice(b_line, missingDataIndex)
    
    a_thetas = [float(e)/average_intensity for e in a_line[1:]]
    b_thetas = [float(e)/average_intensity for e in b_line[1:]]
    snp_answers = get_answers(snp, hapmap_key, sample_hapmap_index)

    out.write(snp)
    for i in xrange(0,len(a_thetas)):
        out.write(';' + snp_answers[i] + ' ' + floatformat(a_thetas[i]) + ' ' + floatformat(b_thetas[i]))
    out.write('\n')
    
    
def processHeader(headerLine, hapmap_header, gender_dictionary, out):
    
    source_header = headerLine.split()

    source_header = [extract_na(e) for e in source_header[1:]]
    #print source_header
    sample_hapmap_index = [hapmap_header.index(e) for e in source_header]
    
    #print sample_hapmap_index

    num_samples = len(source_header)        
    out.write('probeset_id')
    for na in source_header:
        if na in gender_dictionary:
            out.write('\t' + gender_dictionary[na])  # Writes the first line which has gender info
        else:
            print ("Sample missing from gender dictionary:" + na + " quitting!")
            sys.exit(1)
    out.write('\n')
    return (sample_hapmap_index)
        
# Now we go back and reformat the source summary file with the hapmap answers interpolated
def writeSumZ(input_fname, strMissingValueLabel, hapmap_answers_fname, hapmapGenderFile, output_fname):
    gender_dictionary=loadGender(hapmapGenderFile)
    average_intensity=calculateAverageIntensity(input_fname, strMissingValueLabel)
    hapmap_key,hapmap_header=loadHapmapAnswers(hapmap_answers_fname)
    
    print "Writing out the new table..."

    f = open(input_fname,'r')
    out = open(output_fname,'w')
    
    #read 2 lines at a time.
    a_line=None
    for strLine in f:
        if not strLine.startswith("#"): #skip any lines with "#"
            if strLine.startswith("probeset_id"): #header line.
               sample_hapmap_index=processHeader(strLine, hapmap_header, gender_dictionary, out)               
            else:   
                if a_line is None:
                    a_line=strLine.split()
                else:    
                    b_line=strLine.split()
                    processLine(a_line, b_line, hapmap_key, sample_hapmap_index, average_intensity, strMissingValueLabel, out)
                    a_line=None
            
    out.close()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-o", "--output", dest="output_fname",
                      help="""Where to write output.  Default: stdout""")
    
    parser.add_option("-i", "--intensity_file", dest="input_fname",
                      help="""Intensity summary file, (output using the sumz option of apt-probeset-genotype).  Can be
                      generated by other programs.  The first column name is probeset_id, followed by sample names.  
                      Each row contains the intensity information for an A or B probe for those samples (with a -A or -B 
                      to indicate which allele is being measured.)  
                      Example: 
                      probeset_id     NA06985_GW6-R_P2RJ_C_F3.CEL     NA06991_GW6-R_P2RJ_C_E5.CEL
                      SNP_A-2131660-A 1403.81353      1175.07797
                      SNP_A-2131660-B 1507.16102      1160.32130      2240.28761""")
    
    parser.add_option("--genotype_file", dest="hapmap_answers_fname",
                      help="""Hapmap genotype file.  Each row is a SNP, each column an individual.  
                      SNPS should match the SNPs in the intensity file.
                      Example:
                      probeset_id     NA06985 NA06991
                      AFFX-SNP_10000979       1       1""")
    
    parser.add_option("--genderFile", dest="hapmapGenderFile",
                      help="""Hapmap gender file.  Contains two columns, the sample ID, and a 1 for males, 2 for females.  The file is tab seperated.""") 
    
    parser.add_option("-m", "--missing_value_label", dest="strMissingValueLabel", default="NaN", 
                      help="""Label of data that is missing from the platform. 
Illumina products do not always have data available for every probe/individual combination. 
Default is %default.""")


    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=['output_fname', 'input_fname', 'hapmap_answers_fname', 'hapmapGenderFile']
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
        
    writeSumZ(dctOptions.input_fname, dctOptions.strMissingValueLabel, dctOptions.hapmap_answers_fname, dctOptions.hapmapGenderFile, dctOptions.output_fname)
    
        
if __name__ == "__main__":
    sys.exit(main())
