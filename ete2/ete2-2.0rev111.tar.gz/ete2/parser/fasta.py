__VERSION__="ete2-2.0rev111" 
# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://ete.cgenomics.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the policy of the GPL copyleft license
# (2008-2010). ETE is developed in the context of a research
# community. References and citations to the specific methods
# implemented are indicated in the documentation of the corresponding
# functions.
#
# ETE original authors and references can be found in the last ETE
# publication:
#
# [1] ETE: a python Environment for Tree Exploration. Jaime
# Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon. BMC Bioinformatics
# 2010,:24doi:10.1186/1471-2105-11-24
#
# If you use ETE for your analysis, please support its development by
# citing the program.
#
# The ETE package is currently written and maintained by Jaime Huerta-Cepas
# (jhcepas@gmail.com)
#
# Documentation can be found at http://ete.cgenomics.org
#
# 
# #END_LICENSE#############################################################

import os
import string
from sys import stderr as STDERR

def read_fasta(source, obj=None):
    """ Reads a collection of sequences econded in FASTA format."""

    if obj is None:
        from ete2.coretype import seqgroup
        SC = seqgroup.SeqGroup()
    else:
        SC = obj

    names = set([])
    seq_id = -1

    # Prepares handle from which read sequences
    if os.path.isfile(source):
        _source = open(source, "rU")
    else:
        _source = iter(source.split("\n"))

    seq_name = None
    for line in _source:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        # Reads seq number
        elif line.startswith('>'):
            # Checks if previous name had seq
            if seq_id>-1 and SC.id2seq[seq_id] == "":
                raise Exception, "No sequence found for "+seq_name

            seq_id += 1
            # Takes header info
            seq_header_fields = map(string.strip, line[1:].split("\t"))
            seq_name = seq_header_fields[0]

            # Checks for duplicated seq names
            if seq_name in names:
                tag = str(len([k for k in SC.name2id.keys() if k.endswith(seq_name)]))
                old_name = seq_name
                seq_name = tag+"_"+seq_name
                print >>STDERR, "Duplicated entry [%s] was renamed to [%s]" %(old_name, seq_name)

            # stores seq_name
            SC.id2seq[seq_id] = ""
            SC.id2name[seq_id] = seq_name
            SC.name2id[seq_name] = seq_id
            SC.id2comment[seq_id] = seq_header_fields[1:]
            names.add(seq_name)

        else:
            if seq_name is None:
                raise Exception, "Error readind sequences: Wrong format."

            # removes all white spaces in line
            s = line.strip().replace(" ","")

            # append to seq_string
            SC.id2seq[seq_id] += s

    if seq_name and SC.id2seq[seq_id] == "":
        print >>STDERR, seq_name,"has no sequence"
        return None

    # Everything ok
    return SC

def write_fasta(sequences, outfile = None, seqwidth = 80):
    """ Writes a SeqGroup python object using FASTA format. """

    text =  '\n'.join([">%s\n%s" %( "\t".join([name]+comment), _seq2str(seq)) for
                       name, seq, comment in sequences])

    if outfile is not None:
        OUT = open(outfile,"w")
        OUT.write(text)
        OUT.close()
    else:
        return text

def _seq2str(seq, seqwidth = 80):
    sequence = ""
    for i in xrange(0,len(seq),seqwidth):
        sequence+= seq[i:i+seqwidth] + "\n"
    return sequence
