
import dual, dual_l1, os, cPickle, pylab
import scipy as sp
import scipy.linalg as la
ra = sp.random 

def sanitychecks():
    d = 2
    N = 10
    K = 4

    j = sp.random.randint(0, d, size=(N,))
    alphas = sp.random.rand(N)
    X = sp.zeros((d, N), sp.float32)
    X[j, sp.arange(N)] = alphas

    D0 = sp.random.normal(size=(d, K))
    D0 /= sp.sqrt(sp.sum(D0**2, 0)).reshape((1, -1))
    C0 = sp.random.normal(size=(K, d))
    D, C, U, full_out = dual_l1.learn(X, D0, C0, tau=2, rtol=1.e-8, maxiter=80, minused=0, verbose=True)
    print D.T
    print C
    print U

def generate_data(N, K, k, d):

    # generating dictionary, all atoms have unitary norm 
    D_true = ra.uniform(-1, 1, size=(d, K)).astype(sp.float32)
    D_true /= sp.sqrt(sp.sum(D_true**2, 0)).reshape((1, -1))

    # generating coefficients
    U_true = sp.zeros((K, N), sp.float32)
    for i in xrange(N):
        U_true[ra.permutation(K)[:k],i] = ra.uniform(-1, 1, size=(k,))
    assert sp.all(sp.sum(sp.where(sp.absolute(U_true) > 0, 1, 0), 0) == k)

    # generate data
    X = sp.dot(D_true, U_true)
    assert X.shape == (d, N)
    #assert sp.all(sp.absolute(sp.mean(X, 0)) < 1.e-6), sp.mean(X, 0)
    #assert sp.allclose(sp.mean(X, 0), 0, atol=1.e-7), sp.mean(X, 0)

    return X, D_true, U_true

if __name__=='__main__':

    sanitychecks()
    1/0
    
    N = 1000 # number of data
    K = 50  # dimension of the dictionary
    k = 5   # number of relevant atoms for each datum
    d = 10  # dimension of the data
    noiselevel = 0.1

    ######## input data
    inputfn = os.path.join(os.path.dirname(__file__),
                           'test_paddle_l1_INPUT.npz')
    if os.access(inputfn, os.R_OK):
        print 'loading from', inputfn
        npz = sp.load(inputfn)
        X, D_true, U_true = npz['X'], npz['D'], npz['U']
    else:
        X, D_true, U_true = generate_data(N, K, k, d)
        sp.savez(inputfn, X=X, D=D_true, U=U_true)

        
    ######### experiments results (so far)
    outputfn = os.path.join(os.path.dirname(__file__),
                           'test_paddle_l1_OUTPUT.pck')
    if os.access(outputfn, os.R_OK):
        print 'loading current results from', outputfn
        results = cPickle.load(open(outputfn))
    else:
        results = dict()
        
    # add some Gaussian noise
    if noiselevel > 0:
        noise = ra.normal(0, noiselevel, size=(d, N))
        SNR = la.norm(X) / la.norm(noise)
        print 'SNR (dB) = %d' % (20*sp.log10(SNR),)
        X += noise
    else:
        print 'NO noise'

    r_noise = results.setdefault(noiselevel, dict())

    algo = 'paddle'
    r_algo = r_noise.setdefault(algo, dict())

    for tau in [1.e0, 5.e-1, 2.e-1, 1.e-1, 1.e-2, 1.e-4, 1.e-6]:
        if tau not in r_algo:
            if algo == 'paddle-l1':
                D0, C0 = dual_l1.init(X, K)
                D, C, U, full_out = dual_l1.learn(X, D0, C0, tau=tau, rtol=1.e-5, maxiter=80, minused=0)
            elif algo == 'paddle':
                D0, C0, U0 = dual.init(X, K)
                D, C, U, full_out = dual.learn(X, D0, C0, U0, tau=tau, rtol=1.e-5, maxiter=80, minused=1)

            U = sp.dot(C, X)
            rec = la.norm(X - sp.dot(D, U)) / la.norm(X)
            l1 = sp.absolute(U).mean()

            r_algo[tau] = (rec, l1)

    print results
    print results.keys()

    cPickle.dump(results, open(outputfn, 'w'))

    pylab.figure()
    for noiselev, r_noise in results.items():
        if algo in r_noise:
            r_algo = r_noise[algo]
            taus = sorted(r_algo.keys())
            x = [r_algo[t][1] for t in taus]
            y = [r_algo[t][0] for t in taus]
            pylab.plot(x, y, label='%.1e' % noiselev)
            #pylab.plot(x, y, 'o')
    pylab.ylabel('Relative rec. err.')
    pylab.xlabel('Avg $\ell_1$-norm of codes')
    pylab.legend()
    pylab.grid()

    pylab.figure()
    r_noise = results[noiselevel]
    print r_noise.keys()
    for algo, r_algo in r_noise.items():
        taus = sorted(r_algo.keys())
        x = [r_algo[t][1] for t in taus]
        y = [r_algo[t][0] for t in taus]
        pylab.plot(x, y, label=algo)
        pylab.plot(x, y, 'o')
    pylab.ylabel('Relative rec. err.')
    pylab.xlabel('Avg $\ell_1$-norm of codes')
    pylab.legend()
    pylab.grid()
        
    pylab.show()
