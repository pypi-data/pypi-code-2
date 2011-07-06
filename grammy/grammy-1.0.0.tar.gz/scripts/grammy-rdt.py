#!/usr/bin/env python

import optparse as op
import os, sys, platform, shutil, gzip
from Bio import SeqIO

BLD_DIR="build/lib.linux-%s-2.6/gem"
sys.path.append( BLD_DIR % platform.machine() )

from grammy import gemaux, gemlib, gemcore, gemmath, gemutil

"""suppose we have an o_prefix dir,
   all file paths are relative from that,
   rdt file is to be kept in o_prefix dir"""

def parse_reads( o_prefix, src_dir, i_suffix, name_change, seq_tech ):
  #
  for file in os.listdir( os.path.join( src_dir ) ):
    #
    if file.endswith(i_suffix):
      #
      print >>sys.stderr, "processing", file
      reads_src = None
      set_name = os.path.basename(file).rstrip(i_suffix)
      set_name = set_name in name_change and name_change[set_name] or set_name
      reads_src = os.path.join( src_dir, file )
      reads_tgt = os.path.join( o_prefix, '%s.fasta.gz' % set_name )
      if file.endswith('.gz'):
        #
        #print reads_src, reads_tgt
        shutil.copy2( reads_src, reads_tgt )
      else:
        #
        reads_content = open( reads_src, 'rb' )
        reads_tgt_file = gzip.open( reads_tgt, 'wb' )
        reads_tgt_file.writelines( reads_content )
        reads_tgt_file.close()
      reads_len = 0
      reads_no = 0
      for seq_rec in SeqIO.parse( gzip.open( reads_tgt ), "fasta" ):
        #
        reads_no += 1
        reads_len += len(seq_rec.seq)
      reads_file = '%s.fasta.gz' % set_name
      rdata = gemaux.Read_Data()
      rdata.read_tech = seq_tech
      rdata.read_length = reads_len/reads_no
      rdata.reads_file = reads_file
      rdata.reads_number = reads_no
      rdata.write( os.path.join(o_prefix,set_name) )

def main():
  #
  usage_error = """ type %s -h for more information """ % os.path.basename(sys.argv[0])
  usage = """ %prog [options] o_prefix i_prefix 

Arguments:
  o_prefix STRING       o_prefix,  the output will be o_prefix/xxx.rdt nd o_prefix/xxx.fasta.gz, use '.' for current directory
  i_prefix STRING       i_prefix,  a dir where reads file reside"""

  parser = op.OptionParser(usage, )
  #parser.add_option("-m","--mtx", dest="mtx", type="string", help="input read probability matrix file", metavar="FILE")
  parser.add_option("-s","--suf", dest="suf", type="string", help="read files suffix, default=fa.gz", default="fa.gz", metavar="STRING")
  parser.add_option("-t","--tec", dest="tec", type="string", help="sequencing tech, default=sanger", default="sanger", metavar="STRING")
  parser.add_option("-c","--chg", dest="chg", type="string", help="name change set 'o1:n1,o2:n2', default= ", default="", metavar="STRING")
  (options, args) = parser.parse_args()

  if len(args) != 2:
    #
    parser.error(usage_error)

  if options.chg:
    name_change = dict( [ v.split(':') for v in options.chg.split(',') ] )
  else:
    name_change = dict()
  o_prefix = args[0]
  src_dir = args[1]
  parse_reads( o_prefix=o_prefix, src_dir=src_dir, i_suffix=options.suf, name_change=name_change, seq_tech=options.tec )

if __name__ == "__main__":
  #
  main()
