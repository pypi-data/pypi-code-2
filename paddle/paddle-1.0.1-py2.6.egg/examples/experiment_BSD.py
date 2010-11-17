'''
This is the script to run the experiment on the BSd dataset, reported in
section 4.2 of the techical report:

C.Basso, M.Santoro, A.Verri and S.Villa. "PADDLE: Proximal Algorithm for
Dual Dictionaries LEarning", DISI-TR-2010-XX, 2010.
'''

import sys, os, glob, pylab
import scipy.linalg as la
import scipy.stats
import scipy as sp
from paddle import dual, common

def checkBSD(path):
    '''
    Cheks that the is the root directory of the standard distribution
    of the Berkeley segmentation dataset, as downloaded from
    http://www.eecs.berkeley.edu/Research/Projects/CS/vision/bsds/BSDS300-images.tgz
    It returns the absolute paths of the test and training directories.
    '''
    print 'Looking for Berkeley segmentation dataset in', path
    print ' ...',
    if not os.access(path, os.X_OK):
        print 'the path is not accessible. Exiting.'
        sys.exit(0)
    # sets the path holding all images
    imagesdir = os.path.join(path, 'images')
    if not os.access(imagesdir, os.X_OK):
        print 'the images directory (%s) is not accessible. Exiting.' % imagesdir
        sys.exit(0)
    # sets the path holding test images
    testdir = os.path.join(imagesdir, 'test')
    if not os.access(testdir, os.X_OK):
        print 'the test directory (%s) is not accessible. Exiting.' % testdir
        sys.exit(0)
    # sets the path holding training images
    traindir = os.path.join(imagesdir, 'train')
    if not os.access(traindir, os.X_OK):
        print 'the train directory (%s) is not accessible. Exiting.' % traindir
        sys.exit(0)
    print 'OK!'
    return testdir, traindir

def draw_sample(path, W, N):
    '''
    Draws randomly N patches with size WxW from the images in path.
    It returns an ndarray with shape (W*W, N).
    '''
    # list of training images
    trainlist = glob.glob(os.path.join(path, '*.jpg'))
    # number of training images (should be 200)
    Nfiles = len(trainlist)
    if Nfiles != 200:
        print 'WARNING: number of images in train dir is %d (!= 200)' % Nfiles
    # number of patches to sample from each image
    n = N/Nfiles
    if n*Nfiles < N:
        n += 1
    print 'Sampling %d patches each from %d images, for a total of %d patches' % (n, Nfiles, n*Nfiles)
    bytesize = (n*Nfiles*W*W*sp.dtype('f').itemsize)
    print 'Total size about %d MB' % (bytesize/(1024**2))
    # creates the sampling stencil
    stencil = sp.indices((W,W))
    stencil.shape = (2,1,-1)
    # loops over the images
    patches = []
    for fn in trainlist:
        #print ' ...', os.path.basename(fn)
        # load the images
        img = sp.misc.imread(fn)
        assert img.ndim == 3, img.ndim
        assert img.shape[2] == 3, img.shape
        # convert to gray scale
        img = sp.mean(img, 2)
        # recenter
        img -= img.flatten().mean()
        # normalize
        img /= 125.
        # pick random positions for upper left corner
        y = sp.random.randint(0, img.shape[0]-W, size=(1, n))
        x = sp.random.randint(0, img.shape[1]-W, size=(1, n))
        yx = sp.concatenate((y,x), 0)
        assert yx.shape == (2,n), yx.shape
        yx.shape = (2,n,1)
        # create an array with the positions of all pixels in the pacthes
        s = stencil + yx
        assert s.shape == (2,n,W*W), s.shape
        # sample from the image
        p = img[s[0], s[1]]
        assert p.shape == (n,W*W), p.shape
        # append to the list
        patches.append(p)
    # build matrix
    patches = sp.concatenate(patches, 0).T
    return patches

def draw_patches(traindir, W, N):
    # check if a previously drawn sample is already there
    patchesfn = 'BSD_patches_%dx%d_%dk.npz' % (W, W, N/1e3)
    if os.access(patchesfn, os.R_OK):
        print 'Loading a previously drawn sample from', patchesfn
        print 'REMOVE the file IF you want a NEW SAMPLE'
        npz = sp.load(patchesfn)
        Xtrn = npz['Xtrn']
        Xtst = npz['Xtst']
    else:
        # if not there, draw a new sample
        Xtrn = draw_sample(traindir, W, N)
        Xtst = draw_sample(traindir, W, N)
        sp.savez(patchesfn, Xtrn=Xtrn, Xtst=Xtst)
    return Xtrn, Xtst

if __name__=='__main__':

    W = 12   # patch width
    N = 1e4  # number of patches to sample
    tau = 1. # sparsity coefficient
    eta = 1. # coding/decoding weight
    K = 200  # size of dictionary
    R = 1    # number of repetitions
    pca = True

    # set the input arguments
    if len(sys.argv) < 2:
        print 'usage: python %s BSD_root_path [tau eta K]' % sys.argv[0]
        sys.exit(0)

    if len(sys.argv) > 2:
        if len(sys.argv) != 5:
            print 'usage: python %s BSD_root_path [tau eta K]' % sys.argv[0]
            sys.exit(0)
        tau = float(sys.argv[2])
        eta = float(sys.argv[3])
        K = int(sys.argv[4])

    # checks the directory holding the Berkeley segmentation dataset
    path = sys.argv[1]
    testdir, traindir = checkBSD(path)

    # randomly draw the patches for training images, or load them from file
    Xtrn, Xtst = draw_patches(traindir, W, N)

    # recenter the patches
    Xtrn -= sp.mean(Xtrn, 0).reshape((1, -1))
    Xtst -= sp.mean(Xtst, 0).reshape((1, -1))

    # start dictionary learning
    pars = {
        'tau' : tau, # sparsity coefficient
        'mu'  : 0, # l2 regularization
        'eta' : eta, # coding/decoding weight
        'maxiter' : 200,
        'minused' : 1,
        'verbose': False,
        'rtol': 1.e-5,
        }
    # file where the results are stored
    dicfn = 'BSD_dict_%dx%d_%dk_tau%.1e_eta%d_K%d.npz' % (W, W, N/1e3, pars['tau'], pars['eta'], K)
    if not os.access(dicfn, os.R_OK):
        # initialize the variables
        D0, C0, U0 = dual.init(Xtrn, K, det=False)
        # learn the dictionary
        D, C, U, full_out = dual.learn(Xtrn, D0, C0, U0, **pars)
        print
        print ' whole computation took %.1f secs' % full_out['time'][-1]
        timing = sp.sum(sp.array(full_out['time'][:-1]), 0)
        print ' ... time spent optimizing U = %6.1f secs (%.1f%%)' % (timing[0], 100*timing[0]/full_out['time'][-1])
        print ' ... time spent optimizing D = %6.1f secs (%.1f%%)' % (timing[1], 100*timing[1]/full_out['time'][-1])
        print ' ... time spent optimizing C = %6.1f secs (%.1f%%)' % (timing[2], 100*timing[2]/full_out['time'][-1])
        # save the results
        sp.savez(dicfn, D=D, C=C, U=U)

    # compute PCA for comparison
    if pca:
        pcafn = 'BSD_pca_%dx%d_%dk.npz' % (W, W, N/1e3)
        if not os.access(pcafn, os.R_OK):
            Cov = sp.dot(Xtrn, Xtrn.T)/(Xtrn.shape[1]-1)
            ew, ev = la.eigh(Cov)
            order = sp.argsort(ew)[::-1]
            ew = ew[order]
            ev = ev[:,order]
            assert sp.allclose(sp.sum(ev**2, 0), 1)
            Erec_pca, Erec_pca_tst = [], []
            for i in xrange(1, ev.shape[1]-1):
                Xr = sp.dot(ev[:,:i], sp.dot(ev[:,:i].T, Xtrn))
                erec = la.norm(Xtrn - Xr)/la.norm(Xtrn)
                Erec_pca.append(erec)
                Xr = sp.dot(ev[:,:i], sp.dot(ev[:,:i].T, Xtst))
                erec = la.norm(Xtst - Xr)/la.norm(Xtst)
                Erec_pca_tst.append(erec)
            Erec_pca, Erec_pca_tst = sp.array(Erec_pca), sp.array(Erec_pca_tst)
            sp.savez(pcafn, Erec_pca=Erec_pca, Erec_pca_tst=Erec_pca_tst)
        else:
            npz = sp.load(pcafn)
            Erec_pca = npz['Erec_pca']
            Erec_pca_tst = npz['Erec_pca_tst']

    # draw the atoms
    dicfn = 'BSD_dict_%dx%d_%dk_tau%.1e_eta%d_K%d.npz' % (W, W, N/1e3, tau, eta, K)
    assert os.access(dicfn, os.R_OK), 'output dictionary file %s not found' % dicfn
    npz = sp.load(dicfn)
    figfn = 'BSD_atoms_%dx%d_%dk_tau%.0e_eta%d_K%d' % (W, W, N/1e3, tau, eta, K)
    Nrows, Ncols = 20, 10
    assert Nrows*Ncols <= K, 'reduce the number of rows or columns'
    U, D, C = npz['U'], npz['D'], npz['C']
    common._saveDict(D, U, Nrows, Ncols, path = figfn + '_D.png', sorted = True)
    common._saveDict(C.T, U, Nrows, Ncols, path = figfn + '_C.png', sorted = True)
        
