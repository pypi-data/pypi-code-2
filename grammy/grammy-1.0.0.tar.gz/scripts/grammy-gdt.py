#!/usr/bin/env python

import optparse as op
import os, sys, platform

BLD_DIR="build/lib.linux-%s-2.6/gem"
sys.path.append( BLD_DIR % platform.machine() )
from grammy import gemaux, gemlib, gemcore, gemmath, gemutil

def main():
  usage_error = """ type %s -h for more information """ % os.path.basename(sys.argv[0])
  usage = """ %prog [options] o_prefix taxids
  
Arguments:
  o_prefix: STRING      o_prefix.gdt will be the output filename
  taxids: t1,t2,...,tm  each tid t? is a INTEGER and must be found in grefs/gid_tid.dmp"""

  parser = op.OptionParser(usage, )
  #parser.add_option("-m","--mtx", dest="mtx", type="string", help="input read probability matrix file", metavar="FILE")
  parser.add_option("-d","--dmp", dest="dmp", type="string", help="gid to tid dump file, default=grefs/gid_tid.dmp", default="grefs/gid_tid.dmp", metavar="STRING")
  parser.add_option("-r","--ref", dest="ref", type="string", help="reference genome dir, default=grefs", default="grefs", metavar="STRING")
  parser.add_option("-p","--per", dest="per", type="int", help="number of genomes per file, default=20", default=20, metavar="INTEGER")
  (options, args) = parser.parse_args()

  if len(args) != 2:
    parser.error(usage_error)

  taxids = [int(v) for v in args[1].split(',')]
  o_prefix = args[0]
  gdata = gemaux.Genome_by_gref( taxids=taxids, o_prefix=o_prefix, dmp_file=options.dmp, gref_dir=options.ref, per_set=options.per ) 
  gdata.write( o_prefix )

if __name__ == "__main__":
  main()
