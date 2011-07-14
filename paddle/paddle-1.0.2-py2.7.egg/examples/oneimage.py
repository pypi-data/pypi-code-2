'''
This script trains a dictionary over one image.

The image is always converted to grayscale.
'''

import sys
from optparse import OptionParser
import scipy as sp
import paddle

def parse_cl():
    # parse command line args
    op = OptionParser(usage='%prog imagefile [options]')
    op.add_option("-n", dest="nmax", type="int", default=0,
                  help="limit the number of training patches to INT",
                  metavar="INT")
    op.add_option("-p", dest="patchsize", type="int", default=12,
                  help="set the size of the patches to INTxINT (default 12)",
                  metavar="INT")
    op.add_option("-k", dest="dictsize", type="int", default=200,
                  help="set the size of the dictionary to INT (default 200)",
                  metavar="INT")
    op.add_option("--tau", dest="tau", type="float", default=0.5,
                  help="set the weight of sparsity penalty to FLOAT (default 0.5)", metavar="FLOAT")
    op.add_option("--npzfile", dest="npzfile", default=None,
                  help="save the results to PATH in npz format", metavar="PATH")
    op.add_option("--outpath", dest="outpath", default=None,
                  help="save to PATH three images with a sample of the training patches, the dictionary atoms and their dual filters, all arranged in tables", metavar="PATH")
    op.add_option("--nrows", dest="nrows", type="int", default=10,
                  help="set the number of rows of the tables to INT (default 10)", metavar="INT")
    op.add_option("--ncols", dest="ncols", type="int", default=20,
                  help="set the number of columns of the tables to INT (default 20)", metavar="INT")
    
    (options, args) = op.parse_args()
    
    if len(args) == 0:
        op.print_usage()
        print 'ERROR: an input image is required!'
        sys.exit(0)
    elif len(args) > 1:
        op.print_usage()
        print 'ERROR: too many arguments! (maybe should have been an option?)'
        sys.exit(0)

    if options.dictsize < (options.patchsize*options.patchsize):
        print 'INFO: the dictionary is not overcomplete (patchsize^2 > dictsize).'
    if options.outpath and options.dictsize < (options.nrows*options.ncols):
        print 'ERROR: trying to save too many atoms (nrows*ncols > dictsize).'
        sys.exit(0)
        
    return args[0], options

if __name__=='__main__':

    # parse the arguments
    path, opts = parse_cl()
    
    # load the image
    img = sp.misc.imread(sys.argv[1])

    # possibly convert to grayscale
    if img.ndim == 3:
        assert img.shape[2] <= 3, img.shape
        img = sp.mean(img, 2)

    # extract the patches
    h, w = opts.patchsize, opts.patchsize
    X = paddle.common.img2patches(img, size=(h, w), Nmax=opts.nmax)
    assert X.shape[0] == (h*w), X.shape

    # standardize the patches
    X -= sp.mean(X, 0).reshape((1, -1))

    # call paddle
    K = opts.dictsize
    D0, C0, U0 = paddle.dual.init(X, K)
    D, C, U, full_out = paddle.dual.learn(X, D0, C0, U0, tau=opts.tau, rtol=1.e-8)

    # save the results
    if opts.npzfile:
        sp.savez(opts.npzfile, D=D, C=C)

    if opts.outpath:
        # save an image with a subset of the patches
        paddle.common._saveDict(X, None, Nrows=opts.nrows, Ncols=opts.ncols, path='patches.png', sorted=False)
        paddle.common._saveDict(D, U, Nrows=opts.nrows, Ncols=opts.ncols, path='atoms.png', sorted=True)
        paddle.common._saveDict(C.T, U, Nrows=opts.nrows, Ncols=opts.ncols, path='filters.png', sorted=True)
