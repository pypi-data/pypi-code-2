"""
The "rogues" module is a reimplmentation of Nick Higham's test matrices into
Python, Numpy, and Scipy.  They were generally ported by using the
iPython shell.  They were developed from Version 3 (1995) of the test
matrix package from code downloaded from Higham's web site.  Also,
the earlier TOMS 694 version was used as reference in some cases.
That code was download from netlib.  Both of these packages were
accessed in February of 2009.

Also included are a small number of routines from Nick Higham's matrixcomp
library as well as several required functions that had no implementations.

Some of the issues in porting to numpy from m*lab
    * numpy arrays have zero based array indexing while m*lab has one's
      based array indexing
    * numpy / python has indexing that does not include the upper end of
      the specified range, e.g. a[0:n]  is  a[0], a[1], ..., a[n-1].  This
      is different from m*lab
    * Of course, it is much easier to handle default values on the input
      parameters in Python
    * Element by element operation is the default in numpy.  To get the
      matrix behavior, the array must be converted to matrices.  Also,
      when dealing with arrays, we do not need to use the dot notation of
      m*lab  (ie x./y).  Also numpy has the a concept called broadcasting
      so that we can write and expression such as 1/x  which, if x is a
      array becomes  [[1/x[0,0], 1/x[0,1], ... rather than ones(n,n)./x
    * Some of the numpy functions take tuples for the shapes of arrays
      (notably zeros, ones, etc) while others do not (random.randn())
    * The m*lab routines that take matrix size arguments generally assume
      that a single dimension, say n, means the matrix is square, say n by n.
      This means that when you want a vector, you have to give the function
      _two_ arguments ie say zeros(n,1) or ones(1,n) etc. In numpy, one
      dimension is the default and we use zeros(n) etc.  When we need a
      two dimensional array we use zeros((m,n))
      
Comments and references were mostly preserved in the functions.  They were
slightly updated to reflect the changes necessary in Python

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
   
Don MacMillen 7 Nov 2010
"""

__version__ = "0.2.0"
   
from matrices import *
from utils import *

