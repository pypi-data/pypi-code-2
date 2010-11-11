import numpy as np
import numpy.linalg as nl
import scipy.sparse as scp
import pylab as plt
from mpl_toolkits.mplot3d import axes3d
import rogues as rg

def see(a, k = 0):
    """
    see    Pictures of a matrix and its (pseudo-) inverse.
    see(a) displays mesh(a), mesh(pinv(a)), semilogy(svd(a),'o'),
    and (if a is square) fv(a) in four subplot windows.
    see(a, 1) plots an approximation to the pseudospectrum in the
    third window instead of the singular values.
    see(a, -1) plots only the eigenvalues in the fourth window,
    which is much quicker than plotting the field of values.
    If 'a' is complex, only real parts are used for the mesh plots.
    If 'a' is sparse, just spy(a) is shown.

    NOTE: This routine is still not quite right in calling ps and
          fv has still not been ported.  Also, need to change the
          arg 'k' to something more Pythonic.
    """

    (m, n) = a.shape
    square = m == n

    if scp.issparse(a):
        plt.spy(a)

    else:
        fig = plt.figure()
        b = nl.pinv(a)
        u, s, v = nl.svd(a)
        any_s_zeros = not s.all()
        # Remove zero singular values for semilogy plot.
        s = s.compress(s)
        # Create the x any y arrays to match the matrix indices
        x, y = plt.mgrid[0:a.shape[0], 0:a.shape[1]]

        ax221 = fig.add_subplot(221, projection = '3d')
        ax221.plot_wireframe(x, y, a.real)
        ax222 = fig.add_subplot(222, projection = '3d')
        ax222.plot_wireframe(x, y, b.real)

        ax223 = fig.add_subplot(223)
        ax224 = fig.add_subplot(224)

        if k <= 0:
            ax223.semilogy(s, 'og')
            ax223.hold(True)
            ax223.semilogy(s, '-')
            ax223.hold(False)
            if any_s_zeros:
                ax223.title('Zero(s) omitted')

        elif k == 1:
            rg.ps(a, ax = ax223)

        if square:
            if k == -1:
                rg.ps(a, ax = ax224)
            else:
                pass
                #  fv not yet ported

        else:
            if k == 0:
                ax224.axis('off')
            else:
                plt.clf()

            plt.text(0,0,'Matrix not square.')

    plt.show()
