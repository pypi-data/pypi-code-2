'''
Experimental protocol:
 - 50k training set / 10k validation set / 10k test set
 - per-image preprocessing: standardize pixel values
 - extract global feature vector (256-dimensional in kavukcuoglu08)
 - train and test a classifier:
   - a linear regularized log-reg classifier (e.g. kavukcuoglu08)
'''

import sys, os, glob, scipy, pylab, warnings, time
sys.path.append("../") 
from optparse import OptionParser, check_choice, OptionValueError
import scipy as sp
import scipy.stats
from scikits.learn.linear_model import LogisticRegression
from scikits.learn.grid_search import GridSearchCV
from scikits.learn.pca import PCA
import cPickle, gzip
import paddle, dual, dual_l1, tight2
import data
from common import sparsity
import time

def compute_support(U, rtol=1.e-3):
    # Uabs = sp.absolute(U)
    # i = sp.indices(Uabs.shape)[0]
    # j = sp.argsort(Uabs, 1)
    # Usorted = Uabs[i, j]
    # Um = sp.mean(Usorted, 0)
    # supp = sp.where(Um > rtol*Um.max(), 1, 0)
    # K = supp.sum()
    K = sp.sum(sp.where(U != 0, 1, 0), 1).mean()
    print ' Average support has %d atoms (over %d)' % (K, U.shape[1])
    return int(K)#, i, j

def compute_threshold(U, CX, rtol=1.e-3):
    assert U.shape == CX.shape
    #K, i, j = compute_support(U, rtol)
    K = compute_support(U)
    CXabs = sp.absolute(CX)
    i = sp.indices(CXabs.shape)[0]
    j = sp.argsort(CXabs, 1)
    ts = CXabs[i[:,-K-1],j[:,-K-1]]
    print ' Mean threshold = %.2f (sd = %.2f)' % (ts.mean(), ts.std())
    t = ts.mean() + ts.std()
    print ' Optimal threshold set to = %.2f' % t
    return t

def restrict_support(X, k):
    #n = sp.sqrt(sp.sum(X**2, 1)).reshape((-1, 1))
    Xabs = sp.absolute(X)
    i = sp.indices(Xabs.shape)[0]
    j = sp.argsort(Xabs, 1)
    X[i[:,:-k],j[:,:-k]] = 0
    #n /= sp.sqrt(sp.sum(X**2, 1)).reshape((-1, 1))
    #X *= n
    return X

def preprocess(X, center=True):
    assert X.shape[1] == 28*28, X.shape
    if center:
        X -= sp.mean(X, 1).reshape((-1, 1))
    X /= sp.std(X, 1).reshape((-1, 1))
    return X

def raw_trn(X, par, **kwargs):
    return X, None

def raw(X, dummy):
    return X

def _ist(X, D, tau, eta=0., C=None):
    p = {'tau': tau, 'mu': 0., 'eta': eta, 'verbose': False, 'rtol': 1.e-4, 'nnU': False, 'nnD': False}
    U0 = sp.zeros((D.shape[1], X.shape[0]), sp.float32)
    U, full_out = dual._ist(X.T, U0, D, C, p, maxiter=1000)
    return U.T


########## learning methods

def pca_trn(X, par, **kwargs):
    # V [Ale] qui bisogna usare par per determinare il numero di componenti
    _pca_check = PCA(whiten=True)
    _pca_check.fit(X)
    n_components = sp.searchsorted(sp.cumsum(_pca_check.explained_variance_ratio_), 0.99)+1
    _pca = PCA(n_components, whiten=True)
    _pca.fit(X)
    print "number of principal components: ", n_components
    return _pca

def _paddle(X, tau, eta, K=256, verbose=False, rtol=1.e-4, nmf=False):
    D0, C0, U0 = dual.init(X.T, K)
    if nmf:
        C0 = sp.clip(C0, 0, sp.inf)
        U0 = sp.clip(U0, 0, sp.inf)
    D, C, U, full_out = dual.learn(X.T, D0, C0, U0, verbose=verbose, tau=tau, eta=eta, mu=0, rtol=rtol, nnU=nmf, nnD=nmf)
    return D, C, U, full_out

def l1dl_lrn(X, tau, **kwargs):
    D, C, U, full_out = _paddle(X, tau, eta=0)
    pars = D, tau
    return pars

def paddle_lrn(K, eta=1., nmf=False):
    def _paddle_lrn(X, tau, **kwargs):
        D, C, U, full_out = _paddle(X, tau, eta=eta, K=K, verbose=kwargs['verbose'], nmf=nmf)

        #CX = sp.dot(X, C.T)
        if nmf and eta == 0:
            k = K
        else:
            k = compute_support(U.T)
        pars = D, C, U, tau, eta, k
        return pars
    return _paddle_lrn

def paddle_ml_lrn(K, layer0fn, eta=1.):
    def _paddle_lrn(X, tau, **kwargs):
        pars = cPickle.load(open(layer0fn))
        C, k = pars[1], pars[5]
        X = restrict_support(sp.dot(X, C.T), k)
        D, C, U, full_out = _paddle(X, tau, eta=eta, K=K, verbose=kwargs['verbose'], rtol=1.e-1)
        k = compute_support(U.T)
        pars = D, C, U, tau, eta, k, layer0fn
        return pars
    return _paddle_lrn

def paddle_u_lrn(K):
    def _paddle_u_lrn(X, tau, **kwargs):
        D, C, U, full_out = _paddle(X, tau, eta=0.1, K=K, verbose=kwargs['verbose'])
        pars = D, C, tau
        U = _ist(X, D, tau) # encoding with mu=0
        return pars
    return _paddle_u_lrn

def paddle_v_lrn(K):
    eta = 0.1
    def _paddle_v_lrn(X, tau, **kwargs):
        D, C, U, full_out = _paddle(X, tau, eta=eta, K=K, verbose=kwargs['verbose'])
        pars = D, C, tau, eta
        return pars
    return _paddle_v_lrn

def paddlel1_lrn(K):
    def _paddlel1_lrn(X, tau, **kwargs):
        D0, C0 = dual_l1.init(X.T, K)
        C0 = sp.zeros(C0.shape, C0.dtype)
        D, C, U, full_out = dual_l1.learn(X.T, D0, C0, verbose=kwargs['verbose'], tau=tau, mu=0, minused=0, rtol=1.e-5)
        pars = D, C, tau
        return pars
    return _paddlel1_lrn

def paddletf_lrn(K):
    def _paddletf_lrn(X, tau, **kwargs):
        D0, U0 = tight2.init(X.T, K)
        D, U, full_out = tight2.learn(X.T, D0, U0, verbose=kwargs['verbose'], tau=tau, mu=0, minused=0, rtol=1.e-4)
        pars = D, D.T, tau
        return pars
    return _paddletf_lrn

########## encoding methods

def pca(X, _pca):
    return _pca.transform(X)

def l1dl_enc(X, pars):
    D, tau = pars
    U = _ist(X, D, tau)
    return U

def paddle_enc(X, pars):
    D, C, U0, tau, eta, k = pars
    U = sp.dot(X, C.T)
    U = restrict_support(U, k)
    #U = sp.where(sp.absolute(U) <= t, 0, U)    
    return U

def paddle_ml_enc(X, pars):
    D1, C1, U1, tau1, eta1, k1, layer0fn = pars
    D0, C0, U0, tau0, eta0, k0 = cPickle.load(open(layer0fn))
    U = restrict_support(sp.dot(X, C0.T), k0)
    U = restrict_support(sp.dot(U, C1.T), k1)
    return U

def paddle_u_enc(X, pars):
    D, C, tau = pars
    U = _ist(X, D, tau) # encoding with mu=0
    return U

def paddle_v_enc(X, pars):
    D, C, tau, eta = pars
    U = _ist(X, D, tau, eta, C) # encoding with mu=0
    return U

########## decoding methods

def pca_rec(X, _pca):
    return _pca.mean_.reshape((1, -1)) + sp.dot(X, _pca.components_.T)

def l1dl_dec(U, pars):
    D, tau = pars
    return sp.dot(U, D.T)

def paddle_dec(U, pars):
    D = pars[0]
    return sp.dot(U, D.T)

def paddle_ml_dec(U, pars):
    D1, C1, U1, tau1, eta1, k1, layer0fn = pars
    D0, C0, U0, tau0, eta0, k0 = cPickle.load(open(layer0fn))
    X = sp.dot(U, D1.T)
    X = sp.dot(X, D0.T)
    return X

###################################

def compute_recs(X, U, method, pars):
        R = METHODS[method]['dec'](U, pars)
        err = sp.sqrt(sp.mean((R - X)**2, 1))
        assert len(err) == R.shape[0], err.shape
        return R, err.mean(), err.std()

def class_experiment(reps, n, Xtrn, Ytrn, Xval, Yval, Xtst, Ytst, penalties, verbose):

    err_trn = sp.zeros((reps,), sp.float32)
    err_val = sp.zeros((reps,), sp.float32)
    err_tst = sp.zeros((reps,), sp.float32)
    
    for r in xrange(reps):
    
        if n == Xtrn.shape[0]:
            data = Xtrn
            labels = Ytrn
        
        else:

            print ' sampling'
            data = sp.zeros((n*10, Xtrn.shape[1]), Xtrn.dtype)
            labels = sp.zeros((n*10,), sp.int32)
         
            for cls in sp.arange(10):
                i = sp.where(Ytrn == cls)[0]
                j = i[sp.random.permutation(len(i))[:n]]
                data[n*cls:n*(cls+1)] = Xtrn[j]
                labels[n*cls:n*(cls+1)] = cls

        # logistic regression
        optimal = 0
        opt_pen = None
        print ' training'
        #for penalty in [1.e4, 1.e3, 1.e2, 1.e1, 1.e0, 1.e-1, 1.e-2]:
        for penalty in penalties:
            #start = time.clock() 
            LR = LogisticRegression(penalty='l2', C=penalty)
            LR.fit(data, labels)
            score_val = LR.score(Xval, Yval)
            if verbose:
                print '   validation error %.1%% (pen )'
                print '   validation error = %.1f%% (pen = %.1e)' % (100*(1-score_val), penalty)
            if score_val > optimal:
                err_trn[r] = 1 - LR.score(data, labels)
                err_tst[r] = 1 - LR.score(Xtst, Ytst)
                err_val[r] = 1 - score_val
                optimal = score_val
                opt_pen = penalty
            #print "It took %d seconds" % ((time.clock()-start))

        print ' optimal test error = %.1f%% (pen = %.1e)' % (100*err_tst[r], opt_pen)
        if opt_pen == penalties[0] or opt_pen == penalties[-1]:
            warnings.warn('optimal penalty is at the range limits')

    return err_trn, err_val, err_tst

def methodkey(method, mpar=None):
    if mpar == None:
        mkey = method
        filelabel = method
    else:
        mkey = (method, mpar)
        filelabel = '%s_%.1e' % (method, mpar)
    return mkey, filelabel

def update_results(method, mpar, results, nsamples, outfn, force, verbose, dltrnsize=20000):

    mkey, filelabel = methodkey(method, mpar)
    featfn = os.path.join(outpath, 'features_%s.npz' % filelabel)
    if dltrnsize > 0:
        sizelbl = '%dk' % (dltrnsize/1000,)
    else:
        sizelbl = 'ALL'
    parsfn = 'parameters_%s_%s.pkl' % (filelabel, sizelbl)
    parsfn = os.path.join(outpath, parsfn)
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
        X0 = preprocess(train_set[0], center)
        if dltrnsize > 0:
            X0 = X0[:dltrnsize]
        pars = METHODS[method]['lrn'](X0, mpar, verbose=verbose)
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
            start = time.clock()
            X[lbl] = METHODS[method]['enc'](X0, pars)
            elapsed += time.clock() - start
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

    # classification
    for n in nsamples:

        if not n in results[mkey].keys():

            #penalties = [1.e8, 2.e7, 1.e7, 5.e6, 2.e6, 1.e6, 5.e5, 2.e5, 1.e5, 1.e4, 1.e3, 1.e2]
            penalties = [1., 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3, 2.e-3, 1.e-3]
            if 'pen' in METHODS[method]:
                penalties = METHODS[method]['pen'][n]
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

            #print ' experiment already performed (method %s, parameter %.1e, training set size %d)' % (method, mpar, n)

    return None

def compute_sparsities(results, outfn, force=False):
    for key in results:
        if 'sparsity' not in results[key] or force:
            if isinstance(key, str):
                method = key
                mpar = None
                print ' computing sparsity for method %s' % method,
            else:
                method, mpar = key
                print ' computing sparsity for method %s (par = %.1e)' % key,
            mkey, filelabel = methodkey(method, mpar)
            featfn = os.path.join(outpath, 'features_%s.npz' % filelabel)
            print '<- %s' % featfn
            npz = sp.load(featfn)
            Xtrn, Ytrn = npz['Xtrn'], npz['Ytrn']
            Xval, Yval = npz['Xval'], npz['Yval']
            Xtst, Ytst = npz['Xtst'], npz['Ytst']
            s = sp.concatenate((sparsity(Xtrn, axis=1),
                                sparsity(Xval, axis=1),
                                sparsity(Xtst, axis=1)))
            results[key]['sparsity'] = (s.mean(), s.std())
            print '   sparsity = %.2f (s.d. = %.2f)' % results[key]['sparsity']
            cPickle.dump(results, open(outfn, 'w'))
                            
####################################### MAIN ################################

# list of available methods
METHODS = {
    'RAW' : {'lrn': raw_trn, 'enc': raw, 'dec': raw},
    'PCA' : {'lrn': pca_trn, 'enc': pca, 'dec': pca_rec},
    'L1DL' : {'lrn': l1dl_lrn, 'enc': l1dl_enc, 'dec': l1dl_dec,
              'pen': {10: [1.e0, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3, 1.e-3],
                      100: [1.e0, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3, 1.e-3],
                      1000: [5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2]}},
    'PADDLE' : {'lrn': paddle_lrn(256, 1.), 'enc': paddle_enc, 'dec': paddle_dec,
                'pen': {10: [1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                        100: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                        1000: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_1024' : {'lrn': paddle_lrn(1024, 1.), 'enc': paddle_enc, 'dec': paddle_dec,
                     'pen': {10: [2.e2, 1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2],
                            100: [1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            1000: [2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_2048' : {'lrn': paddle_lrn(2048, 1.), 'enc': paddle_enc, 'dec': paddle_dec,
                     'pen': {10: [2.e2, 1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2],
                            100: [1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            1000: [2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_NMF' : {'lrn': paddle_lrn(1024, 1., nmf=True), 'enc': paddle_enc, 'dec': paddle_dec,
                     'pen': {10: [2.e2, 1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2],
                            100: [1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            1000: [2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_ML' : {'lrn': paddle_ml_lrn(1024, 'results_MNIST/parameters_PADDLE_1024_3.0e+00.pkl', 1.), 'enc': paddle_ml_enc, 'dec': paddle_ml_dec,
                     'pen': {10: [2.e2, 1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2],
                            100: [1.e2, 5.e1, 2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            1000: [2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_L1' : {'lrn': paddlel1_lrn(1024), 'enc': paddle_enc, 'dec': paddle_dec,
                    'pen': {10: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            100: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            1000: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_TF' : {'lrn': paddletf_lrn(1024), 'enc': paddle_enc, 'dec': paddle_dec,
                    'pen': {10: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            100: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2],
                            1000: [1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1]}
                },
    'PADDLE_U' : {'lrn': paddle_u_lrn(256), 'enc': paddle_u_enc, 'dec': paddle_dec,
                  'pen': {10: [5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3, 2.e-3, 1.e-3],
                          100: [5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3],
                          1000: [2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2]}
                  },
    'PADDLE_V' : {'lrn': paddle_v_lrn(256), 'enc': paddle_v_enc, 'dec': paddle_dec,
                  'pen': {10: [5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3, 2.e-3, 1.e-3],
                          100: [5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2, 5.e-3],
                          1000: [2.e1, 1.e1, 5.e0, 2.e0, 1.e0, 5.e-1, 2.e-1, 1.e-1, 5.e-2, 2.e-2, 1.e-2]}
                  }
    }

def parse_cl():
    # parse command line args
    op = OptionParser(usage='%prog dataset [options]')
    op.add_option("-o", "--outpath", dest="outpath",
                  default='./results_MNIST/',
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
    op.add_option("-t", "--dltrnsize", dest="dltrnsize",
                  type="int", default=20000,
                  help="size of the training set for learning the dictionary (0==all)")
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
    outpath, method, mpar, force, verbose, dltrnsize = options.outpath, options.method, options.mpar, options.force, options.verbose, options.dltrnsize
    
    # creates the output path if not present
    if not os.access(outpath, os.W_OK):
        os.mkdir(outpath)

    W = 28 # image size for the MNIST dataset
    reps = 10 # replicas
    nsamples = [10, 100, 1000] # number of training samples in each exp.

    # load previous results
    outfn = os.path.join(outpath, 'results.pkl')
    if os.access(outfn, os.R_OK):
        results = cPickle.load(open(outfn))
    else:
        results = {}

    # possibly compute missing results
    if method != None:
        # the key could be a combination of method and parameter
        if mpar != None:
            mkey = (method, mpar)
        else:
            mkey = method
        # check if the results are there, if not compute them
        update_results(method, mpar, results, nsamples, outfn, force, verbose, dltrnsize)

    # sparsity vs RMSE
    compute_sparsities(results, outfn)
    print sorted(results.keys())

    if options.show:

        #lines = zip(['L1DL', 'PADDLE', 'PADDLE_1024', 'PADDLE_2048', 'PADDLE_NMF'], ['b', 'r', 'g', 'k', 'y'])
        #lines = zip(['L1DL', 'PADDLE_1024', 'PADDLE_2048'], ['b', 'g', 'k']) # senza NMF
        lines = zip(['L1DL', 'PADDLE_1024', 'PADDLE_NMF'], ['b', 'g', 'k'])
        #lines = zip(['PADDLE_1024', 'PADDLE_NMF'], ['g', 'k'])

        pylab.figure()
        # raw
        y, yerr = results['RAW']['sparsity']
        pylab.errorbar(0, y, yerr, fmt='mo')
        # PCA
        x, xerr = results['PCA']['rec_trn']
        y, yerr = results['PCA']['sparsity']
        pylab.errorbar(x, y, yerr, fmt='ro')
        for m, c in lines:
            keys = sorted([k for k in results.keys() if k[0] == m])
            x = [results[k]['rec_trn'][0] for k in keys]
            #x = [results[k]['rec_tst'][0] for k in keys]
            y = [results[k]['sparsity'][0] for k in keys]
            yerr = [results[k]['sparsity'][1] for k in keys]
            pylab.errorbar(x, y, yerr, fmt='%co--' % c)


        pylab.title('Sparsity vs RMSE')
        pylab.ylabel('Sparsity')
        pylab.xlabel('RMSE')
        xmin, xmax = pylab.xlim()
        pylab.xlim(xmin-0.02, xmax+0.02)
        pylab.ylim(0, 1)
        pylab.grid()
        pylab.legend()
        #pylab.savefig(os.path.join(outpath, 'sparsity.png'))
        pylab.savefig(os.path.join(outpath, 'sparsity_vs_rmse.pdf'), boundingbox='tight', transparent=True)
            
        #pylab.show()


        show_trn = False

        pylab.figure(figsize=(12,5))
        for i, n in enumerate([10, 100, 1000]):
            # accuracy vs RMSE
            pylab.subplot(1, 3, i+1)
            #pylab.title('%d training samples / %d reps' % (n, reps))
            pylab.title('%d training samples' % n)
            # raw features
            #y, yerr = results['RAW'][n]['err_tst']
            #pylab.errorbar(0, 100*y, 100*yerr, fmt='m<')
            # PCA encoding
            x, xerr = results['PCA']['rec_tst']
            y, yerr = results['PCA'][n]['err_tst']
            #pylab.errorbar(x, 100*y, 100*yerr, xerr, fmt='b^')
            pylab.errorbar(x, 100*y, 100*yerr, fmt='r^')
            for m, c in lines:
                keys = sorted([k for k in results.keys() if k[0] == m])
                x = [results[k]['rec_tst'][0] for k in keys]
                xerr = [results[k]['rec_tst'][1] for k in keys]
                y = [100*results[k][n]['err_tst'][0] for k in keys]
                yerr = [100*results[k][n]['err_tst'][1] for k in keys]
                #pylab.errorbar(x, y, yerr, xerr, fmt='%c^-' % c, label=m)
                pylab.errorbar(x, y, yerr, fmt='%c^-' % c, label=m)
            if show_trn:
                y, yerr = results['RAW'][n]['err_trn']
                pylab.errorbar(0, 100*y, 100*yerr, fmt='m>')
                x, xerr = results['PCA']['rec_trn']
                y, yerr = results['PCA'][n]['err_trn']
                pylab.errorbar(x, 100*y, 100*yerr, fmt='rv')
                for m, c in lines:
                    keys = sorted([k for k in results.keys() if k[0] == m])
                    x = [results[k]['rec_trn'][0] for k in keys]
                    xerr = [results[k]['rec_trn'][1] for k in keys]
                    y = [100*results[k][n]['err_trn'][0] for k in keys]
                    yerr = [100*results[k][n]['err_trn'][1] for k in keys]
                    pylab.errorbar(x, y, yerr, fmt='%cv-' % c, label=m)
            pylab.ylabel('Error rate %')
            pylab.xlabel('RMSE')
            xmin, xmax = pylab.xlim()
            pylab.xlim(xmin-0.02, xmax+0.02)
            pylab.ylim(0, 30.)
            pylab.grid()
            #pylab.legend()
            pylab.savefig(os.path.join(outpath, 'accuracies_vs_rmse.pdf'), boundingbox='tight', transparent=True)

        pylab.figure(figsize=(12,5))
        for i, n in enumerate([10, 100, 1000]):
            # accuracy vs elapsed time
            pylab.subplot(1, 3, i+1)
            #pylab.title('%d training samples / %d reps' % (n, reps))
            pylab.title('%d training samples' % n)
            # raw features
            y, yerr = results['RAW'][n]['err_tst']
            pylab.errorbar(0, 100*y, 100*yerr, fmt='mo')
            # PCA encoding
            if 'elapsed' in results['PCA']:
                x, xerr = results['PCA']['elapsed']
                y, yerr = results['PCA'][n]['err_tst']
                pylab.errorbar(x, 100*y, 100*yerr, fmt='ro')
            for m, c in lines:
                keys = sorted([k for k in results.keys() if k[0] == m and 'elapsed' in results[k]])
                if len(keys) > 0:
                    x = [results[k]['elapsed'] for k in keys]
                    y = [100*results[k][n]['err_tst'][0] for k in keys]
                    yerr = [100*results[k][n]['err_tst'][1] for k in keys]
                    i = sp.argmin(y)
                    pylab.errorbar(x[i], y[i], yerr[i], fmt='%co-' % c, label=m)
            #x = results[('PADDLE_NMF', 0.)]['elapsed']
            #y = 100*results[('PADDLE_NMF', 0.)][n]['err_tst'][0]
            #yerr = 100*results[('PADDLE_NMF', 0.)][n]['err_tst'][1] 
            #pylab.errorbar(x, y, yerr, fmt='%co-' % c, label=m)
            pylab.ylabel('Error rate %')
            pylab.xlabel('elapsed time')
            #xmin, xmax = pylab.xlim()
            #pylab.xlim(xmin-0.02, xmax+0.02)
            pylab.semilogx()
            pylab.ylim(0, 30.)
            pylab.grid()
            #pylab.legend()
            pylab.savefig(os.path.join(outpath, 'accuracies_vs_elapsed.pdf'), boundingbox='tight', transparent=True)

        Ns = sp.array([10, 100, 1000])
        pylab.figure()
        # raw features
        #y = sp.array([results['RAW'][n]['err_tst'][0] for n in Ns])
        #yerr = sp.array([results['RAW'][n]['err_tst'][1] for n in Ns])
        #pylab.errorbar(Ns/784., 100*y, 100*yerr, fmt='m^-')
        # PCA encoding
        y = sp.array([results['PCA'][n]['err_tst'][0] for n in Ns])
        yerr = sp.array([results['PCA'][n]['err_tst'][1] for n in Ns])
        pylab.errorbar(Ns/256., 100*y, 100*yerr, fmt='r^-', label='PCA')
        # for i, n in enumerate([10, 100, 1000]):
        #     # accuracy vs elapsed time
        #     pylab.subplot(1, 3, i+1)
        #     #pylab.title('%d training samples / %d reps' % (n, reps))
        #     pylab.title('%d training samples' % n)
        dim = {'L1DL' : 256., 'PADDLE' : 256., 'PADDLE_1024': 1024., 'PADDLE_2048': 2048., 'PADDLE_NMF': 1024.}
        for m, c in lines:
            keys = sorted([k for k in results.keys() if k[0] == m])
            y, yerr = [], []
            for n in Ns:
                r = [results[k][n]['err_tst'][0] for k in keys]
                i = sp.argmin(r)
                y.append(100*r[i])
                yerr.append(100*[results[k][n]['err_tst'][1] for k in keys][i])
            pylab.errorbar(Ns/dim[m], sp.array(y), sp.array(yerr), fmt='%c^-' % c, label=m)
        pylab.ylabel('Error rate %')
        pylab.xlabel('Training set relative size')
        #xmin, xmax = pylab.xlim()
        #pylab.xlim(xmin-0.02, xmax+0.02)
        pylab.semilogx()
        pylab.ylim(0, 30.)
        pylab.grid()
        #pylab.legend(loc='lower left')
        pylab.savefig(os.path.join(outpath, 'accuracies_vs_trnsize.pdf'), boundingbox='tight', transparent=True)


        pylab.show()

    for key in sorted(results.keys()):
        print key
        for n in nsamples:
            if n in results[key]:
                err, sd = results[key][n]['err_tst']
                print ' n = %d, val. err. = %.3f (sd = %.3f)' % (n, err, sd)
