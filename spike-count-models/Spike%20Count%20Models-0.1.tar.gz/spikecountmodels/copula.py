# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2010 Bernstein Center for Computational Neuroscience Berlin   #
# author: André Großardt, based on Matlab code from Arno Onken                #
# contributor(s): Mahmoud Mabrouk                                             #
#									                                          #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################
#
# === ChangeLog ============================================================= #
# 2010-09-15: First release version
# 2011-08-05: Sampling added to new copulas, bugs corrected
# =========================================================================== #
#
###############################################################################

"""
Copulas
"""
from math   import pi
from numpy  import (abs, append, atleast_2d, argsort, array, concatenate, dot,
                    exp, eye, log, isscalar, isfinite, logical_and,
                    logical_not, logical_or, matrix, mgrid, ones, sign, sin,
                    sqrt, tile, zeros)
from numpy.random           import gamma, rand, randint
from scipy.stats            import logser, expon, norm, t
from scipy.special          import expm1
from scipy.optimize         import fsolve
import spikecountmodels.config as config
from spikecountmodels.tools.matrix                                            \
                            import binary_combinations, is_positive_definite
from spikecountmodels.tools.stats import debye_1, factorial,                  \
                                         weighted_random_integer
from spikecountmodels.distributions.mvnormal                                  \
                            import MultivariateNormalDistribution
from spikecountmodels.distributions.mvstudentt                                \
                            import MultivariateStudentTDistribution
from spikecountmodels.tools import float_info
import numpy as np



class Copula:
    """
    Main class for Copulas
    """
    def __init__(self, dimension = 1):
        """
        Initialization
        
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        @rtype:  Copula
        @return: Copula
        """
        
        self.dimension = dimension
        self.alpha = 0
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        Raises NotImplementedError for the main class.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        raise NotImplementedError, '%s CDF not implemented' % self.__class__
    
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        Raises NotImplementedError for the main class.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        raise NotImplementedError, '%s PDF not implemented' % self.__class__
    
    def gradient(self, eval_points):
        """
        Gradient for the copula.
        Raises NotImplementedError for the main class.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        """
        raise NotImplementedError, '%s GRADIENT not implemented'              \
                                                               % self.__class__
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        Raises NotImplementedError for the main class.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        """
        raise NotImplementedError, '%s RAND not implemented' % self.__class__
    
    def fit(self, data):
        """
        Fit copula parameters according to given data.
        Raises NotImplementedError for the main class.
        
        @type  data: 1-d array
        @param data: Data to be fitted
        """
        raise NotImplementedError, '%s FIT not implemented' % self.__class__
    
    def plot(self, function, options = {}, label = ''):
        """
        Function to plot the CDF or PDF
        
        @type  function: Function
        @param function: Function to plot
        @type  options: Dictionary
        @param options: Option set for the plot:
                            - B{type}: Type of the plot, '3d' or default
                            (String)
                            - B{steps}: Number of steps in each dimension for
                            how many points the function is evaluated (Integer,
                            default: 100)
                            - B{color}: True or False (default: False)
                            - B{plot_steps}: Density of the grid in 3d-plot
                            (Integer, default: 25)
                            - B{xlabel}: Label for the x-axis (String)
                            - B{ylabel}: Label for the y-axis (String)
                            - B{zlabel}: Label for the z-axis (String)
                            - B{vmin}: Minimum value for color scale (if none
                            is specified use max(0, min(data)))
                            - B{vmax}: Maximum value for color scale (if none
                            is specified use min(10, max(data)))
        @type  label: String
        @param label: Default value for zlabel (is overwritten by options)
        """
        # load matplotlib modules
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import pylab
        from mpl_toolkits.mplot3d   import axes3d
        
        # Specify default options
        default = {}
        # Steps in data sample (steps^2 data points)
        default['steps']        = 100
        # Number of lines in plot
        default['plot_steps']   = 25
        # Plot type, ('3d' or default)
        default['type']         = ''
        # coloring (colored or black/white)
        default['color']        = False
        # Axis labels
        default['xlabel']       = '$u_{1}$'
        default['ylabel']       = '$u_{2}$'
        default['zlabel']       = label
        # Min./Max. values for color scale
        default['vmin']         = None
        default['vmax']         = None
        # Set default options where nothing specified
        for key in default.keys():
            if not key in options:
                options[key] = default[key]
        if not self.dimension == 2:
            raise NotImplementedError, 'Plot works only for two-dimensional ' \
                                       'copulas'
        dx = options['steps'] * 1j
        a = 0
        b = 1
        x, y = mgrid[a:b:dx, a:b:dx]
        mx = atleast_2d(x.flatten())
        my = atleast_2d(y.flatten())
        ep = concatenate((mx, my)).transpose()
        data = function(ep).reshape(x.shape)
        if options['type'].lower() == '3d':
            # 3D Plot
            ax = axes3d.Axes3D(plt.figure())
            pstr = int(options['steps'] / options['plot_steps'])
            ax.plot_wireframe(x, y, data, rstride = pstr, cstride = pstr)
            ax.set_xlabel(options['xlabel'])
            ax.set_ylabel(options['ylabel'])
            ax.set_zlabel(options['zlabel'])
        else:
            # Shade plot (default)
            if options['color']:
                col = None
            else:
                col = cm.gray
            if options['vmin'] == None:
                options['vmin'] = array([data.min(), 0]).max()
            if options['vmax'] == None:
                options['vmax'] = array([data.max(), 10]).min()
            im = plt.imshow(data, interpolation = 'bilinear', cmap = col,
                            origin = 'lower', extent = [0,1,0,1],
                            vmin = options['vmin'], vmax = options['vmax'])
            pylab.xlabel(options['xlabel'])
            pylab.ylabel(options['ylabel'])
            pylab.colorbar()
        plt.show()
    
    def plot_cdf(self, options = {}):
        """
        Function to plot the CDF
        
        @type  options: Dictionary
        @param options: Option set for the plot:
                            - B{type}: Type of the plot, '3d' or default
                            (String)
                            - B{steps}: Number of steps in each dimension for
                            how many points the function is evaluated (Integer,
                            default: 100)
                            - B{color}: True or False (default: False)
                            - B{plot_steps}: Density of the grid in 3d-plot
                            (Integer, default: 25)
                            - B{xlabel}: Label for the x-axis (String)
                            - B{ylabel}: Label for the y-axis (String)
                            - B{zlabel}: Label for the z-axis (String)
                            - B{vmin}: Minimum value for color scale (if none
                            is specified use max(0, min(data)))
                            - B{vmax}: Maximum value for color scale (if none
                            is specified use min(10, max(data)))
        """
        self.plot(self.cdf, options, 'CDF')
    
    def plot_pdf(self, options = {}):
        """
        Function to plot the PDF
        
        @type  options: Dictionary
        @param options: Option set for the plot:
                            - B{type}: Type of the plot, '3d' or default
                            (String)
                            - B{steps}: Number of steps in each dimension for
                            how many points the function is evaluated (Integer,
                            default: 100)
                            - B{color}: True or False (default: False)
                            - B{plot_steps}: Density of the grid in 3d-plot
                            (Integer, default: 25)
                            - B{xlabel}: Label for the x-axis (String)
                            - B{ylabel}: Label for the y-axis (String)
                            - B{zlabel}: Label for the z-axis (String)
                            - B{vmin}: Minimum value for color scale (if none
                            is specified use max(0, min(data)))
                            - B{vmax}: Maximum value for color scale (if none
                            is specified use min(10, max(data)))
        """
        self.plot(self.pdf, options, 'PDF')
        
    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        return 1
    
    def real_number_of_parameters(self):
        """
        For the FGM copula this returns the number of parameters for the
        defined order, while I{number_of_parameters()} returns the maximal
        number of parameters.
        For the other copulas this is the same as I{number_of_parameters()}.
        """
        return self.number_of_parameters()
    
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        return CopulaConstraints()
    
    def flashlight(self, sector = None):
        """
        Return a flashlight transformed copula
        @type  sector: List
        @param sector: List of the dimensions that are transformed, can be
                       either a binary vector of length dimension or a list
                       of integers from 0 to dimension - 1.
        @rtype:  FlashlightTransformedCopula
        @return: Flashlight transformed copula
        """
        # if no sector argument is given assume survival transformation
        if sector == None:
            sector = ones(self.dimension)
        else:
            sector = array(sector)
        # allow sector as list of numbers of dimension (0,...,d-1), too
        if sector.max() > 1 or len(sector) < 2:
            sector = sector_transformation(sector, self.dimension)
        if (sector == 0).all():
            return self
        else:
            return FlashlightTransformedCopula(self, sector)
    
    def survival(self):
        """
        Return a survival transformed copula.
        Same as I{flashlight(range(dimension))}
        @rtype:  FlashlightTransformedCopula
        @return: Survival transformed copula
        """
        return self.flashlight(ones(self.dimension))
    
    def get_param(self):
        """
        Return the copula parameter
        """
        return self.alpha
    
    def set_param(self, alpha, autocorrect = False):
        """
        Set the copula parameter
        
        @param alpha: New copula parameter
        @type  autocorrect: Boolean
        @param autocorrect: If True the parameter is corrected instead of
                            raising an error if it is not in the right range.
        """
        self.alpha = alpha


class FlashlightTransformedCopula(Copula):
    """
    Class for the result of a flashlight transformation.
    Usually, this is not createt individually but obtained as result of
    the I{flashlight()} or I{survival()} method.
    """
    def __init__(self, original_copula, sector):
        """
        Initialization
        
        @type  original_copula: Copula
        @param original_copula: The copula before the transformation
        @type  sector: Sector argument of the transformation
        """
        self.original_copula = original_copula
        self.sector = sector
        self.dimension = original_copula.dimension
        self.alpha = original_copula.alpha
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        ntrials, d = eval_points.shape
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        s_d = self.sector.sum()
        bsets = ones((2**s_d, d), dtype = 'int')
        bcomb = binary_combinations(s_d)
        bsets[:, logical_not(self.sector == 0)] = bcomb
        # Terms with an even number of ones are positive
        signs = -ones(bcomb.shape[0])
        signs[bcomb.sum(1) % 2 == 0] = 1
        c_f = zeros(ntrials)
        for i in range(ntrials):
            v = tile(self.sector * (1 - eval_points[i, :]) + (1 - self.sector)
                     * eval_points[i, :], (bcomb.shape[0], 1))
            v[logical_not(bsets)] = 1
            c = self.original_copula.cdf(v)
            c_f[i] = (signs * c).sum()
        return c_f
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        u = atleast_2d(u)
        ntrials, d = u.shape
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        s_d = self.sector.sum()
        bsets = ones((2**s_d, d), dtype = 'int')
        bcomb = binary_combinations(s_d)
        bsets[:, logical_not(self.sector == 0)] = bcomb
        # Terms with an even number of ones are positive
        signs = -ones(bcomb.shape[0])
        signs[bcomb.sum(1) % 2 == 0] = 1
        c_f = zeros(ntrials)
        for i in range(ntrials):
            v = tile(self.sector * (1 - u[i, :]) + (1 - self.sector) * u[i, :],
                     (bcomb.shape[0], 1))
            v[logical_not(bsets)] = 1
            c = self.original_copula.gradient(v)
            c_f[i] = (signs * c).sum()
        return c_f
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        u = self.original_copula.rand(cases)
        s = self.sector.astype('bool')
        u[:, s] = 1. - u[:, s]
        return u
    
    def get_param(self):
        return self.original_copula.get_param()


class FrankCopula(Copula):
    """
    Frank copula
    """
    def __init__(self, alpha = 0, dimension = 2):
        """
        Initialization
        
        @type  alpha: Scalar
        @param alpha: Parameter of the copula
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        """
        if not isscalar(alpha):
            raise ValueError, 'alpha must be a scalar'
        elif dimension > 2 and alpha < 0:
            raise ValueError, 'alpha must not be negative for dimension > 2'
        else:
            self.alpha = alpha
            self.dimension = dimension
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        if self.alpha == 0:
            return eval_points.prod(1)
        elif self.alpha >= float_info.max:
            return 0
        else:
            return -log(1 + (expm1(-self.alpha * eval_points)).prod(1)
                        / expm1(-self.alpha)**(d - 1)) / self.alpha
    
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if not d in (2,3):
            raise ValueError, 'Copula implemented only for dimension 2 and 3'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        if d == 2:
            p = (exp(self.alpha * eval_points)).prod(1)
            res = -self.alpha * expm1(-self.alpha) * p / (1 + exp(-self.alpha)
                               * p - (exp(self.alpha * eval_points)).sum(1))**2
            edge = (eval_points == 0).any(1)
            res[edge] = 0
            return res
        else:
            # Not implemented:
            raise NotImplementedError, 'Frank PDF only implemented for two '  \
                                       'dimensions'
            ### Old Implementation below
            ### Do not trust in this
            u = eval_points[:, 0]
            v = eval_points[:, 1]
            w = eval_points[:, 2]
            s = u + v + w
            a = self.alpha
            epa = expm1(a)
            ema = expm1(-a)
            #return (
            oldresult = (
                        (
                            exp(-a * (1 + 2*s)) * ema**(1 - 2*d) * (epa
                            + exp(a*u) - exp(a + a*u) + exp(a*v) - exp(a*(u+v))
                            + exp(a*(1+u+v)) - exp(a + a*v) + exp(a*w)
                            - exp(a*(u+w)) + exp(a*(1+u+w)) - exp(a*(v+w))
                            + exp(a*(1+v+w)) + exp(a*s) - exp(a + a*w)
                            + exp(a*(1+s)) * (-1 + ema**d))* a**2
                        ) / (
                            1 + ema**(1-d) * expm1(-a * u) * expm1(-a * v)
                            * expm1(-a * w)
                        )**3
                    )
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        if self.dimension == 2:
            u1 = rand(cases)
            p = rand(cases)
            if abs(self.alpha) > log(float_info.max):
                u2 = (u1 < 0) + sign(self.alpha) * u1
            elif abs(self.alpha) > sqrt(float_info.epsilon):
                e = exp(-self.alpha * u1) * (1 - p) / p
                u2 = -log((e + exp(-self.alpha)) / (1 + e)) / self.alpha
            else:
                u2 = p
            return array([u1, u2]).transpose()
        else:
            x = rand(cases, self.dimension)
            if self.alpha > 0:
                # Apply algorithm by Marshall and Olkin (1988)
                # y is log series distributed
                y = logser.rvs(1 - exp(-self.alpha), size = cases)
                y = tile(y, (self.dimension, 1)).transpose()
                x = -log(1 - exp(log(x)/y) * (1-exp(-self.alpha))) / self.alpha
            return x
        
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        u = atleast_2d(u)
        s = 0
        for i in range(self.dimension):
            s = (s + (expm1(-self.alpha * u[:, range(i) +
                 range(self.dimension)[i+1:]])).prod(1)
                 * u.transpose().flatten()[i] * exp(-self.alpha * u[:, i]))
        ea  = expm1(-self.alpha)**(1 - self.dimension)
        eab = expm1(-self.alpha)**self.dimension
        eau = expm1(-self.alpha * u).prod(1)
        return (log(ea * eau + 1) / (self.alpha**2) - (-ea * s -
                         (exp(-self.alpha) * (1 - self.dimension) * eau) / eab)
                         / (self.alpha * (ea * eau + 1)))
    
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        if self.dimension <= 2:
            return CopulaConstraints()
        else:
            return CopulaConstraints(float_info.epsilon)
    
    def param_kendall(self, correlation_coefficient):
        """
        ???
        
        @type  correlation_coefficient: Scalar
        @param correlation_coefficient: Correlation coefficient
        """
        r = correlation_coefficient
        if r == 0:
            return 0
        elif abs(r) < 1:
            return fsolve(frank_root_kendall, sign(r), (r,))
        else:
            return sign(r) * float_info.max
    
    def str(self):
        """
        Return a string describing the copula.
        """
        return 'Frank Copula with parameter %s' % self.alpha


class FrankHigherOrderCopula(Copula):
    """
    Frank higher order copula
    """
    def __init__(self, alpha = None, dimension = 2):
        """
        Initialization
        
        @type  alpha: 1-d array or list
        @param alpha: Copula Parameter, vector of length
                      2^dimension - dimension - 1 (default: zeros)
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        """
        self.dimension = dimension
        if alpha == None:
            alpha = zeros(self.number_of_parameters())
        if isscalar(alpha):
            alpha = array([alpha])
        if not len(alpha) == self.number_of_parameters():
            raise ValueError, 'alpha must be a vector of length (2^dimension' \
                              '- dimension - 1)'
        self.alpha = alpha
    
    def set_param(self, alpha, autocorrect = False):
        """
        Set the copula parameter
        
        @param alpha: New copula parameter
        @type  autocorrect: Boolean
        @param autocorrect: If True the parameter is corrected instead of
                            raising an error if it is not in the right range.
        """
        if isscalar(alpha):
            alpha = array([alpha])
        if not len(alpha) == self.number_of_parameters():
            raise ValueError, 'alpha must be a vector of length (2^dimension' \
                              '- dimension - 1)'
        self.alpha = alpha
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        # All binary combinations
        bcomb = binary_combinations(self.dimension)
        # Summation over all combinations of order >= 2
        sbcomb = bcomb.sum(1)
        bcomb  = bcomb[sbcomb >= 2]
        sbcomb = sbcomb[sbcomb >= 2]
        # Sort bcomb according to the number of elements
        # (corresponds to order of correlations)
        si = argsort(sbcomb)
        bcomb = bcomb[si, :]
        # Matrix to compute p
        ap = zeros((eval_points.shape[0], bcomb.shape[0]))
        for i in range(bcomb.shape[0]):
            dim = bcomb[i, :].sum()
            alpha = self.alpha[i]
            if dim > 2 and alpha < 0:
                alpha = 0
            copula = FrankCopula(alpha, dim)
            ap[:, i] = (copula.cdf(eval_points[:, bcomb[i, :]])
                        * eval_points[:, logical_not(bcomb[i, :])].prod(1))
        return ap.sum(1) / len(self.alpha)
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        # Vector of length cases of random integers in [1, 2^d-d)
        m = randint(0, 2**self.dimension - self.dimension - 1, cases)
        # All binary combinations
        bcomb = binary_combinations(self.dimension)
        # Summation over all combinations of order >= 2
        sbcomb = bcomb.sum(1)
        bcomb  = bcomb[sbcomb >= 2]
        sbcomb = sbcomb[sbcomb >= 2]
        # Sort bcomb according to the number of elements
        # (corresponds to order of correlations)
        si = argsort(sbcomb)
        bcomb = bcomb[si, :]
        x = rand(cases, self.dimension)
        for i in range(cases):
            copula = FrankCopula(self.alpha[m[i]], sbcomb[m[i]])
            x[i, bcomb[m[i], :]] = copula.rand(1).flatten()
        return x
    
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        npar = self.number_of_parameters()
        order = self.dimension * (self.dimension - 1) / 2
        lb = zeros(npar)
        lb[range(order)] = -float_info.max
        return CopulaConstraints(lb, ones(npar) * float_info.max)
        
    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        return 2**self.dimension - self.dimension - 1

class ClaytonCopula(Copula):
    """
    Clayton copula
    """
    def __init__(self, alpha = 1, dimension = 2):
        """
        Initialization
        
        @type  alpha: Scalar
        @param alpha: Copula Parameter (must be non-negative)
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        """
        if not (isscalar(alpha) and (0 <= alpha)):
            raise ValueError, 'alpha must be a non-negative scalar'
        self.alpha = alpha
        self.dimension = dimension

    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if d > 2 and self.alpha < 0:
            raise ValueError, 'alpha must be non-negative for d > 2'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        if self.alpha <= 0:
            return eval_points.prod(1)
        else:
            s = (eval_points**(-self.alpha)).sum(1) - d + 1
            s[s < 0.] = 0.
            return exp(-log(s) / self.alpha)
        
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        n, d = eval_points.shape
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if self.alpha <= 0:
            return ones(n)
        else:
            alpha = array(self.alpha)
            s = (eval_points**(-alpha)).sum(1) - d + 1
            s[s < 0.] = 0.
            log_c = -log(s) / alpha
            res = (alpha * range(d) + 1).prod() * exp((1 + alpha * d)
                       * log_c - (alpha + 1) * log(eval_points).sum(1))
            edge = (eval_points == 0).any(1)
            res[edge] = 0
            return res
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        # Apply algorithm by Marshall and Olkin (1988)
        u = rand(cases, self.dimension)
        if self.alpha <= 0:
            return u
        y = gamma(1 / self.alpha, size = (cases, 1))
        y = tile(y, (1, self.dimension))
        return (1. - log(u) / y)**(-1. / self.alpha)
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        u = atleast_2d(u)
        uas = (u**(-self.alpha)).sum(1) - self.dimension + 1
        return (log(uas) / (self.alpha**2) - (-log(u) / (u**self.alpha)).sum(1)
                                  / (self.alpha * uas)) / uas**(1 / self.alpha)
    
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        return CopulaConstraints(0)
    
    def str(self):
        """
        Return a string describing the copula.
        """
        return 'Clayton Copula with parameter %s' % self.alpha


class AliMikhailHaqCopula(Copula):
    """
    Ali-Mikhail-Haq copula
    """
    def __init__(self, alpha = .5, dimension = 2):
        """
        Initialization
        
        @type  alpha: Scalar
        @param alpha: Copula Parameter, must be in [-1,1)
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        """
        if not (isscalar(alpha) and (-1 <= alpha < 1)):
            raise ValueError, 'alpha must be a scalar in [-1,1)'
        self.alpha = alpha
        self.dimension = dimension
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if d > 2 and self.alpha < 0:
            raise ValueError, 'alpha must be non-negative for d > 2'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        return (self.alpha - 1) / (self.alpha - ((1 - self.alpha + self.alpha *
                                           eval_points) / eval_points).prod(1))
    
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if not d == 2:
            raise ValueError, 'AliMikhailHaqCopula PDF not implemented for '  \
                              'dimension greater than 2'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        z = -1 + self.alpha * (eval_points - 1).prod(1)
        res = (-1 - self.alpha * (-1 + eval_points.sum(1)
                                  + eval_points.prod(1) + z)) / (z**3)
        edge = (eval_points == 0).any(1)
        res[edge] = 0
        return res
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        u = atleast_2d(u)
        s = 0
        for i in range(self.dimension):
            s = s + (self.alpha * u[:, range(i) + range(self.dimension)[i+1:]]
                     - self.alpha + 1).prod(1) * (1 - u[:, i])
        au = (self.alpha * u - self.alpha + 1).prod(1)
        up  = u.prod(1)
        return 1. / (self.alpha - au / up) - ((self.alpha - 1)
                                    * (1 + s / up)) / (self.alpha - au / up)**2

    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        if self.dimension <= 2:
            return CopulaConstraints(-1, 1)
        else:
            return CopulaConstraints(0, 1)


class GumbelCopula(Copula):
    """
    Gumbel-Hougaard copula
    """
    def __init__(self, alpha = 2, dimension = 2):
        """
        Initialization
        
        @type  alpha: Scalar
        @param alpha: Copula Parameter, must be >= 1
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        """
        if not (isscalar(alpha) and alpha >= 1):
            raise ValueError, 'alpha must be a scalar >= 1'
        self.alpha = alpha
        self.dimension = dimension
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        return exp(-((-log(eval_points))**self.alpha).sum(1)**(1./self.alpha))
    
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if ((eval_points > 1).any() or (eval_points < 0).any() or
            (eval_points == 1).all()):
            return zeros(eval_points.shape[0])
        g = ((-log(eval_points))**self.alpha).sum(1)
        ia = 1. / self.alpha
        c = exp(-g**ia)
        l = (-log(eval_points)).prod(1)**(self.alpha-1)/eval_points.prod(1) * c
        if d == 2:
            res = l * (g**(2 * (ia - 1)) + (self.alpha - 1) * g**(ia - 2))
        else:
            res = l * (g**(3 * (ia - 1)) + 3 * (self.alpha - 1)
                       * g**(2 * ia - 3) + (2 * self.alpha**2 - 3 * self.alpha
                       + 1) * g**(ia - 3))
        edge = (eval_points == 0).any(1)
        res[edge] = 0
        return res
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        # Apply algorithm by Marshall and Olkin (1988)
        u = rand(cases, self.dimension)
        # y is Levy alpha-stable distributed, Chambers, Mallows, Stuck (1976)
        theta = rand(cases) * pi
        w = expon.rvs(size = cases)
        ia = 1. / self.alpha
        a = (sin((1 - ia) * theta) * sin(ia * theta)**(ia / (1. - ia)) /
             sin(theta)**(1. / (1. - ia)))
        y = (a / w)**((1 - ia) * self.alpha)
        y = tile(y, (self.dimension, 1)).transpose()
        return exp(-(-log(u) / y)**ia)
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        u = atleast_2d(u)
        lua   = (-log(u))**self.alpha
        lus  = lua.sum(1)
        lusa = lus**(1. / self.alpha)
        return -exp(-lusa) * lusa * (((lua * log(-log(u))).sum(1)) /
                                 (self.alpha * lus) - log(lus) / self.alpha**2)
    
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        return CopulaConstraints(1)


class FarlieGumbelMorgensternCopula(Copula):
    """
    Farlie-Gumbel-Morgenstern copula
    """
    def __init__(self, alpha = None, dimension = 2, order = None):
        """
        Initialization
        
        @type  alpha: 1-d array or list
        @param alpha: Copula Parameter, vector of length
                      2^dimension - dimension - 1 (default: zeros)
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        """
        self.dimension = dimension
        if alpha == None:
            self.alpha = zeros(self.number_of_parameters())
        else:
            if isscalar(alpha):
                alpha = array([alpha])
            alpha = array(alpha).flatten()
            if not len(alpha) == self.number_of_parameters():
                raise Warning, 'Number of Parameters for the FGM Copula '     \
                               'is not 2^dim - dim - 1'
            if not ((-1 <= alpha).all() and (alpha <= 1).all()):
                raise ValueError, 'alpha must be in [-1,1]^(2^dim - dim - 1)'
            else:
                self.alpha = alpha
    
    def set_param(self, alpha, autocorrect = False):
        """
        Set the copula parameter
        
        @param alpha: New copula parameter
        @type  autocorrect: Boolean
        @param autocorrect: If True the parameter is corrected instead of
                            raising an error if it is not in the right range.
        """
        if isscalar(alpha):
            alpha = array([alpha])
        alpha = array(alpha).flatten()
        if not len(alpha) == self.number_of_parameters():
            raise Warning, 'Number of Parameters for the FGM Copula '         \
                           'is not 2^dim - dim - 1'
        if autocorrect:
            for i in range(len(alpha)):
                if alpha[i] > 1:
                    alpha[i] = 1
                elif alpha[i] < -1:
                    alpha[i] = -1
        elif not ((alpha >= -1).all() and (alpha <= 1).all()):
            raise ValueError, 'alpha must be in [-1,1]^(2^dim - dim - 1)'
        self.alpha = alpha
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        # See Nelsen (1999) p. 87.
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        # All binary combinations
        bcomb = binary_combinations(d)
        # Check additional parameter constraint
        ecomb = ones(bcomb.shape)
        ecomb[bcomb] = -1
        # Summation over all combinations of order >= 2
        sbcomb = bcomb.sum(1)
        bcomb  = bcomb[sbcomb >= 2]
        sbcomb = sbcomb[sbcomb >= 2]
        # Sort bcomb according to the number of elements
        # (corresponds to order of correlations)
        si = argsort(sbcomb)
        bcomb = bcomb[si, :]
        # Further reduce the number of combinations by excluding those for
        # which alpha is zero
        nz = logical_not(self.alpha == 0)
        bcomb = bcomb[nz, :]
        alpha = self.alpha[nz]
        if len(alpha) == 0:
            return eval_points.prod(1)
        # Linear constraints matrix
        ac = zeros((ecomb.shape[0], bcomb.shape[0]))
        # Matrix to compute p
        ap = zeros((eval_points.shape[0], bcomb.shape[0]))
        for i in range(bcomb.shape[0]):
            ac[:, i] = -(ecomb[:, bcomb[i, :]]).prod(1)
            ap[:, i] = (1 - eval_points[:, bcomb[i, :]]).prod(1)
        # Linear constraint ac * alpha <= 1
        if (matrix(ac) * matrix(alpha).transpose() > 1).any():
            raise ValueError, 'Constraint for alpha violated'
        return eval_points.prod(1) * (1 + array(matrix(ap)
                                      * matrix(alpha).transpose()).flatten())
    
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        # See Nelsen (1999) p. 87.
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        # All binary combinations
        bcomb = binary_combinations(self.dimension)
        # Check additional parameter constraint
        ecomb = ones(bcomb.shape)
        ecomb[bcomb] = -1
        # Summation over all combinations of order >= 2
        sbcomb = bcomb.sum(1)
        bcomb  = bcomb[sbcomb >= 2]
        sbcomb = sbcomb[sbcomb >= 2]
        # Sort bcomb according to the number of elements
        # (corresponds to order of correlations)
        si = argsort(sbcomb)
        bcomb = bcomb[si, :]
        # Further reduce the number of combinations by excluding those for
        # which alpha is zero
        nz = logical_not(self.alpha == 0)
        bcomb = bcomb[nz, :]
        alpha = self.alpha[nz]
        # Linear constraints matrix
        ac = zeros((ecomb.shape[0], bcomb.shape[0]))
        # Matrix to compute p
        ap = zeros((eval_points.shape[0], bcomb.shape[0]))
        for i in range(bcomb.shape[0]):
            ac[:, i] = -(ecomb[:, bcomb[i, :]]).prod(1)
            ap[:, i] = (1 - 2 * eval_points[:, bcomb[i, :]]).prod(1)
        # Linear constraint ac * alpha <= 1
        malpha = matrix(alpha).transpose()
        if (matrix(ac) * malpha > 1).any():
            raise ValueError, 'Constraint for alpha violated'
        if len(alpha) == 0:
            return 1
        else:
            return array(1 + matrix(ap) * malpha).flatten()
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        alpha = array(self.alpha)
        # All binary combinations
        bcomb = binary_combinations(self.dimension)
        # Summation over all combinations of order >= 2
        sbcomb = bcomb.sum(1)
        bcomb  = bcomb[sbcomb >= 2]
        sbcomb = sbcomb[sbcomb >= 2]
        # Sort bcomb according to the number of elements
        # (corresponds to order of correlations)
        si = argsort(sbcomb)
        bcomb = bcomb[si, :]
        # Further reduce the number of combinations by excluding those for
        # which alpha is zero
        nz = logical_not(alpha == 0)
        bcomb = bcomb[nz, :]
        alpha = alpha[nz]
        x = zeros((cases, self.dimension))
        reevaluate = ones(cases, 'bool')
        while cases > 0:
            ap = zeros((cases, bcomb.shape[0]))
            # Independent uniform random numbers
            w = rand(cases, self.dimension)
            if (alpha == 0).all():
                # Independence
                x[reevaluate, :] = w
            else:
                # Initialize with .5 => unprocessed product terms will be zero
                x[reevaluate, :] = .5 * ones((cases, self.dimension))
                # See Armstrong and Galli (2002): contains some mistakes though
                x[reevaluate, 0] = w[:, 0]
                for i in range(self.dimension - 1):
                    for j in range(bcomb.shape[0]):
                        ap[:, j] = (1-2*x[reevaluate][:, bcomb[j, :]]).prod(1)
                    b = 1 + array(matrix(ap)
                                  * matrix(alpha).transpose()).flatten()
                    x[reevaluate, i+1] = 0
                    for j in range(bcomb.shape[0]):
                        ap[:, j] = (1-2*x[reevaluate][:, bcomb[j, :]]).prod(1)
                    a = array(matrix(ap) * matrix(alpha).transpose()).flatten()
                    x[array(range(cases))[reevaluate], i+1] = (a + b
                          - sqrt((a + b)**2 - 4 * a * b * w[:, i+1])) / (2 * a)
            reevaluate = logical_or(x > 1, x < 0).any(1)
            cases = reevaluate.sum()
        return x
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        u = atleast_2d(u)
        # All binary combinations
        bcomb = binary_combinations(self.dimension)
        # Summation over all combinations of order >= 2
        sbcomb = bcomb.sum(1)
        bcomb  = bcomb[sbcomb >= 2]
        sbcomb = sbcomb[sbcomb >= 2]
        # Sort bcomb according to the number of elements
        # (corresponds to order of correlations)
        si = argsort(sbcomb)
        bcomb = bcomb[si, :]
        # Compute gradient
        y = zeros((u.shape[0], bcomb.shape[0]))
        for i in range(bcomb.shape[0]):
            y[:, i] = (1 - u[:, bcomb[i, :]]).prod(1)
        return tile(u.prod(1), (y.shape[1], 1)).transpose() * y

    def constraints(self, order = None):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        if self.dimension <= 2:
            return CopulaConstraints(-1, 1)
        else:
            npar = self.number_of_parameters(order)
            # All binary combinations
            bcomb = binary_combinations(self.dimension)
            ecomb = ones(bcomb.shape)
            ecomb[bcomb] = -1
            # Summation over all combinations of order >= 2
            sbcomb = bcomb.sum(1)
            bcomb  = bcomb[sbcomb >= 2]
            sbcomb = sbcomb[sbcomb >= 2]
            # Sort bcomb according to the number of elements
            # (corresponds to order of correlations)
            si = argsort(sbcomb)
            bcomb = bcomb[si, :]
            bcomb = bcomb[range(npar), :]
            # Linear constraints matrix
            ac = zeros((ecomb.shape[0], npar))
            for i in range(npar):
                ac[:, i] = -(ecomb[:, bcomb[i, :]]).prod(1)
            # Linear constraint ac * alpha <= 1
            b = ones(ecomb.shape[0])
            lb = -ones(npar)
            ub = ones(npar)
            return CopulaConstraints(lb, ub, ac, b)
    
    def number_of_parameters(self, order = None):
        """
        Returns the (maximal) number of parameters of the copula.
        """
        if self.dimension <= 2:
            return 1
        else:
            if order == None:
                order = self.dimension
            if order > self.dimension:
                raise ValueError, 'order must be lower or equal dimension'
            npar = 0
            fac = factorial(self.dimension)
            for i in range(order - 1):
                npar = npar + fac / (factorial(i + 2) *
                                             factorial(self.dimension - i - 2))
            return npar
    
    def real_number_of_parameters(self):
        """
        Returns the number of parameters for the defined order
        """
        if self.dimension <= 2:
            return 1
        else:
            return len(self.alpha)


class FrechetHoeffdingLowerBound(Copula):
    """
    The Frechet-Hoeffding Lower Bound.
    This is NOT a copula for d > 2 (because it is not d-increasing for d > 2).
    """
    def __init__(self, dimension = 2):
        """
        Initialization
        """
        self.dimension = dimension
        self.alpha = 0
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        p = eval_points.sum(1) - d + 1
        p[p < 0] = 0
        return p

    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        return 0
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
                
        @type  cases: Integer
        @param cases: Number of samples to generate.
        """
        if dimension == 2:
            result = np.zeros((cases, 2), float)
            for i in range(0, cases):
                result[i, 0] = rand()
                result[i, 1] = 1 - rand()
            return result
        else:
            raise NotImplementedError, '%s sampling for more than two dimension not implemented'% self.__class__

class FrechetHoeffdingUpperBound(Copula):
    """
    Frechet Hoeffding upper bound
    """
    def __init__(self, dimension = 2):
        """
        Initialization
        """
        self.dimension = dimension
        self.alpha = 0
        
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        return eval_points.min(1)

    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        return 0
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        """
        if self.dimension == 2:
            result = np.zeros((cases, 2), float)
            for i in range(0, cases):
                result[i, 0] = rand()
                result[i, 1] = result[i, 0]
            return result
        else:
            raise NotImplementedError, '%s sampling for more than two dimension not implemented' % self.__class__

class CopulaMixture(Copula):
    """
    Mixture of copulas
    """
    def __init__(self, copulas, weights = []):
        """
        Initialization
        
        @type  copulas: List of Copula
        @param copulas: List of the mixed copulas
        @type  weights: 1-d array or list
        @param weights: Weight vector
        """
        self.copulas = copulas
        self.weights = normalize_weights(weights, len(copulas))
        self.dimension = copulas[0].dimension
        for c in copulas:
            if not self.dimension == c.dimension:
                raise ValueError, 'All copulas must have the same dimension'
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        p = 0
        for i in range(len(self.copulas)):
            p = p + self.weights[i] * self.copulas[i].cdf(eval_points)
        return p
    
    def pdf(self, eval_points):
        """
        Probability density function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        p = 0
        for i in range(len(self.copulas)):
            p = p + self.weights[i] * self.copulas[i].pdf(eval_points)
        return p
    
    def gradient(self, u):
        """
        Gradient for the copula.
        
        @type  u: 2-d array or list
        @param u: array of points at which the PDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        grad = 0
        for i in range(len(self.copulas)):
            grad = grad + self.weights[i] * self.copulas[i].gradient(u)
        return grad
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
        
        @type  cases: Integer
        @param cases: Number of samples to generate.
        @rtype:  2-d array
        @return: cases-by-dimension array of random samples
        """
        x = zeros((cases, self.dimension))
        for i in range(cases):
            # draw a copula index
            index = weighted_random_integer(self.weights)
            x[i, :] = self.copulas[index].rand()
        return x
    
    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        return len(self.get_param())
    
    def get_param(self):
        """
        Return the copula parameter
        """
        alpha = []
        for c in self.copulas:
            alpha.append(c.get_param())
        return array(alpha).flatten()
    
    def get_weights(self):
        """
        Return the weights of the mixed copulas
        """
        return self.weights
    
    def set_weights(self, weights):
        """
        Set the copula weights
        
        @param weights: New copula weights
        """
        self.weights = normalize_weights(weights, len(self.copulas))


class CopulaShuffle(Copula):
    """
    Shuffle of copulas
    """
    def __init__(self, outer_copula, inner_copula, omega = 0):
        """
        Initialization
        
        @type  outer_copula: Copula
        @param outer_copula: Outer copula
        @type  inner_copula: Copula
        @param inner_copula: Inner copula
        @type  omega: Scalar
        @param omega: border between inner and outer copula
        """
        copulas = (outer_copula, inner_copula)
        if not (isscalar(omega) and 0 <= omega <= 1):
            raise ValueError, 'omega has to be a scalar in [0, 1]'
        if omega > .5:
            omega = 1 - omega
        if not (len(copulas) == 2):
            raise ValueError, 'Only shuffles of exactly 2 copulas implemented'
        self.omega = omega
        self.copulas = copulas
        self.dimension = copulas[0].dimension
        if not self.dimension == 2:
            raise ValueError, 'CopulShuffle only implemented for dimension 2'
        for c in copulas:
            if not self.dimension == c.dimension:
                raise ValueError, 'All copulas must have the same dimension'
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        # Indices of inner square:
        k = logical_and((eval_points > self.omega).all(1),
                        (eval_points < 1 - self.omega).all(1))
        inner_u = eval_points[k, 0]
        inner_v = eval_points[k, 1]
        # Calculate CDF outside first
        p = self.copulas[0].cdf(eval_points)
        # Correction inside
        zeta = []
        for i in (0,1):
            c = lambda u, v: self.copulas[i].cdf(array([u, v]).transpose())
            zeta.append(lambda u1, v1, u2, v2: c(u2, v2) - c(u2, v1)
                                             - c(u1, v2) + c(u1, v1))
        omega = self.omega * ones(len(inner_u))
        m = array([inner_u, inner_v]).min(0)
        p[k] = (p[k] - zeta[0](omega, omega, inner_u, inner_v)
                     + zeta[0](omega, omega, m, 1 - omega)
                     / zeta[1](omega, omega, m, 1 - omega)
                     * zeta[1](omega, omega, inner_u, inner_v))
        return p

    def outer_copula(self):
        """
        Return the outer copula
        
        @rtype:  Copula
        @return: Outer copula
        """
        return self.copulas[0]
    
    def inner_copula(self):
        """
        Return the inner copula
        
        @rtype:  Copula
        @return: Inner copula
        """
        return self.copulas[1]


class FrankMixtureCopula(CopulaMixture):
    """
    Mixture of Frank copulas
    """
    def __init__(self, alpha = None, dimension = 2, weights = [1]):
        """
        Initialization
        
        @type  alpha: 1-d array
        @param alpha: Vector of parameters of the mixed Frank copulas
        @type  dimension: Integer
        @param dimension: Dimension of the copula
        @type  weights: 1-d array
        @param weights: Weight vector of the mixed Frank copulas
        """
        copulas = []
        if alpha == None:
            alpha = zeros(len(weights))
        if not len(alpha) == len(weights):
            raise ValueError, 'alpha and weights must have the same size'
        for a in alpha:
            copulas.append(FrankCopula(a, dimension))
        CopulaMixture.__init__(self, copulas, weights)
        
    def set_param(self, alpha, autocorrect = False):
        """
        Set the copula parameter
        
        @param alpha: New copula parameter
        @type  autocorrect: Boolean
        @param autocorrect: If True the parameter is corrected instead of
                            raising an error if it is not in the right range.
        """
        if not (isscalar(alpha) or len(alpha) == len(self.copulas)):
            raise ValueError, 'alpha has the wrong size'
        for i in range(len(self.copulas)):
            if isscalar(alpha):
                self.copulas[i].set_param(alpha, autocorrect)
            else:
                self.copulas[i].set_param(alpha[i], autocorrect)


class FrankShuffleCopula(CopulaShuffle):
    """
    Shuffle of Frank copulas
    """
    def __init__(self, alpha = [1, 1], omega = 0):
        if not (len(alpha) == 2):
            raise ValueError, 'alpha must be a vector of length 2'
        copulas = [FrankCopula(alpha[0]), FrankCopula(alpha[1])]
        CopulaShuffle.__init__(self, copulas, omega)


class NelsenShuffleCopula(CopulaShuffle):
    """
    Copula Shuffle described in Nelsen 2006, p. 75
    This copula has zero correlation for theta=(2-4^(1/3))/4 but is not the
    product copula.
    """
    def __init__(self, omega = (2. - 4.**(1. / 3.)) / 4):
        """
        Initialization
        
        @type  omega: Scalar
        @param omega: border between inner and outer copula
        """
        if not (isscalar(omega) and 0 <= omega <= 1):
            raise ValueError, 'omega must be a scalar in [0, 1]'
        outer_copula = FrechetHoeffdingLowerBound()
        inner_copula = FrechetHoeffdingUpperBound()
        CopulaShuffle.__init__(self, outer_copula, inner_copula, omega)
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        # Indices of inner square:
        k = logical_and((eval_points > self.omega).all(1),
                        (eval_points < 1 - self.omega).all(1))
        # Calculate CDF outside first
        p = self.copulas[0].cdf(eval_points)
        p[k] = self.copulas[1].cdf(eval_points[k, :]) - self.omega
        return p


class GaussianCopula(Copula):
    """
    Gaussian copula
    """
    def __init__(self, cov = None, dimension = 2):
        """
        Initialization
        
        @type  cov: Scalar, 2-d array or list
        @param cov: Covariance matrix (symmetric square matrix).
                    For 2-d the offdiagonal can be given as a scalar.
        @type  dimension: Integer
        @param dimension: Copula dimension
        """
        self.dimension = dimension
        self.alpha = 0
        if cov == None:
            cov = eye(dimension)
        elif dimension == 2 and isscalar(cov):
            cov = array([[1., cov], [cov, 1.]])
        else:
            cov = array(cov)
        if not (cov.shape[0] == cov.shape[1]):
            raise ValueError, 'cov must be a square matrix'
        if not (cov == cov.transpose()).all():
            raise ValueError, 'cov must be symmetric'
        if not is_positive_definite(cov):
            raise ValueError, 'cov must be positive definite'
        self.cov = cov
    
    def cdf(self, eval_points, maxpts = None):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @type  maxpts: Integer
        @param maxpts: Maximum number of function evaluations for multivariate
                       normal distribution function.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        n, d = eval_points.shape
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if maxpts == None:
            maxpts = self.dimension * 100000
        return MultivariateNormalDistribution.cdf(norm.ppf(eval_points),
                              zeros(self.dimension), self.cov, maxpts = maxpts)
    
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        if self.dimension <= 2:
            return CopulaConstraints(-1,1)
        else:
            npar = self.number_of_parameters()
            return CopulaConstraints(-ones(npar), ones(npar))
    
    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        if self.dimension <= 2:
            return 1
        else:
            return self.dimension * (self.dimension - 1) / 2
    
    def rand(self, cases = 1):
        """
        Generate random samples for the copula.
                
        @type  cases: Integer
        @param cases: Number of samples to generate.
        """
        if self.dimension == 2:
            result = np.zeros((cases, 2), float)
            for i in range(0, cases):
                cov = [[1, self.alpha],[self.alpha,1]]
                result[i, :] = norm.cdf( np.random.multivariate_normal([0, 0], cov, cases ) )
            return result
        else:
            raise NotImplementedError, '%s sampling for more than two dimension is not implemented' % self.__class__
    


class GaussianMixtureCopula(CopulaMixture):
    """
    Mixture of Gaussian copulas
    """
    def __init__(self, alpha = [None, None], dimension = 2, weight = 0):
        """
        Initialization
        
        @type  alpha: Scalar, 1-d array or list
        @param alpha: Copula parameter
        @type  dimension: Integer
        @param dimension: Copula dimension
        """
        if not (len(alpha) == 2):
            raise ValueError, 'alpha must be a vector of length 2'
        copulas = [GaussianCopula(alpha[0], dimension),
                   GaussianCopula(alpha[1], dimension)]
        CopulaMixture.__init__(self, copulas, weight)


class TCopula(Copula):
    """
    Gaussian copula
    """
    def __init__(self, cov = None, dof = None, dimension = 2):
        """
        Initialization
        
        @type  cov: Scalar, 2-d array or list
        @param cov: Correlation matrix (symmetric square matrix).
                      For 2-d the offdiagonal can be given as a scalar.
        @type  dof: Scalar
        @param dof: Degrees of freedom (nu parameter)
        @type  dimension: Integer
        @param dimension: Copula dimension
        """
        self.dimension = dimension
        self.alpha = 0
        if cov == None:
            cov = eye(dimension)
        elif dimension == 2 and isscalar(cov):
            cov = array([[1., cov], [cov, 1.]])
        else:
            cov = array(cov)
        if not (cov.shape[0] == cov.shape[1]):
            raise ValueError, 'cov must be a square matrix'
        if not (cov == cov.transpose()).all():
            raise ValueError, 'cov must be symmetric'
        if not is_positive_definite(cov):
            raise ValueError, 'cov must be positive definite'
        self.cov = cov
        if dof == None:
            self.dof = 1
        else:
            self.dof = dof
    
    def cdf(self, eval_points, maxpts = None):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @type  maxpts: Integer
        @param maxpts: Maximum number of function evaluations for multivariate
                       T distribution function.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        n, d = eval_points.shape
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if maxpts == None:
            maxpts = self.dimension * 100000
        return MultivariateStudentTDistribution.cdf(t.ppf(eval_points,
                                self.dof), self.cov, self.dof, maxpts = maxpts)
        
    def constraints(self):
        """
        Get the constraints for the copula class.
        
        @rtype:  CopulaConstraints
        @return: Empty CopulaConstraints instance
        """
        if self.dimension <= 2:
            return CopulaConstraints(-1,1)
        else:
            npar = self.number_of_parameters()
            return CopulaConstraints(-ones(npar), ones(npar))
    
    def number_of_parameters(self):
        """
        Returns the number of parameters of the copula.
        """
        if self.dimension <= 2:
            return 1
        else:
            return self.dimension * (self.dimension - 1) / 2


class IndependenceCopula(Copula):
    """
    Independence copula
    """
    def __init__(self, alpha = None, dimension = 2):
        """
        Initialization
        
        @type  alpha: Scalar, 1-d array or list
        @param alpha: Copula parameter
        @type  dimension: Integer
        @param dimension: Copula dimension
        """
        self.dimension = dimension
        self.alpha = 0
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function for the copula.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probabilities
        """
        eval_points = array(eval_points)
        if not len(eval_points.shape) == 2:
            raise ValueError, 'eval_points has wrong shape'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit copula dimension'
        if (eval_points > 1).any() or (eval_points < 0).any():
            return zeros(eval_points.shape[0])
        return eval_points.prod(1)

class CopulaConstraints:
    """
    Constraints for copulas
    """
    def __init__(self, lower_bound = -float_info.max,
                 upper_bound = float_info.max, linear_constraint_matrix = [],
                 linear_constraint_rhs = []):
        """
        Initialization, upper and lower bounds and a linear equality constraint
        A*x = b
        
        @type  lower_bound: Scalar
        @param lower_bound: Lower bound
        @type  upper_bound: Scalar
        @param upper_bound: Upper bound
        @type  linear_constraint_matrix: 2-d array or list
        @param linear_constraint_matrix: Matrix A
        @type  linear_constraint_rhs: 1-d array or list
        @param linear_constraint_rhs: Vector b
        """
        if isscalar(lower_bound):
            lower_bound = [lower_bound]
        if isscalar(upper_bound):
            upper_bound = [upper_bound]
        self.lower_bound = array(lower_bound).flatten()
        self.upper_bound = array(upper_bound).flatten()
        if not len(self.lower_bound) == len(self.upper_bound):
            raise ValueError, 'Bounds must have same size'
        self.linear_constraint_matrix = matrix(linear_constraint_matrix)
        self.linear_constraint_rhs = array(linear_constraint_rhs).flatten()
        
    def bounds(self, length = 1):
        """
        Return the bounds as required by scipy fmin functions
        
        @type  length: Integer
        @param length: Length of the returned list
        @rtype:  List
        @return: List of tuples [(lb1, ub1), (lb2, ub2), ...]
        """
        if len(self.lower_bound) == 1:
            return [(self.lower_bound[0], self.upper_bound[0])] * length
        else:
            l = []
            for i in range(len(self.lower_bound)):
                l.append((self.lower_bound[i], self.upper_bound[i]))
            if len(l) == length:
                return l
            elif len(l) > length:
                return l[:length]
            else:
                l2 = []
                for i in range(length):
                    l2.append(l[i % len(l)])
                return l2
    
    def lb(self, length = 1):
        """
        Return the lower bounds as vector
        
        @type  length: Integer
        @param length: Length of the returned list
        @rtype:  1-d array
        @return: Vector of lower bounds
        """
        if len(self.lower_bound) == 1:
            return [self.lower_bound[0]] * length
        else:
            l = []
            for i in range(len(self.lower_bound)):
                l.append(self.lower_bound[i])
            if len(l) == length:
                return l
            elif len(l) > length:
                return l[:length]
            else:
                l2 = []
                for i in range(length):
                    l2.append(l[i % len(l)])
                return l2
    
    def ub(self, length = 1):
        """
        Return the upper bounds as vector
        
        @type  length: Integer
        @param length: Length of the returned list
        @rtype:  1-d array
        @return: Vector of upper bounds
        """
        if len(self.upper_bound) == 1:
            return [self.upper_bound[0]] * length
        else:
            l = []
            for i in range(len(self.upper_bound)):
                l.append(self.upper_bound[i])
            if len(l) == length:
                return l
            elif len(l) > length:
                return l[:length]
            else:
                l2 = []
                for i in range(length):
                    l2.append(l[i % len(l)])
                return l2
        
    def constraint(self, x):
        """
        Constraint function, returns A*x - b
        
        @type  x: 1-d array
        @param x: Vector for which the constraint is evaluated
        @rtype:  1-d array
        @return: Resulting vector
        """
        x = matrix(array(x).flatten()).transpose()
        a = self.linear_constraint_matrix
        b = matrix(self.linear_constraint_rhs).transpose()
        return a * x - b
    
    def cobyla_constraints(self):
        """
        Formulate both the bounds and the equality constraints as inequality
        constraints
        
        @rtype:  List of functions
        @return: List of inequality constraint functions
        """
        constr = []
        # Bounds:
        constr.append(lambda x: (x - array(self.lb(len(x)))))
        constr.append(lambda x: (array(self.ub(len(x))) - x))
        # Constraints:
        aeq = self.linear_constraint_matrix
        beq = self.linear_constraint_rhs
        for i in range(len(beq)):
            constr.append(lambda x: (dot(aeq[i], x) - beq[i])) # ax >= beq
            constr.append(lambda x: (beq[i] - dot(aeq[i], x))) # ax <= beq
        return constr
    
    def eqcons(self):
        """
        Return the equality constraints as functions.
        
        @rtype:  List of functions
        @return: List of equality constraint functions
        """
        constr = []
        aeq = self.linear_constraint_matrix
        beq = self.linear_constraint_rhs
        for i in range(len(beq)):
            constr.append(lambda x: dot(aeq[i], x) - beq[i])
        return constr
    
    def str(self):
        """
        Return a string describing the copula.
        """
        return ('Lower Bounds: %s\n' % self.lower_bound
                + 'Upper Bounds: %s\n' % self.upper_bound
                + 'Linear Constraints: %s * x = %s'
                % (self.linear_constraint_matrix, self.linear_constraint_rhs))


def normalize_weights(weights, target_length):
    """
    Normalizes a weight vector to a vector of length I{target_length}.
    If I{weights} is too long it is cut off. If it is too short, the remaining
    weight (1 - sum(weights)) is distributed uniformly among the remaining
    components. If sum(weights) is larger or equal to one it is filled up with
    zeros.
    
    @type  weights: 1-d array or list
    @param weights: Weight vector
    @type  target_length: Integer
    @param target_length: Length of resulting weight vector
    @rtype:  1-d array
    @return: Normalized weight vector
    """
    weights = array(weights)
    # if weights too long: cut
    # if too short: distribute remaining weight (if any) uniformly
    if len(weights) > target_length:
        weights = weights[:target_length]
    elif len(weights) < target_length:
        if sum(weights) < 1:
            weights = append(weights, ones(target_length - len(weights))
                      * (1-sum(weights)) / (target_length-len(weights)))
        else:
            weights = append(weights, zeros(target_length - len(weights)))
    return weights / sum(weights)
    
def sector_transformation(sector, dimension):
    """
    Transforms a sector argument as list of integers to a binary vector.
    
    @type  sector: List
    @param sector: Sector argument as list of integers
    @type  dimension: Integer
    @param dimension: The dimension of the copula.
    """
    binary_sector = zeros(dimension)
    for i in sector:
        binary_sector[i] = 1
    return binary_sector

def frank_root_kendall(alpha, target):
    """
    ???
    """
    if abs(alpha) < sqrt(float_info.min):
        return -target
    else:
        return 1 + 4 * (debye_1(alpha) - 1) / alpha - target
