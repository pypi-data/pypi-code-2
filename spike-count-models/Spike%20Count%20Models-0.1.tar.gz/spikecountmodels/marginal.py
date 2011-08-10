# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2010 Bernstein Center for Computational Neuroscience Berlin   #
# author: André Großardt, based on Matlab code from Arno Onken                #
# contributor(s): Mahmoud Mabrouk					      #
#                                                                             #
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
# 2011-08-05: New distributions added, bugs corrected			      
# =========================================================================== #
#
###############################################################################

"""
Marginal distributions
"""


from numpy  import (abs, array, atleast_2d, isscalar, log, matrix, ones, tile,
                    zeros, exp)
from scipy.stats    import nbinom, poisson
from scipy.optimize import fmin, fmin_slsqp
from scipy.special  import gammaln
import pdb
import spikecountmodels.config as config
from spikecountmodels.tools import float_info
import scipy.stats as ss
import numpy as np
class Marginal:
    """
    Main class for marginals
    """
    def __init__(self):
        """
        Initialisation
        """
        self.dimension = 1
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        Raises NotImplementedError for the main class.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        """
        eval_points = atleast_2d(eval_points)
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        raise NotImplementedError, '%s CDF not implemented' % self.__class__
    
    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        Raises NotImplementedError for the main class.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        """
        eval_points = atleast_2d(eval_points)
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        raise NotImplementedError, '%s PDF not implemented' % self.__class__
    
    def rand(self, n = 1):
        """
        Calculate random samples.
        Raises NotImplementedError for the main class.
        
        @type  n: Integer
        @param n: Number of samples to calculate
        """
        raise NotImplementedError, '%s RAND not implemented' % self.__class__
    
    def fit(self, data):
        """
        Fit parameters according to given data.
        Raises NotImplementedError for the main class.
        
        @type  data: 1-d array or list
        @param data: Data to fit
        """
        raise NotImplementedError, '%s FIT not implemented' % self.__class__
    
    def plot_cdf(self, eval_points, options):
        """
        Plot the CDF.
        Not implemented yet.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        """
        raise NotImplementedError, '%s PLOT CDF not implemented' % self.__class__
    
    def plot_pdf(self, eval_points, options):
        """
        Plot the PDF.
        Not implemented yet.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        """
        raise NotImplementedError, '%s PLOT PDF not implemented' % self.__class__
        
    def inverse(self, p):
        """
        Calculate the inverese of the PDF.
        Raises NotImplementedError for the main class.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse PDF is evaluated
        """
        raise NotImplementedError, '%s INVERSE not implemented'               \
                                                               % self.__class__
    
    def set_param(self, mu):
        """
        Set the marginal parameter
        
        @param mu: New parameter
        """
        return True
    
    def get_param(self):
        """
        Get the marginal parameter
        
        @return: Marginal parameter
        """
        return 0


class DiscreteMarginal(Marginal):
    """
    Main class for discrete marginals
    """
    def __init__(self, mu = None):
        """
        Initialization
        
        @type  mu: Array
        @param mu: Parameter of the marginal
        """
        if mu == None:
            self.mu = array([[]])
        else:
            self.mu = atleast_2d(mu).astype('float')
    
    def is_discrete(self):
        """
        True for discrete marginal
        """
        return True
    
    def set_param(self, mu):
        """
        Set the marginal parameter
        
        @param mu: New parameter
        """
        if mu == None:
            self.mu = array([[]])
        else:
            self.mu = atleast_2d(mu).astype('float')
    
    def get_param(self):
        """
        Get the marginal parameter
        
        @return: Marginal parameter
        """
        return self.mu


class ContinuousMarginal(Marginal):
    """
    Main class for continuous marginals
    """
    def __init__(self, mu = None):
        """
        Initialization
        
        @type  mu: Array
        @param mu: Parameter of the marginal
        """
        if mu == None:
            self.mu = array([[]])
        else:
            self.mu = atleast_2d(mu).astype('float')
            
    def set_param(self, mu):
        """
        Set the marginal parameter
        
        @param mu: New parameter
        """
        if mu == None:
            self.mu = array([[]])
        else:
            self.mu = atleast_2d(mu).astype('float')      
                      
    def is_discrete(self):
        """
        False for continuous marginal
        """
        return False
        
    def get_param(self):
        """
        Get the marginal parameter
        
        @return: Marginal parameter
        """
        return self.mu
class Exponential(ContinuousMarginal):
    """
    Exponential marginal (continuous distribution)
    
    The parameter for this class id mu = \lambda
    The CDF of this distribution is 1-e^{-\lambda\dot x} 
    and the PDF is \lambda e^{-\lambda\dot x} 
    """
    
    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        @rtype:  Array
        @return: Array of CDF values of same shape as I{eval_points}
        """
        # Postinitialize variable for processing 
        if isscalar(eval_points): 
            x = array([eval_points])
        else:
            x = array(eval_points)
        if len(x.shape) == 1:
            x = atleast_2d(x)
            vector_output = True
        else:
            x = x.transpose()
            vector_output = False
        lambd = self.mu[0]
        loc = self.mu[1]
        return 1 - exp( -lambd * (x-loc)) 
	
    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the PDF is evaluated
        @rtype:  Array
        @return: Array of PDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            x = array([eval_points])
        else:
            x = array(eval_points)
        if len(x.shape) == 1:
            x = atleast_2d(x)
            vector_output = True
        else:
            x = x.transpose()
            vector_output = False
        lambd = self.mu[0]
        loc = self.mu[1]
        return lambd * exp( -lambd * (x-loc)) 
	
    def fit(self, data):
        """
        Fit parameters according to given data AND set the attributes of the
        current instance to this values
        
        @type  data: 1-d array or list
        @param data: Data to fit
        @rtype:  1-d array
        @return: Parameter vector mu
        """
        loc,lambd=ss.expon.fit(data)

        mu = [lambd, loc]
        self.mu = mu
        return mu        
    
    def rand(self, cases = 1):
        """
        Generate samples from the exponential distribution
        @type cases: integer
        @param cases: number of samples to generate
        @rtype: 1-d array
        @return: samples generated from the distribution
        """
        return np.random.exponential(1/self.mu[0] + self.mu[1], cases)
    
    def inverse(self, p):
        """
        Calculate the inverse of the CDF.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse CDF is evaluated
        """
        return ss.expon.ppf(p, self.mu[1], self.mu[0])
                

class Gamma(ContinuousMarginal):
    """
    Gamma marginal (continuous distribution)
    
    The parameter for this class id mu = [k \theta]

    """
    def __init__(self, shape=2, loc=0, scale=3):
        self.mu = [shape, loc, scale]

    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        @rtype:  Array
        @return: Array of CDF values of same shape as I{eval_points}
        """
        # Postinitialize variable for processing 
        if isscalar(eval_points): 
            x = array([eval_points])
        else:
            x = array(eval_points)
        if len(x.shape) == 1:
            x = atleast_2d(x)
            vector_output = True
        else:
            x = x.transpose()
            vector_output = False
        mu = self.mu
        tmp = ss.gamma.cdf(x, mu[0], mu[1], mu[2])
        return tmp

    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the PDF is evaluated
        @rtype:  Array
        @return: Array of PDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            x = array([eval_points])
        else:
            x = array(eval_points)
        if len(x.shape) == 1:
            x = atleast_2d(x)
            vector_output = True
        else:
            x = x.transpose()
            vector_output = False
        mu = self.mu
        tmp = ss.gamma.pdf(x, mu[0], mu[1], mu[2])
        return tmp

    def fit(self, data):
        """
        Fit parameters according to given data AND set the attributes of the
        current instance to this values
        
        @type  data: 1-d array or list
        @param data: Data to fit
        @rtype:  1-d array
        @return: Parameter vector mu
        """
        shape,loc,scale=ss.gamma.fit(data)

        mu = [shape, loc, scale]
        self.mu = mu
        return mu
        
    def inverse(self, p):
        """
        Calculate the inverese of the CDF.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse CDF is evaluated
        @rtype:  Array
        @return: Array of x-values with same shape as I{p}
        """
        return ss.gamma.ppf(p, self.mu[0], self.mu[1], self.mu[2])

    def rand(self, cases = 1):
        """
        Calculate random samples.
        
        @type  cases: Integer
        @param cases: Number of samples to calculate
        @rtype:  1-d array
        @return: cases-dimensional vector of samples
        """
        return np.random.gamma(self.mu[0], self.mu[2], cases) + self.mu[1]

class NegativeBinomial(DiscreteMarginal):
    """
    Negative binomial marginal
    
    The parameter for this class is mu = [\lambda, \nu] where the negative
    binomial distribution has the CDF
    F(r; \lambda, \nu) = \sum_{k=0}^{\text{floor}(r)} \frac{\lambda^k}{k!}
    * \left(1+\frac{\lambda}{\nu}\right)^{-\nu}
    * \frac{\Gamma(\nu + k)}{\Gamma(\nu) (\nu + \lambda)^k}
    """
    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        @rtype:  Array
        @return: Array of CDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            x = array([eval_points])
        else:
            x = array(eval_points)
        if len(x.shape) == 1:
            x = atleast_2d(x)
            vector_output = True
        else:
            x = x.transpose()
            vector_output = False
        mu = self.mu
        l = tile(mu[:, 1], (x.shape[1], 1)).transpose()
        r = tile(mu[:, 1] / (mu[:, 0] + mu[:, 1]), (x.shape[1], 1)).transpose()
        p = nbinom.cdf(x, l, r)
        shape = p.shape
        p = p.flatten()
        x = x.flatten()
        if (l >= float_info.max).any():
            k = (l >= float_info.max).flatten().nonzero()[0]
            rk, ck = (l >= float_info.max).nonzero()
            murk = []
            for i in rk:
                murk.append(mu[i,0])
            p[k] = poisson.cdf(x[k], murk)
        if vector_output:
            return p
        else:
            return p.reshape(shape).transpose()
    
    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the PDF is evaluated
        @rtype:  Array
        @return: Array of PDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            x = array([eval_points])
        else:
            x = array(eval_points)
        if len(x.shape) == 1:
            x = atleast_2d(x)
            vector_output = True
        else:
            x = x.transpose()
            vector_output = False
        mu = self.mu
        l = tile(mu[:, 1], (x.shape[1], 1)).transpose()
        r = tile(mu[:, 1] / (mu[:, 0] + mu[:, 1]), (x.shape[1], 1)).transpose()
        p = nbinom.pmf(x, l, r)
        shape = p.shape
        p = p.flatten()
        x = x.flatten()
        if (l >= float_info.max).any():
            k = (l >= float_info.max).flatten().nonzero()[0]
            rk, ck = (l >= float_info.max).nonzero()
            murk = []
            for i in rk:
                murk.append(mu[i,0])
            p[k] = poisson.pmf(x[k], murk)
        if vector_output:
            return p
        else:
            return p.reshape(shape).transpose()
    
    def fit(self, data):
        """
        Fit parameters according to given data AND set the attributes of the
        current instance to this values
        
        @type  data: 1-d array or list
        @param data: Data to fit
        @rtype:  1-d array
        @return: Parameter vector mu
        """
        data = array(data)
        if len(data.shape) == 1:
            data = atleast_2d(data).transpose()
        d = data.shape[1]
        mu = zeros((d,2))
        for i in range(d):
            x = data[:, i]
            m = x.mean()
            v = x.var()
            if m >= v:
                mu[i, 0] = m
                mu[i, 1] = float_info.max
            else:
                f = lambda r: _nbinom_neg_loglikelihood(r, len(x), x, x.sum())
                rhat = fmin(f, m*m/(v-m))
                phat = rhat / (m + rhat)
                mu[i, 0] = rhat * (1./phat - 1.)
                mu[i, 1] = rhat
        self.__init__(mu)
        return mu
                
    def inverse(self, p):
        """
        Calculate the inverese of the CDF.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse PDF is evaluated
        @rtype:  Array
        @return: Array of x-values with same shape as I{p}
        """
        mu = self.mu
        p = array(p)
        if len(p.shape) == 1:
            p = atleast_2d(p)
            vector_output = True
        else:
            p = p.transpose()
            vector_output = False
        l = tile(mu[:, 1], (p.shape[1], 1)).transpose()
        r = tile((mu[:, 1] / (mu[:, 0]+mu[:, 1])), (p.shape[1], 1)).transpose()
        x = nbinom.ppf(p, l, r)
        shape = x.shape
        x = x.flatten()
        p = p.flatten()
        if (l >= float_info.max).any():
            k = (l >= float_info.max).flatten().nonzero()[0]
            rk, ck = (l >= float_info.max).nonzero()
            murk = []
            for i in rk:
                murk.append(mu[i,0])
            x[k] = poisson.ppf(p[k], murk)
        if vector_output:
            return x
        else:
            return x.reshape(shape).transpose()
    
    def rand(self, cases):
        """
        Calculate random samples.
        
        @type  cases: Integer
        @param cases: Number of samples to calculate
        @rtype:  1-d array
        @return: cases-dimensional vector of samples
        """
        return np.random.negative_binomial(self.mu[0, 1], 1 / (self.mu[0, 0]/self.mu[0,1] + 1), cases)

    def str(self):
        """
        Return information about the marginal instance as string
        """
        return 'Negative Binomial with parameter %s' % self.mu


class NegativeBinomialMixture(DiscreteMarginal):
    """
    Mixture of negative binomial marginals
    """
    def __init__(self, mus = 2):
        """
        Initialization
        
        @type  mus: List or Integer
        @param mus: List of mu parameters for each marginal in the mixture
                    and the mixture matrix as last element.
                    If an integer I{i} is given, an empty marginal mixture with
                    I{i} components will be created.
        """
        if isscalar(mus):
            mus = zeros(int(mus) + 1)
        self.mu = atleast_2d(mus[-1]).astype('float')
        self.marginals = []
        for i in range(len(mus) - 1):
            self.marginals.append(NegativeBinomial(mus[i]))
    
    def components(self):
        """
        Number of mixed margins
        """
        return len(self.marginals)
            
    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        @rtype:  Array
        @return: Array of CDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            x = array([eval_points])
        else:
            x = array(eval_points)
        vector_output = False
        if len(x.shape) == 1:
            x = atleast_2d(x).transpose()
            vector_output = True
        p = zeros(x.shape)
        for i in range(self.components()):
            p = p + (array(tile(matrix(self.mu)[i, :], (x.shape[0], 1))) *
                     self.marginals[i].cdf(x))
        if vector_output:
            return p.flatten()
        else:
            return p
    
    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the PDF is evaluated
        @rtype:  Array
        @return: Array of PDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            x = array([eval_points])
        else:
            x = array(eval_points)
        vector_output = False
        if len(x.shape) == 1:
            x = atleast_2d(x).transpose()
            vector_output = True
        p = zeros(x.shape)
        for i in range(self.components()):
            p = p + (array(tile(matrix(self.mu)[i, :], (x.shape[0], 1))) *
                     self.marginals[i].pdf(x))
        if vector_output:
            return p.flatten()
        else:
            return p
    
    def fit(self, data, number_of_components = None):
        """
        Fit parameters according to given data AND set the attributes of the
        current instance to this values
        
        @type  data: 1-d array or list
        @param data: Data to fit
        @rtype:  1-d array
        @return: Parameter vector mu
        """
        if number_of_components == None:
            m = self.components()
        else:
            m = number_of_components
            if m < 2 or not type(m) == type(1):
                raise ValueError, 'number of components must be an integer > 1'   
        data = array(data)
        if len(data.shape) == 1:
            data = atleast_2d(data).transpose()
        # Dimension
        d = data.shape[1]
        # Convergence tolerance for EM
        tol = 1e-3
        # Initialize mu
        mu = []
        for i in range(m):
            mu.append(ones((d, 2)) * (i + 1))
        mu.append(ones((m, d)) / m)
        # Parameter bounds
        bounds = [(tol, float_info.max)] * (2*m)
        for i_d in range(d):
            # EM
            mu_d = []
            for i in range(m):
                mu_d.append(mu[i][i_d, :])
            mu_d.append(mu[-1][:, i_d])
            z = zeros(m)
            while abs(z - mu_d[-1]).mean() > tol:
                # Latest weighted probabilities
                wpdf = zeros((data.shape[0], m))
                for i in range(m):
                    margin = NegativeBinomial(mu_d[i])
                    wpdf[:, i] = (mu_d[-1].transpose().flatten()[i]
                                  * margin.pdf(data[:, i_d]))
                # E-step
                z = mu_d[-1]
                mu_d[-1] = (wpdf/tile(wpdf.sum(1), (m, 1)).transpose()).mean(0)
                # M-step
                mu_init = zeros(2 * m)
                for j in range(m):
                    mu_init[2*j] = mu_d[j][0]
                    mu_init[2*j+1] = mu_d[j][1]
                mu_min = fmin_slsqp(_negative_logarithm_minimization_function,
                      mu_init, args = (data[:,i_d], mu_d[-1]), bounds = bounds)
                z_c = mu_d[-1]
                mu_d = []
                for i_c in range(len(z_c)):
                    mu_d.append([mu_min[2*i_c], mu_min[2*i_c+1]])
                mu_d.append(z_c)
            for i in range(m):
                mu[i][i_d, :] = mu_d[i]
            mu[-1][:, i_d] = mu_d[-1]
        self.__init__(mu) 
        return mu
        
    def inverse(self, p):
        """
        Calculate the inverese of the CDF.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse PDF is evaluated
        @rtype:  Array
        @return: Array of x-values with same shape as I{p}
        """
        if isscalar(p):
            p = array([p])
        p = array(p)
        vector_output = False
        if len(p.shape) == 1:
            p = atleast_2d(p).transpose()
            vector_output = True
        max_p = p.max(0)
        max_x = ones(p.shape[1])
        i_p = zeros(p.shape[1])
        count = 0
        while (i_p < max_p).any() and count < config.WHILE_LOOP_ABORT:
            count = count + 1
            if count == config.WHILE_LOOP_ABORT:
                raise OverflowError, 'while loop did not end for %s runs'     \
                                                      % config.WHILE_LOOP_ABORT
            max_x = max_x + 1
            i_p = self.cdf(max_x)
        max_x = int(max_x.max())
        cdf = zeros((max_x, p.shape[1]))
        for i in range(max_x):
            cdf[i, :] = self.cdf(ones((1, p.shape[1])) * i)
        x = zeros(p.shape)
        for i in range(p.shape[0]):
            for j in range(p.shape[1]):
                x[i, j] = (p[i, j] > cdf[:, j]).sum()
        if vector_output:
            return x.flatten()
        else:
            return x


class DiscreteEmpiricalMarginal(DiscreteMarginal):
    """
    Discrete empirical marginal
    """
    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        @rtype:  Array
        @return: Array of CDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            eval_points = array([eval_points])
        x = array(eval_points).astype('int')
        vector_output = False
        if len(x.shape) == 1:
            x = atleast_2d(x).transpose()
            vector_output = True
        mu = self.mu
        length = max(mu.shape)
        x[x > length] = length
        x[x < 0] = 0
        mu = mu.cumsum(1)
        p = zeros(x.shape)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if (mu.shape >= array([j + 1, x[i, j] + 1])).all():
                    p[i, j] = mu[j, x[i, j]]
                else:
                    p[i, j] = 1
        if vector_output:
            return p.flatten()
        else:
            return p
        
    
    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the PDF is evaluated
        @rtype:  Array
        @return: Array of PDF values of same shape as I{eval_points}
        """
        if isscalar(eval_points):
            eval_points = array([eval_points])
        mu = self.mu
        #if not (mu[:, -1] == 0).all():
        #    raise ValueError, 'mu does not have the right format'
        x = array(eval_points).astype(int)
        vector_output = False
        if len(x.shape) == 1:
            x = atleast_2d(x).transpose()
            vector_output = True
        length = max(mu.shape)
        x[x > length - 1] = length - 1
        x[x < 0] = length - 1
        p = zeros(x.shape)
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                p[i, j] = mu[j, x[i, j]]
        if vector_output:
            return p.flatten()
        else:
            return p
    
    def fit(self, data):
        """
        Fit parameters according to given data AND set the attributes of the
        current instance to this values
        
        @type  data: 1-d array or list
        @param data: Data to fit
        @rtype:  1-d array
        @return: Parameter vector mu
        """
        data = array(data)
        if len(data.shape) == 1:
            data = atleast_2d(data).transpose()
        d = data.shape[1]
        m = data.max()
        l = zeros((d, m+1))
        for i in range(m+1):
            l[:,i] = (data == i).sum(0)
        # Normalize
        mu = l / tile(l.sum(1), (l.shape[1], 1)).transpose()
        self.__init__(mu)
        return mu
    
    def inverse(self, p):
        """
        Calculate the inverese of the CDF.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse PDF is evaluated
        @rtype:  Array
        @return: Array of x-values with same shape as I{p}
        """
        l = self.mu.cumsum(1)
        p = array(p)
        vector_output = False
        if len(p.shape) == 1:
            p = atleast_2d(p).transpose()
            vector_output = True
        x = zeros(p.shape)
        for i in range(p.shape[0]):
            for j in range(p.shape[1]):
                x[i, j] = (p[i, j] > l[j, :]).sum()
        if vector_output:
            return x.flatten()
        else:
            return x
    
    def str(self):
        return 'Discrete Empirical Marginal with parameter %s' % self.mu


class Poisson(DiscreteMarginal):
    """
    Poisson distribution
    """
    def cdf(self, eval_points):
        """
        Cumulative distribution function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the CDF is evaluated
        @rtype:  Array
        @return: Array of CDF values of same shape as I{eval_points}
        """
        if self.mu == 0.:
            return 1.
        return poisson.cdf(eval_points, self.mu)
        
    
    def pdf(self, eval_points):
        """
        Probability density function of the marginal distribution.
        
        @type  eval_points: 1-d or 2-d array or list
        @param eval_points: Points at which the PDF is evaluated
        @rtype:  Array
        @return: Array of PDF values of same shape as I{eval_points}
        """
        return poisson.pmf(eval_points, self.mu)
    
    def fit(self, data):
        """
        Fit parameters according to given data AND set the attributes of the
        current instance to this values
        
        @type  data: 1-d array or list
        @param data: Data to fit
        @rtype:  1-d array
        @return: Parameter vector mu
        """
        # mu is expectation value
        mu = array(data).mean() + 0.000000000000001 #To avoid nan values in pdf with a mean 0
        self.mu = mu
        return mu
    
    def inverse(self, p):
        """
        Calculate the inverese of the CDF.
        
        @type  p: 1-d or 2-d array or list
        @param p: Points at which the inverse PDF is evaluated
        @rtype:  Array
        @return: Array of x-values with same shape as I{p}
        """
        return poisson.ppf(p, self.mu)
    
    def rand(self, n = 1):
        """
        Calculate random samples from a poisson distribution 
        (Algorithm: Knuth (1969). Seminumerical Algorithms. The Art of Computer Programming, Volume 2)
        Raises NotImplementedError for the main class.
        
        @type  n: Integer
        @param n: Number of samples to calculate
        """
        data = np.zeros((n), float)
        for i in range(n):
            L = np.exp(-self.mu)
            k = 0
            p = 1
            while (p>=L):
                k = k + 1
                p = p * np.random.rand()
            data[i] = k -1
        return data
    
    
def _nbinom_neg_loglikelihood(r, lx, x, sx):
    """Helper function"""
    if r < 1e-6:
        return float_info.max
    else:
        xbar = sx / lx
        return (-(gammaln(r+x)).sum() + lx*gammaln(r) - lx*r*log(r/(xbar+r))
                  - sx*log(xbar/(xbar+r)))

# Convert parameter array to data array
def _negative_logarithm_minimization_function(mu_par, x, z):
    """Helper function"""
    c = []
    for i in range(array(z.shape).max()):
        c.append([mu_par[2*i], mu_par[2*i+1]])
    c.append(atleast_2d(z).transpose())
    m = NegativeBinomialMixture(c)
    return -log(m.pdf(x)).sum()
