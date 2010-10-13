
import scipy, sys
import numpy as NP
import paddle

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
    img = scipy.misc.imread(sys.argv[1])

    # ensures it is a color image
    assert img.ndim == 3, img.shape
    assert img.shape[2] == 3, img.shape

    # recenter
    #oldshape = img.shape
    #img.shape = (-1, 3)
    #img -= NP.mean(img, 0).reshape((1, 3))
    # normalize
    #img /= NP.std(img, 0).reshape((1, 3))
    #img.shape = oldshape
    
    # extract the patches
    h, w = 10, 10
    X = paddle.common.img2patches(img, size=(h, w), Nmax=Nmax)
    assert X.shape[0] == (img.shape[2]*h*w), X.shape
    #X -= NP.mean(X, 0).reshape((1, -1))

    # save an image with a subset of the patches
    X = X.astype(NP.float)
    X /= 255.
    paddle.common._saveDict(X, None, Nrows=10, Ncols=25, path='patches.png', sorted=False, channels=3)

    # call paddle
    K = img.shape[2]*h*w + 1
    D0, C0, U0 = paddle.dual.init(X, K)
    D, C, U, full_out = paddle.dual.learn(X, D0, C0, U0, tau=5., rtol=1.e-8)
    #paddle.common.print_frame_assessment(D)

    # save the results
    paddle.common._saveDict(D, U, Nrows=10, Ncols=20, path='atoms.png', sorted=True, channels=3)
    paddle.common._saveDict(C.T, U, Nrows=10, Ncols=20, path='filters.png', sorted=True, channels=3)
