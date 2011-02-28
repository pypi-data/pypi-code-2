
import sys
import scipy as sp
import scipy.linalg as la
import paddle, dual_l1

if __name__=='__main__':

    # parse the arguments
    if len(sys.argv) < 2:
        print 'usage: python %s imagefile [Nmax]' % sys.argv[0]
        sys.exit(0)

    # possibly set the maximum number of patches to extract
    if len(sys.argv) > 2:
        Nmax = int(sys.argv[2])
    else:
        Nmax = 0

    # load the image
    img = sp.misc.imread(sys.argv[1])

    # possibly convert to grayscale
    if img.ndim == 3:
        assert img.shape[2] <= 3, img.shape
        img = sp.mean(img, 2)

    # recenter
    #img -= img.flatten().mean()
    # normalize
    #img /= 125.

    # extract the patches
    h, w = 4, 4
    X = paddle.common.img2patches(img, size=(h, w), Nmax=Nmax)
    assert X.shape[0] == (h*w), X.shape
    X -= sp.mean(X, 0).reshape((1, -1))

    # save an image with a subset of the patches
    #paddle.common._saveDict(X, None, Nrows=10, Ncols=25, path='patches.png', sorted=False)

    # call paddle
    K = 2*h*w 
    #D0, C0 = paddle.dual_l1.init(X, K)
    #D, C, U, full_out = paddle.dual_l1.learn(X, D0, C0, tau=5., rtol=1.e-8)
    D0, C0 = dual_l1.init(X, K)
    #C0[:] = 0
    #C0 = D0.T
    D0 = sp.random.normal(size=(D0.shape))
    C0 = sp.random.normal(size=(C0.shape))
    if False:
        U = sp.sqrt(sp.sum((X[:,sp.newaxis,:] - D0[:,:,sp.newaxis])**2, 0))
        idx = sp.argmin(U, 0)
        U[:] = 0
        U[idx, sp.arange(X.shape[1])] = 1
        C0 = sp.dot(U, la.pinv(X))
    D, C, U, full_out = dual_l1.learn(X, D0, C0, tau=5.e0, rtol=1.e-5, verbose=False, minused=0)

    sp.savez('results.npz', X=X, D=D, C=C, U=U)

    # save the results
    Nrows = int(sp.sqrt(K/2))
    Ncols = K/Nrows
    paddle.common._saveDict(D, U, Nrows=Nrows, Ncols=Ncols, path='atoms.png', sorted=True)
    paddle.common._saveDict(C.T, U, Nrows=Nrows, Ncols=Ncols, path='filters.png', sorted=True)
