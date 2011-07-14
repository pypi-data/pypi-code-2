'''
Experiment to compare the stability of different dictionaty learning algos.

The experiment is run by generating synthetic data as sparse linear
combinations of random atoms, and learning a dictionary from data
plus some noise.
We look at how the solution changes varying the noise level.
'''

import scipy as sp
import scipy.linalg as la
from dual import init, learn
from common import gendata
import pylab as pl

ra = sp.random

if __name__=='__main__':

    N = 2000  # number of data
    K = 50    # dimension of the dictionary
    k = 3     # number of relevant atoms for each datum
    d = 20    # dimension of the data
    reps = 20 # number of experiments repetitions
    # noise levels 
    noisestds = [0.01, 0.02, 0.03, 0.05, 0.07, 0.1]
    # common parameters used by learn
    mu = 1.e-8
    maxiter = 100

    def rnd(size):
        return ra.uniform(-1, 1, size=size)

    ############ synthetic experiment

    E1 = sp.zeros((len(noisestds), 0), sp.float32)
    E2 = sp.zeros((len(noisestds), 0), sp.float32)
    E1p = sp.zeros((len(noisestds), 0), sp.float32)
    E2p = sp.zeros((len(noisestds), 0), sp.float32)
    I = sp.zeros((len(noisestds), 0), sp.float32)
    Ip = sp.zeros((len(noisestds), 0), sp.float32)

    for i in xrange(reps):

        # generates random data
        X0, D_true, U_true = gendata(d, N, k, K, rnd=ra.uniform)

        # checks generated data
        assert sp.all(sp.sum(sp.where(sp.absolute(U_true) > 0, 1, 0), 0) == k)
        assert X0.shape == (d, N)

        # initialize variables
        D_, C_, U_ = init(X0, K)

        ### learn dictionaries without noise

        # learn dictionary without C
        tau = .1
        D0, C0, U0, full_out = learn(X0, D_, C_, U_, tau=tau, mu=mu, eta=0., maxiter=maxiter)

        Un1 = sp.sum(sp.absolute(U0), 1)
        Dn2 = sp.sqrt(sp.sum(D0**2, 0))

        # learn dictionary with C
        taup = .5
        D0p, C0p, U0p, full_outp = learn(X0, D_, C_, U_, tau=taup, mu=mu, eta=1., maxiter=maxiter)

        Upn1 = sp.sum(sp.absolute(U0p), 1)
        Dpn2 = sp.sqrt(sp.sum(D0p**2, 0))

        snr = []
        e1, e2, e1p, e2p, it, itp = [], [], [], [], [], []

        ### learn dictionaries with noise

        for noisestd in noisestds:

            # add some Gaussian noise
            noise = ra.normal(0, noisestd, size=(d, N))
            snr_ = 20*sp.log10(la.norm(X0) / la.norm(noise))
            print 'SNR (dB) = %d' % snr_
            snr.append(snr_)
            X = X0 + noise

            Dnoise, Cnoise, Unoise, full_out = learn(X, D_, C_, U_, tau=tau, mu=mu, eta=0., maxiter=maxiter)

            Dnoisep, Cnoisep, Unoisep, full_outp = learn(X, D_, C_, U_, tau=taup, mu=mu, eta=1., maxiter=maxiter)

            e1.append(sp.sum(sp.absolute(U0-Unoise), 1) / Un1)
            e2.append(sp.sqrt(sp.sum((D0-Dnoise)**2, 0)) / Dn2)
            e1p.append(sp.sum(sp.absolute(U0p-Unoisep), 1) / Upn1)
            e2p.append(sp.sqrt(sp.sum((D0p-Dnoisep)**2, 0)) / Dpn2)
            it.append(full_out['iters'])
            itp.append(full_outp['iters'])

        E1 = sp.concatenate((E1, sp.array(e1)), 1)
        E2 = sp.concatenate((E2, sp.array(e2)), 1)
        E1p = sp.concatenate((E1p, sp.array(e1p)), 1)
        E2p = sp.concatenate((E2p, sp.array(e2p)), 1)
        I = sp.concatenate((I, sp.array(it).reshape((-1, 1))), 1)
        Ip = sp.concatenate((Ip, sp.array(itp).reshape((-1, 1))), 1)

    pl.figure()
    pl.errorbar(snr, sp.mean(E1, 1), sp.std(E1, 1), c='b')
    pl.errorbar(snr, sp.mean(E1p, 1), sp.std(E1p, 1), c='g')
    y0, y1 = pl.ylim()
    pl.ylim(0, y1)
    pl.ylabel('L1 error on U')
    pl.xlabel('SNR (db)')
    pl.grid()
    pl.savefig('stability_U.pdf', boundingbox='tight', transparent=True)
    
    pl.figure()
    pl.errorbar(snr, sp.mean(E2, 1), sp.std(E2, 1), c='b')
    pl.errorbar(snr, sp.mean(E2p, 1), sp.std(E2p, 1), c='g')
    y0, y1 = pl.ylim()
    pl.ylim(0, y1)
    pl.ylabel('L2 error on D')
    pl.xlabel('SNR (db)')
    pl.grid() 
    pl.savefig('stability_D.pdf', boundingbox='tight', transparent=True)
   
    pl.figure()
    pl.errorbar(snr, sp.mean(I, 1), sp.std(I, 1), c='b')
    pl.errorbar(snr, sp.mean(Ip, 1), sp.std(Ip, 1), c='g')
    y0, y1 = pl.ylim()
    pl.ylim(0, y1)
    pl.ylabel('No. iterations')
    pl.xlabel('SNR (db)')
    pl.grid()
    pl.savefig('stability_iters.pdf', boundingbox='tight', transparent=True)

    pl.show()



