'''
This experiment is meant to verify that the l_1 formulation of PADDLE,
with implicit decompositions, does indeed follow the asymptotic behaviour
of PADDLE for \eta going to infinity.
'''

import os, cPickle
import scipy as sp
import scipy.linalg as la
import dual, dual_l1
ra = sp.random

if __name__ == '__main__':

    N = 1000 # number of data
    K = 20  # dimension of the dictionary
    k = 5   # number of relevant atoms for each datum
    d = 10  # dimension of the data
    noiselevel = 0

    datafn = __file__.replace('.py', '_input.npz')
    if os.access(datafn, os.R_OK):
        npz = sp.load(datafn)
        D_true, U_true, X_true = npz['D_true'], npz['U_true'], npz['X_true']
        X = npz['X']
        noiselevel = npz['noiselevel']
    else:
        # generating dictionary, all atoms have unitary norm 
        D_true = ra.uniform(-1, 1, size=(d, K)).astype(sp.float32)
        D_true /= sp.sqrt(sp.sum(D_true**2, 0)).reshape((1, -1))

        # generating coefficients
        U_true = sp.zeros((K, N), sp.float32)
        for i in xrange(N):
            U_true[ra.permutation(K)[:k],i] = ra.uniform(-1, 1, size=(k,))
        assert sp.all(sp.sum(sp.where(sp.absolute(U_true) > 0, 1, 0), 0) == k)

        # generate data
        X_true = sp.dot(D_true, U_true)
        assert X_true.shape == (d, N)

        # add some Gaussian noise
        if noiselevel > 0:
            noise = ra.normal(0, noiselevel, size=(d, N))
            X = X_true + noise
        else:
            X = X_true

        sp.savez(datafn, D_true=D_true, U_true=U_true, X_true=X_true, X=X, noiselevel=noiselevel)

    if noiselevel > 0:
        noise = X - X_true
        SNR = la.norm(X) / la.norm(noise)
        print 'SNR (dB) = %d' % (20*sp.log10(SNR),)
    else:
        print 'NO noise'

    outfn = __file__.replace('.py', '_output.pck')
    if os.access(outfn, os.R_OK):
        results = cPickle.load(open(outfn))
    else:
        results = dict()

    if not 'l1' in results:
        D0, C0 = dual_l1.init(X, K)
        D1, C1, U1, full_out = dual_l1.learn(X, D0, C0, tau=1.e-1, rtol=1.e-5, maxiter=80, minused=0)
        results['l1'] = (D0, C0, D1, C1, U1, full_out)
    else:
        D0, C0 = results['l1'][:2]

    etas = [1.e0, 1.e2, 1e4]
    for eta in etas:
        del results[eta]
        if not eta in results:
            #D0, C0, U0 = dual.init(X, K)
            U0 = sp.zeros((K, N))
            D2, C2, U2, full_out = dual.learn(X, D0, C0, U0, tau=1.e-1, mu=0, eta=eta, rtol=1.e-5, maxiter=80, minused=0, Cbound=100.)
            results[eta] = (D2, C2, U2, full_out)

    cPickle.dump(results, open(outfn, 'w'))

    D1, C1, U1 = results['l1'][2:5]
    for eta in etas:
        print eta
        D2, C2, U2 = results[eta][:3]
        print la.norm(D1-D2)/la.norm(D1), la.norm(C1-C2)/la.norm(C1), la.norm(U1-U2)/la.norm(U1)
