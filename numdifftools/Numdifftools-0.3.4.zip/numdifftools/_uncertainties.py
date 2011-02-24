import numpy as np
try:
    import uncertainties.unumpy as unp
except ImportError:
    unp = None

try:
    import uncertainties
except ImportError:
    uncertainties = None
    
class _Common(object):
    def __init__(self, fun):
        self.fun = uncertainties.wrap(fun)
            
    def _gradient(self, x):
        sx = unp.uarray((np.asarray(x), np.inf))
        sf = self.fun(sx)
        return np.array([sf.derivatives[var] for var in sx])
        
    def _hessian_reverse(self, x):
        return self._cg.hessian([np.asarray(x)])
    
     
class Gradient(_Common):
    '''Estimate gradient of fun at x0

    Assumptions
    -----------
      fun - SCALAR analytical function to differentiate.
            fun must be a function of the vector or array x0,
            but it needs not to be vectorized.

      x0  - vector location at which to differentiate fun
            If x0 is an N x M array, then fun is assumed to be
            a function of N*M variables.


    Examples
    -------- 
      #(nonlinear least squares)
    >>> xdata = np.reshape(np.arange(0,1,0.1),(-1,1))
    >>> ydata = 1+2*np.exp(0.75*xdata)
    >>> fun = lambda c: (c[0]+c[1]*np.exp(c[2]*xdata) - ydata)**2
    >>> Jfun = Gradient(fun)
    >>> Jfun([1,2,0.75]) # should be numerically zero
    array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
    >>> fun = lambda x: np.sum(x**2)
    >>> dfun = Gradient(fun)
    >>> dfun([1,2,3])
    array([ 2.,  4.,  6.])

    #At [x,y] = [1,1], compute the numerical gradient
    #of the function sin(x-y) + y*exp(x)

    >>> sin = np.sin; exp = np.exp
    >>> z = lambda xy: sin(xy[0]-xy[1]) + xy[1]*exp(xy[0])
    >>> dz = Gradient(z)
    >>> grad2 = dz([1, 1])
    >>> grad2
    array([ 3.71828183,  1.71828183])
     

    #At the global minimizer (1,1) of the Rosenbrock function,
    #compute the gradient. It should be essentially zero.

    >>> rosen = lambda x : (1-x[0])**2 + 105.*(x[1]-x[0]**2)**2
    >>> rd = Gradient(rosen)
    >>> grad3 = rd([1,1])
    >>> grad3==np.array([ 0.,  0.])
    array([ True,  True], dtype=bool)
    

    See also
    --------
    Derivative, Hessdiag, Hessian, Jacobian
    '''

    def gradient(self, x0):
        ''' Gradient vector of an analytical function of n variables
        '''
        return self._gradient(x0)
        
    def __call__(self,x): 
        return self._gradient(x)



if __name__ == '__main__':
    import doctest
    doctest.testmod()
     




