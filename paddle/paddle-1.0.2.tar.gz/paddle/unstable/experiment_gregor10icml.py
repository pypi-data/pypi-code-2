'''
Replicating the experiments of Gregor and LeCun, ICML, 2010
'''

import sys, os
from data import checkBSD, draw_patches
import scipy as sp
import scipy.linalg as la
import dual

def pre(X, minstd = 1.e-2):
    # recenter the patches
    X -= sp.mean(X, 0).reshape((1, -1))
    # computes the patches std
    s = sp.std(X, 0).reshape((1, -1))
    # remove low-variance patches
    keep = s.flatten() > minstd
    X = X[:, keep]
    s = s[:, keep]
    # normalize
    X /= s
    return X

if __name__=='__main__':

    W = 10   # patch width
    N = 1e4  # number of patches to sample
    K = 400  # size of dictionary
    d = W*W

    # set the input arguments
    if len(sys.argv) < 2:
        print 'usage: python %s BSD_root_path' % sys.argv[0]
        sys.exit(0)

    # checks the directory holding the Berkeley segmentation dataset
    path = sys.argv[1]
    testdir, traindir = checkBSD(path)

    # randomly draw the patches for training images, or load them from file
    Xtrn, Xtst = draw_patches(traindir, W, N)

    # preprocess
    Xtrn, Xtst = pre(Xtrn), pre(Xtst)

    # learn the dictionary only
    alpha = 0.5 # the coefficient used in the original paper
    tau = (float(K)/d)*alpha
    print 'Setting tau = %.1f' % tau

    outfn1 = __file__.replace('.py', '_out1.npz')
    if not os.access(outfn1, os.R_OK):
        D0, C0, U0 = dual.init(Xtrn, K)
        D, C, U, full_out = dual.learn(Xtrn, D0, C0, U0, tau=tau, eta=0, mu=0, minused=1, verbose=True, rtol=1.e-5)
        sp.savez(outfn1, D=D, U=U)
    else:
        print 'Loading D from', outfn1
        npz = sp.load(outfn1)
        D, U = npz['D'], npz['U']
        

    # verify some of the results from the original paper
    outfn2 = __file__.replace('.py', '_out2.npz')
    if True:#not os.access(outfn2, os.R_OK):
        U0 = sp.zeros(U.shape)#sp.dot(la.pinv(D), Xtrn)
        C = sp.zeros(D.T.shape)
        pars = {'eta': 0., 'mu': 0., 'tau': tau, 'rtol': 1.e-6, 
                'verbose': False}
        U_f1, full_out = dual._ist(Xtrn, U0, D, C, pars, maxiter=1)
        U_f3, full_out = dual._ist(Xtrn, U0, D, C, pars, maxiter=3)
        U_f7, full_out = dual._ist(Xtrn, U0, D, C, pars, maxiter=7)
        print sp.sum((U_f1 - U)**2, 0).mean()
        print sp.sum((U_f3 - U)**2, 0).mean()
        print sp.sum((U_f7 - U)**2, 0).mean()
        sp.savez(outfn2, U_f1=U_f1, U_f3=U_f3, U_f7=U_f7)
        
    
    
