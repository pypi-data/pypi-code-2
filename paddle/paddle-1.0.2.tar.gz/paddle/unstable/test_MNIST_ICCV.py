import sys
sys.path.append("../") 
from optparse import OptionParser, check_choice, OptionValueError
from test_MNIST_classification import *
import time

# [Ale] gestire parametro PCA

def update_results(method, mpar, results, nsamples, outfn, force, verbose):

    mkey, filelabel = methodkey(method, mpar)
    featfn = os.path.join(outpath, 'features_%s.npz' % filelabel)
    parsfn = os.path.join(outpath, 'parameters_%s.pkl' % filelabel)
    recfn = os.path.join(outpath, 'reconstructions_%s.png' % filelabel)

    if method == 'PADDLE_NMF':
        center = False
    else:
        center = True

    # learning step, if needed
    mnist = None
    if os.access(parsfn, os.R_OK) and not force:
        print ' reading from', parsfn
        pars = cPickle.load(open(parsfn))
    else:
        # load the MNIST dataset
        mnist = data.loadMNIST(path)
        train_set = mnist[0]
        # unsupervised feature learning on first 20k
        M = 50000
        X0 = preprocess(train_set[0], center)
        # V [Ale] qui sto facendo dictionary learning solo sui primi M: va fatto su tutti
        pars = METHODS[method]['lrn'](X0[:M], mpar, verbose=verbose)
        print ' saving to', parsfn
        cPickle.dump(pars, open(parsfn, 'w'))

    # compute the features, if needed
    if os.access(featfn, os.R_OK) and not mnist:
        print ' reading from', featfn
        npz = sp.load(featfn)
        Xtrn, Ytrn = npz['Xtrn'], npz['Ytrn']
        Xval, Yval = npz['Xval'], npz['Yval']
        Xtst, Ytst = npz['Xtst'], npz['Ytst']
    else:
        # delete any previous result related to the method
        results[mkey] = {}
        if os.access(recfn, os.R_OK):
            os.remove(recfn)
        # load the MNIST dataset
        if not mnist:
             mnist = data.loadMNIST(path)
        train_set, valid_set, test_set = mnist
        # encoding the rest
        X = {}
        elapsed = 0.
        for dataset, lbl in zip(mnist, ['trn', 'val', 'tst']):
            X0 = preprocess(dataset[0], center)
            start = time.time()
            X[lbl] = METHODS[method]['enc'](X0, pars)
            #paddle_pars = METHODS['PADDLE']['lrn'](X[lbl], 0.1, verbose=verbose)
            #X_pdd[lbl] = METHODS['PADDLE']['enc'](X, paddle_pars)
            elapsed += time.time() - start
            results[mkey]['rec_%s' % lbl] = compute_recs(X0, X[lbl], method, pars)[1:]
        results[mkey]['elapsed'] = elapsed
        Xtrn, Xval, Xtst = [X[lbl] for lbl in ['trn', 'val', 'tst']]
        # saves the reconstruction errors
        cPickle.dump(results, open(outfn, 'w'))
        # labels
        Ytrn = train_set[1]
        Yval = valid_set[1]
        Ytst = test_set[1]
        # saves
        print ' saving to', featfn
        sp.savez(featfn,
                 Xtrn=Xtrn, Ytrn=Ytrn,
                 Xval=Xval, Yval=Yval,
                 Xtst=Xtst, Ytst=Ytst)

    # save some reconstructions as images (using the test set)
    if not os.access(recfn, os.R_OK):
        if 'X0' not in dir():
            train_set, valid_set, test_set = data.loadMNIST(path)
            X0 = preprocess(test_set[0])
        N, d = X0.shape
        Ncols = 10
        Nrows = 3
        if 'pars' not in dir():
            pars = cPickle.load(open(parsfn))
        R, err_mean, err_std = compute_recs(X0, Xtst, method, pars)
        M = Ncols*Nrows
        subset = sp.random.permutation(N)[:M]
        R = R[subset].reshape((M, 28, 28))
        X0 = X0[subset].reshape((M, 28, 28))
        margin = 5
        img = 0.9 * X0.max() * sp.ones((2*28*Nrows+margin*(Nrows+1), 28*Ncols+margin*2), X0.dtype)
        for i in xrange(Ncols):
            for j in xrange(Nrows):
                x0, y0 = margin + i*28, margin + j*(56+margin)
                img[y0:y0+28, x0:x0+28] = X0[j*Ncols+i]
                y0 += 28
                img[y0:y0+28, x0:x0+28] = R[j*Ncols+i]
        pylab.gray()
        pylab.imsave(recfn, img)
    #bad
    reps = 3
    # classification
    for n in nsamples:

        if not n in results[mkey].keys():

            penalties = [1., 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3, 2.e-3, 1.e-3]
            if 'pen' in METHODS[method]:
                penalties = METHODS[method]['pen'][n]
            ### [Ale] gestire caso n==-1
            if n == -1:
                n = Xtrn.shape[0]
                print n
            start = time.clock()    
            Etrn, Eval, Etst = class_experiment(reps, n, Xtrn, Ytrn, Xval, Yval, Xtst, Ytst, penalties)
            results[mkey][n] = {
                'err_trn': (Etrn.mean(), Etrn.std()),
                'err_tst': (Etst.mean(), Etst.std()),
                'err_val': (Eval.mean(), Eval.std())
                }

            cPickle.dump(results, open(outfn, 'w'))
            print "It took %d seconds with %d samples" % ((time.clock()-start),n)

        #else:

            #print ' experiment already performed (method %s, parameter %f, training set size %d)' % (method, mpar, n)

    return None

def parse_cl():
    # parse command line args
    op = OptionParser(usage='%prog dataset [options]')
    op.add_option("-o", "--outpath", dest="outpath",
                  default='./results_MNIST_ICCV',
                  help="output PATH", metavar="PATH")
    op.add_option("-m", "--method", dest="method",
                  type="choice", choices=METHODS.keys(),
                  help="encoding method")
    op.add_option("-p", "--method-par", dest="mpar",
                  type="float",
                  help="set method parameter to FLOAT", metavar="FLOAT")
    op.add_option("-f", "--force", dest="force",
                  action="store_true", default=False,
                  help="forces the computation of the features")
    op.add_option("-v", "--verbose", dest="verbose",
                  action="store_true", default=False,
                  help="verbose output in dictionary learning")
    op.add_option("-s", "--show", dest="show",
                  action="store_true", default=False,
                  help="show and save figures")
    (options, args) = op.parse_args()
    
    if len(args) == 0:
        op.print_usage()
        print 'ERROR: the path to the MNIST dataset file is required!'
        sys.exit(0)
    elif len(args) > 1:
        op.print_usage()
        print 'ERROR: too many arguments! (maybe should have been an option?)'
        sys.exit(0)

    return args[0], options

if __name__=='__main__':

    path, options = parse_cl()
    outpath, method, mpar, verbose, force = options.outpath, options.method, options.mpar, options.verbose, options.force
    
    # creates the output path if not present
    if not os.access(outpath, os.W_OK):
        os.mkdir(outpath)

    W = 28 # image size for the MNIST dataset

    # load previous results
    outfn = os.path.join(outpath, 'results.pkl')
    if os.access(outfn, os.R_OK):
        results = cPickle.load(open(outfn))
    else:
        results = {}

    nsamples = [100]

    # possibly compute missing results
    if method != None:
        mkey = (method, mpar)
        # check if the results are there, if not compute them
        update_results(method, mpar, results, nsamples, outfn, force, verbose)
