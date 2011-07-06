#!/usr/bin/env python

import optparse as op
import os, sys, platform, time

BLD_DIR="build/lib.linux-%s-2.6/gem"
sys.path.append( BLD_DIR % platform.machine() )
from grammy import gemaux, gemlib, gemcore, gemmath, gemutil

def main():
  usage_error = """ type %s -h for more information """ % os.path.basename(sys.argv[0])
  usage = """ %prog [options] read_probability.mtx(s)
Arguments:
  read_probability.mtx: input probability matrix file"""

  parser = op.OptionParser(usage, )
  #parser.add_option("-m","--mtx", dest="mtx", type="string", help="input read probability matrix file", metavar="FILE")
  parser.add_option("-b","--btp", dest="btp", type="int", help="bootstrap number, default=10", default=10, metavar="INTEGER")
  parser.add_option("-t","--tol", dest="tol", type="float", help="tolerance for stopping, default=10e-6", default=.000001, metavar="FLOAT")
  parser.add_option("-c","--mtd", dest="mtd", type="string", help="convergenece method, (U)niform, (L)ikelihood, default=U", default='U', metavar="CHAR")
  parser.add_option("-n","--mit", dest="mit", type="int", help="maximum number of iteration, default=1000", default=1000, metavar="INTEGER")
  parser.add_option("-i","--ini", dest="ini", type="string", help="initilization method, (M)oment, (R)andom, default=M", default='M', metavar="CHAR")
  (options, args) = parser.parse_args()

  if len(args) != 1:
    parser.error(usage_error)
    
  gem = gemlib.pMONO()

  #mtx, btp, tol, mtd, mit, ini
  gem.prep( rdt=None, gdt=None, mmf=args[0].split(',') )                      #mmf is a list of matrix market files to be read in
  gem.em.init_V(options.ini)                                                          #init by moments
  tol = options.tol/gem.em.MN
  mle_start_time = time.time()                                                #time mark for MLE
  gem.status = gem.em.solve( options.tol, options.mit, options.mtd )                                  #in order: tolerance, max_iter, stopping rule
  mle_end_time = time.time()
  lld = gem.em.logL                                                           #log likelihood
  fvec = list(gem.em.V)                                                        #mixing parameter MLE
  print >>sys.stderr, "[%s] em: MLE solved in %s steps, %s seconds" % (sys.argv[0], gem.status, mle_end_time - mle_start_time)
  bootstrap_start_time = time.time()
  btps = gem.em.bootstrap( options.btp, options.tol, options.mit, options.ini, options.mtd )
  #in order: bootstrap_times, tolerance, max_iter, init_method, stopping rule
  bootstrap_end_time = time.time()
  print >>sys.stderr, "[%s] em: Bootstrapped %s times, %s seconds" % (sys.argv[0], options.btp, bootstrap_end_time - bootstrap_start_time)

  #output 
  #print os.path.splitext(args[0])
  prj,suffix = os.path.splitext(args[0])
  btp_fn = '.'.join( [prj, "btp"] )
  est_fn = '.'.join( [prj, "est"] )
  lld_fn = '.'.join( [prj, "lld"] )
  print >>open(btp_fn, 'w'), '\n'.join( [ '\t'.join(  [ "%.4g" % v for v in b ] ) for b in btps ] ) 
  print >>open(lld_fn, 'w'), lld
  print >>open(est_fn, 'w'), '\t'.join( [ "%.4g" % v for v in fvec ] )

if __name__ == "__main__":
  main()
