'''
Created on 13 oct. 2009

@author: coissac
'''

from obitools.format.sequence.embl import emblIterator
from obitools.format.sequence.genbank import genbankIterator
from obitools.format.sequence.fnaqual import fnaFastaIterator
from obitools.format.sequence.fasta import fastaAAIterator,fastaNucIterator,fastaIterator
from obitools.format.sequence.fastq import fastqIlluminaIterator,fastqSolexaIterator
from obitools.fastq import fastqSangerIterator
from obitools.fnaqual.quality import qualityIterator
from obitools.fasta import formatFasta, rawFastaIterator
from obitools.fastq import formatFastq

from obitools.format._format import printOutput

from array import array
from itertools import chain



def addInputFormatOption(optionManager):
    optionManager.add_option('--genbank',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='genbank',
                             help="input file is in genbank format")
    optionManager.add_option('--embl',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='embl',
                             help="input file is in embl format")

    optionManager.add_option('--fasta',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='fasta',
                             help="input file is in fasta nucleic format (including obitools fasta extentions)")

    optionManager.add_option('--raw-fasta',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='rawfasta',
                             help="input file is in fasta format (but more tolerant to format variant)")

    optionManager.add_option('--fna',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='fna',
                             help="input file is in fasta nucleic format produced by 454 sequencer pipeline")

    optionManager.add_option('--qual',
                             action="store", dest="withqualfile",
                             type='str',
                             default=None,
                             help="Specify the name of a quality file produced by 454 sequencer pipeline")

    optionManager.add_option('--sanger',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='sanger',
                             help="input file is in sanger fastq nucleic format (standard fastq)")

    optionManager.add_option('--solexa',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='solexa',
                             help="input file is in fastq nucleic format produced by solexa sequencer")

    optionManager.add_option('--illumina',
                             action="store_const", dest="seqinformat",
                             default=None,
                             const='illumina',
                             help="input file is in fastq nucleic format produced by old solexa sequencer")

    optionManager.add_option('--nuc',
                             action="store_const", dest="moltype",
                             default=None,
                             const='nuc',
                             help="input file is nucleic sequences")
    optionManager.add_option('--prot',
                             action="store_const", dest="moltype",
                             default=None,
                             const='pep',
                             help="input file is protein sequences")
        

def addOutputFormatOption(optionManager):
    optionManager.add_option('--fastq-output',
                             action="store_const", dest="output",
                             default=None,
                             const=formatFastq,
                             help="output sequences in sanger fastq format")
    optionManager.add_option('--fasta-output',
                             action="store_const", dest="output",
                             default=None,
                             const=formatFasta,
                             help="output sequences in obitools fasta format")
    optionManager.add_option('--uppercase',
                             action='store_true',dest='uppercase',
                             default=False,
                             help="Print sequences in upper case (defualt is lower case)")



def addInOutputOption(optionManager):
    addInputFormatOption(optionManager)
    addOutputFormatOption(optionManager)





def autoEntriesIterator(options):
    options.outputFormater=formatFasta
    options.outputFormat="fasta"
    
    def annotatedIterator(formatIterator):
        options.outputFormater=formatFasta
        options.outputFormat="fasta"
        def iterator(lineiterator):
            for s in formatIterator(lineiterator):
                s.extractTaxon()
                yield s

        return iterator

    def withQualIterator(qualityfile):
        options.outputFormater=formatFastq
        options.outputFormat="fastq"
        def iterator(lineiterator):
            for s in fnaFastaIterator(lineiterator):
                q = qualityfile.next()
                quality = array('d',(10.**(-x/10.) for x in q))
                s.quality=quality
                yield s
                
        return iterator

    def autoSequenceIterator(lineiterator):
        options.outputFormater=formatFasta
        options.outputFormat="fasta"
        first = lineiterator.next()
        if first[0]==">":
            if options.withqualfile is not None:
                qualfile=qualityIterator(options.withqualfile)
                reader=withQualIterator(qualfile)
                options.outputFormater=formatFastq
                options.outputFormat="fastq"
            elif options.moltype=='nuc':
                reader=fastaNucIterator
            elif options.moltype=='pep':
                reader=fastaAAIterator
            else:
                reader=fastaIterator
        elif first[0]=='@':
            reader=fastqSangerIterator
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
        elif first[0:3]=='ID ':
            reader=emblIterator
        elif first[0:6]=='LOCUS ':
            reader=genbankIterator
        else:
            raise AssertionError,'file is not in fasta, fasta, embl, or genbank format'
        
        input = reader(chain([first],lineiterator))
        
        return input
                
    if options.seqinformat is None:
        reader = autoSequenceIterator
    else:
        if options.seqinformat=='fasta':
            if options.moltype=='nuc':
                reader=fastaNucIterator
            elif options.moltype=='pep':
                reader=fastaAAIterator
            else:
                reader=fastaIterator
        elif options.seqinformat=='rawfasta':
            reader=annotatedIterator(rawFastaIterator)
        elif options.seqinformat=='genbank':
            reader=annotatedIterator(genbankIterator)
        elif options.seqinformat=='embl':
            reader=annotatedIterator(emblIterator)
        elif options.seqinformat=='fna':
            reader=fnaFastaIterator
        elif options.seqinformat=='sanger':
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            reader=fastqSangerIterator
        elif options.seqinformat=='solexa':
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            reader=fastqSolexaIterator
        elif options.seqinformat=='illumina':
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
            reader=fastqIlluminaIterator
            
        if options.seqinformat=='fna' and options.withqualfile is not None:
            qualfile=qualityIterator(options.withqualfile)
            reader=withQualIterator(qualfile)
            options.outputFormater=formatFastq
            options.outputFormat="fastq"
        
    return reader

        
    
    