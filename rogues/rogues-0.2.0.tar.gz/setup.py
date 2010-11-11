import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name             = 'rogues',
      version          = '0.2.0',
      packages         = find_packages(),
      test_suite       = 'rogues.matrices.tests',
      install_requires = ['numpy', 'scipy', 'matplotlib'],
      author           = "Don MacMillen",
      author_email     = "don@macmillen.net",
      description      = "Python and numpy port of Nicholas Higham's m*lab test matrices",
      license          = "MIT",
      keywords         = "numpy scipy matplotlib linalg",
      classifiers=[
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: OS Independent',
                     'Topic :: Scientific/Engineering :: Mathematics',
      ],
      long_description =
"""
Rogues is a Python and numpy/scipy port of Nicholas Higham's m*lab test matrices.

These matrices are a collection of interesting matrices that appear
in m*lab's 'gallery' collection.  This collection was originally defined
and implemented by Prof. Nicholas Higham of Manchester University and is
more fully discussed in "The Test Matrix Toolbox for Matlab (Version 3.0)",
N.J. Higham, Numerical Analysis Report No. 276, September 1995 and can be
found at

http://www.maths.manchester.ac.uk/~nareports

By 'interesting' we mean that these matrices either present some challenges
to numerical algorithms or have some a set of interesting properties. The
documentation of the individual functions contains much more info, as well
as references.

Also included are a set of matrix utility functions that are needed for 
generating some of members of the collection as well as a few functions
from Prof. Higham's matrixcomp package.  One of the more interesting 
routines here is mdsmax, a direct search optimization algorithm.

The rogues package depends on numpy and scipy, both of which must be installed.
Additionally, there are a few routines that deal with plotting, and these
use matplotlib.  While ipython is not strictly necessary, it is a very
convenient environment for numpy / scipy / matplotlib. Finally, the unit 
tests utilize the nose package and the numpy wrappers around nose. To run 
the tests from inside ipython, for example, type the following

import rogues.matrices.tests at rmt
import rogues.utils.tests as rut

rmt.check()
rut.check()

The inluded matrix generation functions are:

   cauchy    Cauchy matrix
   chebspec  Chebyshev spectral differentiation matrix
   chebvand  Vandermonde-like matrix for the Chebyshev polynomials
   chow      Chow matrix - a singular Toeplitz lower Hessenberg matrix
   clement   Clement matrix - tridiagonal with zero diagonal entries
   comp      Comparison matrices
   compan    Companion matrix
   condex    Counterexamples to matrix condition number estimators
   cycol     Matrix whose columns repeat cyclically
   dingdong  Dingdong matrix - a symmetric Hankel matrix
   dorr      Dorr matrix - diagonally dominant, ill conditioned, tridiagonal.
   dramadah  A (0,1) matrix whose inverse has large integer entries
   fiedler   Fiedler matrix - symmetric
   forsythe  Forsythe matrix - a perturbed Jordan block
   frank     Frank matrix - ill conditioned eigenvalues.
   gearm     Gear matrix
   gfpp      Matrix giving maximal growth factor for GW with partial pivoting
   grcar     Grcar matrix - a Toeplitz matrix with sensitive eigenvalues.
   hadamard  Hadamard matrix
   hankel    Hankel matrix
   hanowa    A matrix whose eigenvalues lie on a vertical line in C
   hilb      Hilbert matrix
   invhess   Inverse of an upper Hessenberg matrix
   invol     An involutory matrix
   ipjfact   A Hankel matrix with factorial elements
   jordbloc  Jordan block matrix
   kahan     Kahan matrix - upper trapezoidal
   kms       Kar-Murdock-Szego Toeplitz matrix
   krylov    Krylov matrix
   lauchli   Lauchli matrix - rectangular
   lehmer    Lehmer matrix - symmetric positive definite
   lesp      A tridiagonal matrix with real, sensitve eigenvalues
   lotkin    Lotkin matrix
   minij     Symmetric positive definite matrix min(i,j)
   moler     Moler matrix symmetric positive definite
   neumann   Singular matrix from the descrete Neumann problem (sparse)
   ohess     Random, orthogonal upper Hessenberg matrix
   parter    Parter matrix - a Toeplitz matrix with singular values near pi
   pascal    Pascal matrix
   pdtoep    Symmetric positive definite Toeplitz matrix
   pei       Pei matrix
   pentoep   Tentadiagonal Toeplitz matrix (sparse)
   poisson   Block tridiagonal matrix from Poisson's equation (sparse)
   prolate   Prolate matrix - symmetric, ill-conditioned Toeplitz matrix
   qmult     Pre-multiply by random orthogonal matrix
   rando     Random matrix with elements -1, 0, or 1
   randsvd   Random matrix with pre-assigned singular values
   redheff   A (0,1) matrix of Redheffer associated with the Riemann hypothesis
   riemann   A matrix associated with the Riemann hypothesis
   smoke     Smoke matrix - complex, with a 'smoke ring' pseudospectrum
   triw      Upper triangular matrix discussed by Wilkinson and others
   wathen    Wathen matrix - a finite element matrix (sparse, random entries)
   wilk      Various specific matrices devised /discussed by Wilkenson
   wilkinson Wilkinson matrix of size n, where n must be odd

Some of generally useful matrix utility functions:

   augment   Agumented system matrix
   bandred   Band reduction by two-sided unitary transformations
   cgs       Classical Gram-Schmidt QR factorization
   cond      Matrix condition number in 1,2,Frobenius, or infinity norm
   condeig   Condition numbers for eigenvalues of a matrix
   cpltaxes  Determine suitable axis for plot of complex vector
   dual      Dual vector with respect to Holder p-norm
   ge        Gaussian elimination without pivoting
   hankel    Given first row, returns a Toeplitz type matrix
   house     Householder matrix
   mdsmax    Multidimensional search method for direct search optimization
   mgs       Modified Gram-Schmidt QR factorization
   pow2      Vector whose i-th element is 2 ** x[i], where x[] is input
   ps        Dot plot of a pseudospectrum
   repmat    Simple re-implementation of m*lab's repmat function
   rq        Rayleigh quotient 
   skewpart  Skew-symmetric (skew-Hermitian) part
   sparsify  Randomly sets matrix elements to zero
   sub       Principal submatrix
   symmpart  Symmetric (Hermitian) part
   toeplitz  Returns toeplitz matrix given first row of the matrix
   treshape  Reshape vector to or from (unit) triangular matrix
   tridiag   Sparse tridiagonl matrix given the diagonals
   vand      Vandermonde matrix
   vecperm   Vector permutation matrix

   More information is available on any of these functions by typing
   "help <funcname>"

Release 0.2.0 Notes
The unit tests are now included in the distribution.  They work with nosetests
and if you have installed the source (not the zip'd egg file) you can do the
following

import rogues.matrices.tests as rmt
rmt.check()
import rogues.utils.tests as rut
rut.check()
rut.check_see()    # matrix visualization
rut.check_ps()     # matrix visualization

Sadly, this does not work with zipped egg files.

Fixed several small bugs in the use of np.max.  Added matrix visualization
routing 'see'
"""
)
