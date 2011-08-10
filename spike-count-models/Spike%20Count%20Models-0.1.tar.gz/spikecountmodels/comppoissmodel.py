# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2010 Bernstein Center for Computational Neuroscience Berlin   #
# author: André Großardt, based on Matlab code from Arno Onken                #
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
# =========================================================================== #
#
###############################################################################

"""
Compound Poisson Model
"""

import sys
import math
import copy
from numpy  import (abs, array, atleast_2d, concatenate, diag, dot, empty, exp,
                    eye, isnan, log2, logical_not, matrix, ones, sqrt, tile,
                    zeros)
from numpy.linalg   import det, pinv
from scipy.optimize import fmin, fmin_slsqp
from scipy.stats    import poisson
from mpl_toolkits.axes_grid import make_axes_locatable

import spikecountmodels.config as config
from spikecountmodels.tools.matrix   import *
from spikecountmodels.tools.stats    import *
from spikecountmodels.marginal       import *
from spikecountmodels.copula         import *
from spikecountmodels.model          import *


class CompoundPoissonModel(SpikeCountModel):
    """
    Compound Poisson model
    """
    def __init__(self, rates = None, mixture_matrix = None, dimension = 2):
        """
        Initialisation
        
        @type  rates: 1-d array or list
        @param rates: Vector of rates of independent variables (must be
                      non-negative)
        @type  mixture_matrix: 2-d array or list
        @param mixture_matrix: Mixture matrix with elements in [0, 1] (number
                               of columns must equal the length of I{rates})
        @type  dimension: Integer
        @param dimension: Dimension of the model
        @rtype:  CompoundPoissonModel
        @return: Multivariate Poisson model
        """
        if not rates == None:
            rates = array(rates).flatten()
            if (rates < 0).any():
                raise ValueError, 'rates must be non-negative'
        if not mixture_matrix == None:
            mixture_matrix = array(mixture_matrix)
            if not (len(rates) == mixture_matrix.shape[1] or rates == None):
                raise ValueError, 'columns of mixture matrix must fit length of'  \
                                  'rates vector'
        self.rates = rates
        self.mixture_matrix = mixture_matrix
        self.dimension = dimension
    
    def pdf(self, eval_points, approximate = False, order = 2):
        """
        Probability density function
        
        @type  eval_points: 2-d array or list
        @param eval_points: Array of points where the PDF is evaluated.
                            Trials-by-dimension matrix, where each row
                            corresponds to a d-dimensional vector for one
                            data point.
        @type  approximate: Boolean
        @param approximate: If True the PDF is approximated
        @type  order: Integer
        @param order: Order of the correlations that are not neglected
                      (relevant only if I{approximate} is True)
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        if isscalar(eval_points) or len(array(eval_points).shape) == 1:
            raise ValueError, 'eval_points must be a two-dimensional array'
        eval_points = array(eval_points)
        trials, n = eval_points.shape
        if approximate:
            if order > self.dimension:
                raise ValueError, 'Order must be lower or equal dimension'
            p = zeros(trials)
            # expectation
            ex = array(matrix(self.mixture_matrix)
                       * matrix(self.rates).transpose()).flatten()
            if order > 1:
                # Calculate central moments of Poisson
                cm = centralize_moments(poisson_moments(self.rates,
                                        range(1, order + 1)))
            for itrials in range(trials):
                s = 0
                for iorder in range(1, order):
                    # Ordered array of indices
                    counter = range(iorder + 1)
                    while counter[-1] < n:
                        # r = central moments of eval_points
                        enx = (cm[:, iorder]
                               * self.mixture_matrix[counter, :].prod(0)).sum()
                        s = s + enx * (eval_points[itrials, counter]
                                     - ex[counter]).prod() / ex[counter].prod()
                        # Increment counter array such that the elements are
                        # still ordered
                        ic = 0
                        while ic < iorder and counter[ic] == counter[ic+1]-1:
                            ic = ic + 1
                        counter[ic] = counter[ic] + 1
                        if ic > 0:
                            counter[:ic] = range(ic)
                if s <= -1:
                    # p cannot be negative => cut off at -1
                    s = -1 + sys.float_info.epsilon
                fac = empty(n)
                for ifac in range(n):
                    fac[ifac] = float(math.factorial(int(eval_points[itrials,
                                                                     ifac])))
                p[itrials] = (exp(-ex) * ex**eval_points[itrials, :]
                              / fac).prod() * (1 + s)
            return p
        else:
            nmu = len(self.rates)
            # Verify that mixture matrix starts with eye(n)
            if not (self.mixture_matrix == None or
                                   self.mixture_matrix[:, :n] == eye(n)).all():
                raise ValueError, 'mixture matrix not supported'
            # Separate mix. into identity and another matrix a2
            a2 = self.mixture_matrix[:, n:nmu]
            a2bool = a2 > 0
            if len(a2.flatten()) == 0:
                # Special case: independent elements
                mu = tile(self.rates, (trials, 1))
                return (poisson.pmf(eval_points, mu)).prod(0)
            else:
                p = zeros(trials)
                for itrials in range(trials):
                    s = 0
                    # Vector for all combinations
                    l = zeros(nmu - n)
                    # Vector with maximum values for l
                    lmax = zeros(nmu - n)
                    for ilmax in range(nmu - n):
                        values = a2[:, ilmax] * eval_points[ilmax, :]
                        lmax[ilmax] = values[a2bool[:, ilmax]].min()
                    # For all feasible combinations of l
                    lcontinue = True
                    loopcount = 0
                    while lcontinue and loopcount < config.WHILE_LOOP_ABORT:
                        loopcount = loopcount + 1
                        if loopcount == config.WHILE_LOOP_ABORT:
                            raise OverflowError, 'While loop took to long'
                        al = array(matrix(a2)*matrix(l).transpose()).flatten()
                        xsub = concatenate((eval_points[itrials, :] - al, l))
                        if (xsub >= 0).all():
                            pr = 1
                            for j in range(nmu):
                                pr = (pr * (self.rates[j]**xsub[j])
                                      / math.factorial(int(xsub[j])))
                            s = s + pr
                        # Loop increment
                        l[0] = l[0] + 1
                        li = 0
                        while lcontinue and l[li] > lmax[li]:
                            l[li] = 0
                            li = li + 1
                            if li >= nmu - n:
                                lcontinue = False
                            else:
                                l[li] = l[li] + 1
                    p[itrials] = exp(-self.rates.sum()) * s
                return p
    
    def log_pdf(self, eval_points, approximate = False, order = 2):
        """
        Logarithm of probability density function
        
        @type  eval_points: 2-d array or list
        @param eval_points: Array of points where the PDF is evaluated.
                            Trials-by-dimension matrix, where each row
                            corresponds to a d-dimensional vector for one
                            data point.
        @type  approximate: Boolean
        @param approximate: If True the PDF is approximated
        @type  order: Integer
        @param order: Order of approximation (only if I{approximate} is True)
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        if isscalar(eval_points) or len(array(eval_points).shape) == 1:
            raise ValueError, 'eval_points must be a two-dimensional array'
        eval_points = array(eval_points)
        trials, n = eval_points.shape
        if not n == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        if approximate:
            if order > self.dimension:
                raise ValueError, 'Order must be lower or equal dimension'
            p = zeros(trials)
            # expectation
            ex = array(matrix(self.mixture_matrix)
                       * matrix(self.rates).transpose()).flatten()
            if order > 1:
                # Calculate central moments of Poisson
                cm = centralize_moments(poisson_moments(self.rates,
                                        range(1, order + 1)))
            for itrials in range(trials):
                s = 0
                for iorder in range(1, order):
                    # Ordered array of indices
                    counter = range(iorder + 1)
                    while counter[-1] < n:
                        # r = central moments of eval_points
                        enx = (cm[:, iorder]
                               * self.mixture_matrix[counter, :].prod(0)).sum()
                        s = s + enx * (eval_points[itrials, counter]
                                     - ex[counter]).prod() / ex[counter].prod()
                        # Increment counter array such that the elements are
                        # still ordered
                        ic = 0
                        while ic < iorder and counter[ic] == counter[ic+1]-1:
                            ic = ic + 1
                        counter[ic] = counter[ic] + 1
                        if ic > 0:
                            counter[:ic] = range(ic)
                if s <= -1:
                    # p cannot be negative => cut off at -1
                    s = -1 + sys.float_info.epsilon
                logf = empty(n)
                for ifac in range(n):
                    logf[ifac] = log(float(math.factorial(int(
                                                 eval_points[itrials, ifac]))))
                p[itrials] = (-ex + eval_points[itrials, :] * log(ex)
                              - logf).sum() + log(1. + s)
            return p
        else:
            nmu = len(self.rates)
            # Separate mix. into identity and another matrix a2
            a2 = self.mixture_matrix[:, n:nmu]
            a2bool = a2 > 0
            if len(a2.flatten()) == 0:
                # Special case: independent elements
                mu = tile(self.rates, (trials, 1))
                return (log(poisson.pmf(eval_points, mu))).sum(1)
            else:
                p = zeros(trials)
                for itrials in range(trials):
                    s = 0
                    # Vector for all combinations
                    l = zeros(nmu - n)
                    # Vector with maximum values for l
                    lmax = zeros(nmu - n)
                    for ilmax in range(nmu - n):
                        values = a2[:, ilmax] * eval_points[itrials, :]
                        lmax[ilmax] = values[a2bool[:, ilmax]].min()
                    # For all feasible combinations of l
                    lcontinue = True
                    loopcount = 0
                    while lcontinue and loopcount < config.WHILE_LOOP_ABORT:
                        loopcount = loopcount + 1
                        if loopcount == config.WHILE_LOOP_ABORT:
                            raise OverflowError, 'While loop took to long'
                        al = array(matrix(a2)*matrix(l).transpose()).flatten()
                        xsub = concatenate((eval_points[itrials, :] - al, l))
                        if (xsub >= 0).all():
                            pr = 1
                            for j in range(nmu):
                                pr = (pr * (self.rates[j]**xsub[j])
                                      / math.factorial(xsub[j]))
                            s = s + pr
                        # Loop increment
                        l[0] = l[0] + 1
                        li = 0
                        while lcontinue and l[li] > lmax[li]:
                            l[li] = 0
                            li = li + 1
                            if li >= nmu - n:
                                lcontinue = False
                            else:
                                l[li] = l[li] + 1
                    if s == 0:
                        raise ArithmeticError, 'Probability too small'
                    p[itrials] = -self.rates.sum() + log(s)
                return p
    
    def pdf_by_montecarlo(self, eval_points, nsamples):
        """
        Estimates the probability density function for samples I{eval_points}
        of a multivariate Poisson distribution for the given rates and mixture
        matrix of the model by Monte-Carlo sampling with I{nsamples} samples.
        
        @type  eval_points: 2-d array or list
        @param eval_points: Array of points where the PDF is evaluated.
                            Trials-by-dimension matrix, where each row
                            corresponds to a d-dimensional vector for one
                            data point.
        @type  nsamples: Integer
        @param nsamples: Number of random samples to calculate
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        if isscalar(eval_points) or len(array(eval_points).shape) == 1:
            raise ValueError, 'eval_points must be a two-dimensional array'
        eval_points = array(eval_points)
        if type(nsamples) == type(1.):
            nsamples = int(nsamples)
        if not (type(nsamples) == type(1) and nsamples > 0):
            raise ValueError, 'nsamples must be a positive integer'
        trials = eval_points.shape[0]
        p = zeros(trials)
        for itrials in range(trials):
            xmc = self.rand(nsamples).transpose()
            p[itrials] = float((xmc == tile(eval_points[itrials, :],
                           (nsamples, 1))).all(0).sum()) / nsamples
        return p
    
    def pdf_by_saddlepoint(self, eval_points):
        """
        Calculates an approximation of the probability density function for
        samples I{eval_points} of a multivariate Poisson distribution for the
        given rates and mixture matrix of the model by means of the saddle
        point method (method of steepest descent, Laplace, stationary phase
        approximation).
        
        @type  eval_points: 2-d array or list
        @param eval_points: Array of points where the PDF is evaluated.
                            Trials-by-dimension matrix, where each row
                            corresponds to a d-dimensional vector for one
                            data point.
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        if isscalar(eval_points) or len(array(eval_points).shape) == 1:
            raise ValueError, 'eval_points must be a two-dimensional array'
        eval_points = array(eval_points)
        trials, n = eval_points.shape
        p = zeros(trials)
        for i in range(trials):
            # Search kappa consistent with eval_points
            kappa = array(matrix(pinv(self.mixture_matrix * tile(self.rates,
                          (n, 1)))) * matrix(eval_points[i, :]).transpose())
            g = exp(self.rates * (kappa - 1))
            phi0 = array(matrix(pinv(self.mixture_matrix).transpose())
                         * matrix(-log(kappa)))
            f_phi0 = ((matrix(eval_points[i, :]) * matrix(phi0)).transpose()
                      + log(g).sum())
            h = array(matrix(self.mixture_matrix * tile(self.rates
                             * kappa.flatten(), (n, 1)))
                             * matrix(self.mixture_matrix).transpose())
            p[i] = abs(exp(f_phi0) / sqrt((2 * math.pi)**n * det(h)))
        return p
    
    def rand(self, trials = 1, full_output = False):
        """
        Generates samples from a multivariate Poisson model for given rates and
        mixture matrix of independent Poisson variables.
        
        @type  trials: Integer
        @param trials: Number of samples (rows) to generate
        @type  full_output: Boolean
        @param full_output: If True: return (x, sigma)
                            If False: return only x
        @rtype:  Tuple or 2-d array (depending on I{full_output})
        @return: (x, sigma) where x is the I{trials}-by-dimension array of
                 a discrete random samples and sigma is the resulting
                 covariance matrix
        """
        if type(trials) == type(1.):
            trials = int(trials)
        if not (type(trials) == type(1) and trials >= 0):
            raise ValueError, 'trials must be a non-negative integer'
        ma = matrix(self.mixture_matrix)
        if trials <= 0:
            x = []
        else:
            # Generate univariate Poisson samples
            xp = poisson.rvs(tile(self.rates, (trials, 1)).transpose())
            # Mix samples
            x = array(ma * matrix(xp))
        if full_output:
            # Calculate covariance matrix
            sigma = array(ma * matrix(diag(self.rates)) * ma.transpose())
            return x, sigma
        else:
            return x
    
    def fit(self, data, approximate = False):
        """
        IMF fit of the model parameters according to a given data set.
        Returns rates and mixture matrix AND sets the attributes of the current
        instance to these values.
        
        @type  data: 2-d array or list
        @param data: Trials-by-dimension array of data points
        @type  approximate: Boolean
        @param approximate: If True perform optimization with bounds
                            (0, max(mean(data))), otherwise without bounds
        @rtype:  Tuple
        @return: (Rates, Mixture Matrix)
        """
        data = atleast_2d(data)
        ntrials, n = data.shape
        if not n == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        # IMF estimation: 2 stages
        # 1. Estimate parameters for marginal distributions
        mu = data.mean(0)
        # 2. Estimate correlation parameters
        # Exploit full structure of the multivariate Poisson distribution
        a = self.full_mixture()
        if n > 1:
            # Number of parameteres
            nl2 = a.shape[1] - n
            f = lambda l2: _multivariate_poisson_negative_logarithm(data,
                           concatenate((mu - array(matrix(a[:, n:])
                           * matrix(l2).transpose()).flatten(), l2)), a)
            if approximate:
                bounds = [(0, mu.max())] * nl2
                l2 = fmin_slsqp(f, zeros(nl2), bounds = bounds, acc = 1e-3)
            else:
                l2 = fmin(f, zeros(nl2))
            mu = abs(concatenate((mu - array(matrix(a[:, n:])
                       * matrix(l2).transpose()).flatten(), l2)))
        self.set_parameters(mu, a)
        return mu, a
    
    def full_mixture(self):
        """
        Generates a mixture matrix for a multivariate Poisson distribution
        with hidden variables and full structure.
        Depends only on the dimension of the current model instance.
        
        @rtype:  2-d array
        @return: Mixture matrix
        """
        a = zeros((2**self.dimension, self.dimension))
        for i in range(self.dimension):
            t = 2**i
            for j in range(2**(self.dimension - i - 1)):
                a[2*j*t:2*j*t+t, self.dimension - i - 1] = ones(t)
        a = a.transpose()
        if self.dimension > 1:
            # Sort according to the number of elements
            indices = argsort(a.sum(0))
        else:
            indices = [2, 1]
        return a[:, indices[1:]]
    
    def estimate_parameters(self, data):
        """
        IMF estimator for the model parameters according to a given data set.
        Returns rates and mixture matrix AND sets the attributes of the current
        instance to these values.
        
        @type  data: 2-d array or list
        @param data: Trials-by-dimension array of data points to be fitted
        @rtype:  Tuple
        @return: (Rates, Mixture Matrix)
        """
        data = atleast_2d(data)
        ntrials, n = data.shape
        # IMF estimation: 2 step maximum likelihood
        # 1. Estimate parameters for marginal distribution
        mu = data.mean(0)
        # 2. Estimate correlation parameters
        # Max. likelihood estimator for the correlation coefficients
        sigma = zeros((n, n))
        data = data - tile(mu, (ntrials, 1))
        for i in range(ntrials):
            sigma = sigma + array(matrix(data[i, :]).transpose()
                                  * matrix(data[i, :]))
        sigma = sigma / sqrt(array(matrix(diag(sigma)).transpose()
                                   * matrix(diag(sigma))))
        if n <= 3:
            margin_angle = math.pi
        else:
            margin_angle = math.pi / 2
        # Separate pairs into adjacent and distant
        nborder = int(margin_angle / (2 * math.pi) * n)
        a_angle = eye(n)
        for i in range(nborder):
            a_angle = a_angle + circshift(eye(n), i+1)
        a_angle = array(matrix(a_angle) * matrix(a_angle).transpose())
        adj_elements = (a_angle > 0) - eye(n)
        n_adj_elements = adj_elements.sum()
        dist_elements = (a_angle == 0)
        n_dist_elements = dist_elements.sum()
        # Compute vectors with correlation coefficients
        corr_adj = adj_elements * sigma
        corr_dist = dist_elements * sigma
        # Average correlation coefficients
        if n_adj_elements > 0:
            corr_adj = float(corr_adj.sum()) / n_adj_elements
            if corr_adj < 0:
                corr_adj = 0
        else:
            corr_adj = 0
        if n_dist_elements > 0:
            corr_dist = float(corr_dist.sum()) / n_dist_elements
            if corr_dist < 0:
                corr_dist = 0
        else:
            corr_dist = 0
        mu, a = _multivariate_poisson_cont(mu, margin_angle, margin_angle,
                                           corr_adj, corr_dist)
        self.set_parameters(mu, a)
        return mu, a
    
    def test(self, data, indices = None):
        """
        Test-set validation for the multivariate Poisson model.
        
        @type  data: List
        @param data: List of trials-by-dimension arrays
        @type  indices: 1-d array or list
        @param indices: List of indices, which data samples should be regarded
                        (default: all)
        @rtype:  1-d array
        @return: Vector of probabilities of same length as I{data}
        """
        if indices == None:
            indices = range(len(data))
        p = zeros(array(indices).max() + 1)
        for i in indices:
            datai = array(data[i])
            # Perform training and test
            ndata = datai.shape[0]
            trainset = range(0, ndata, 2)
            testset = range(1, ndata, 2)
            # Model fit
            lm, a = self.fit(datai[trainset, :])
            # Compute likelihood
            self.set_parameters(lm, a)
            p[i] = (log(self.pdf(atleast_2d(datai[testset, :])))).sum()
        return p
    
    def cross_validation(self, data, indices = None):
        """
        Leave-one-out cross-validation for the multivariate Poisson model.
        
        @type  data: List
        @param data: List of trials-by-dimension arrays
        @type  indices: 1-d array or list
        @param indices: List of indices, which data samples should be regarded
                        (default: all)
        @rtype:  1-d array
        @return: Vector of probabilities of same length as I{data}
        """
        if indices == None:
            indices = range(len(data))
        p = zeros(array(indices).max())
        indexp = 0
        for i in indices:
            datai = array(data[i])
            ndata = datai.shape[0]
            # Mean likelihood of data points for fitted models
            for j in range(ndata):
                trainset = logical_not(array(range(ndata)) == j)
                subdata = datai[trainset, :]
                # Model fit
                l, a = self.fit(subdata)
                # Compute likelihood
                self.__init__(l, a, datai.shape[1])
                p[indexp] = p[indexp] + self.log_pdf(atleast_2d(datai[j,:]))
            indexp = indexp + 1
        return p
    
    def number_of_parameters(self):
        """
        Return the number of parameters of this models
        """
        return 2**self.dimension - 1
    
    def set_parameters(self, rates, mixture_matrix):
        """
        Set the model parameters (rates and mixture matrix) of current instance
        
        @type  rates: 1-d array or list
        @param rates: Rates
        @type  mixture_matrix: 2-d array or list
        @param mixture_matrix: Mixture matrix
        """
        rates = array(rates).flatten()
        mixture_matrix = array(mixture_matrix)
        if (rates < 0).any():
            raise ValueError, 'rates must be non-negative'
        if not len(rates) == mixture_matrix.shape[1]:
            raise ValueError, 'columns of mixture matrix must fit length of ' \
                              'rates vector'
        self.rates = rates
        self.mixture_matrix = mixture_matrix


def _multivariate_poisson_negative_logarithm(data, rates, mixture_matrix):
    """Helper function"""
    rates = array(rates)
    if (rates < 0).any():
        return sys.maxint
    else:
        data = atleast_2d(data)
        m = CompoundPoissonModel(rates, mixture_matrix, data.shape[1])
        return -(m.log_pdf(data, approximate = True)).sum()

def _multivariate_poisson_cont(mu, margin_angle, adj_angle, corr_adj,
                               corr_dist = 0, a_param = 0):
    """Helper function"""
    mu = atleast_2d(mu).flatten()
    if not (isscalar(a_param) and 0 <= a_param <= 1):
        raise ValueError, 'a_param must be a scalar in [0, 1]'
    if not (isscalar(corr_dist) and 0 <= corr_dist <= 1):
        raise ValueError, 'corr_dist must be a scalar in [0, 1]'
    if (mu < 0).any():
        raise ValueError, 'mu must be non-negative'
    if not (isscalar(margin_angle) and 0 <= margin_angle
            <= 2 * math.pi):
        raise ValueError, 'margin_angle must be an angle'
    if not (isscalar(adj_angle) and 0 <= adj_angle
            <= 2 * math.pi):
        raise ValueError, 'adj_angle must be an angle'
    if not (isscalar(corr_adj) and 0 <= corr_adj <= 1):
        raise ValueError, 'corr_adj must be a scalar in [0, 1]'
    n = len(mu)
    if corr_adj == 0:
        l, a = mu, eye(n)
    else:
        # Number of required independent Poisson variables
        # Process special cases
        if n < 1:
            l = []
            a = []
        elif n == 1:
            l = mu
            a = 1
        elif n == 2:
            if corr_adj > 0:
                cov = corr_adj * sqrt(mu[0] * mu[1])
                l = concatenate((mu - cov, cov))
                a = array([[1,0,1],[0,1,1]])
            else:
                l = mu
                a = eye(2)
        else:
            if corr_dist == 0:
                n_l = 2 * n
            else:
                n_l = 2 * n + 1
            # Rates for independent univariate Poisson distributions
            l = zeros(n_l)
            a = zeros((n, n_l))
            # Compute matrix of adjacent elements
            n_margin = int(margin_angle / (2 * pi) * n)
            adj_elements = eye(n)
            for i in range(n_margin):
                adj_elements = adj_elements + circshift(eye(n), i+1)
            # Mixture matrix for diagonal elements
            a[:, :n] = eye(n)
            a[:, n:2*n] = adj_elements
            if not corr_dist == 0:
                # mixture matrix for common noise
                a[:, n_l] = ones(n)
            # Calculate appropriate covariances
            a_margin = array(matrix(a[:, n:2*n])
                             * matrix(a[:, n:2*n]).transpose())
            n_margin = int(adj_angle / (2 * math.pi) * n)
            a_adj = eye(n)
            for i in range(n_margin):
                a_adj = a_adj + circshift(eye(n), i+1)
            # Includes adjacent pairs to the separating angle
            a_adj = array(matrix(a_adj) * matrix(a_adj).transpose())
            # Includes distant pairs to the separating angle
            a_dist = (a_adj == 0)
            na_dist = a_dist.sum()
            # Includes pairs in the margin without the diagonal
            a_margin2 = a_margin - diag(diag(a_margin))
            na_margin2 = (a_margin2 > 0).sum()
            a_adj = a_adj - diag(diag(a_adj))
            na_adj = (a_adj > 0).sum()
            # Geometric mean for normalization
            geo_mean = sqrt(array(matrix(mu).transpose() * matrix(mu)))
            # Compute distant covariance
            if margin_angle > adj_angle:
                # Separate pair sets according to margin_angle and adj_angle
                a_e = a_margin2 * a_dist
                a_a = a_margin2 * (a_e == 0)
                a_d = a_dist * (a_e == 0)
                # Number of elements in a_a
                na_a = (a_a > 0).sum()
                # Sums of normalization factors in the different sets
                sa_e = (1. / geo_mean[a_e > 0]).sum(0)
                sa_a = (1. / geo_mean[a_a > 0]).sum(0)
                sa_d = (a_d / geo_mean).sum()
                sna_e = (a_e / geo_mean).sum()
                sna_a = (a_a / geo_mean).sum()
                # Algebra yields the following equation
                cov_dist = (corr_dist * na_dist / sa_d - (na_a * corr_adj
                            * sna_e) / (sa_d * sna_a)) / (1 + sa_e / sa_d
                            - (sa_a * sna_e) / (sa_d * sna_a))
                # TODO: case a != 0 (not 2level)
                # => Covariances in set a_a are not necessarily equal
            else:
                if na_dist > 0:
                    cov_dist = corr_dist * na_dist / (a_dist / geo_mean).sum()
                else:
                    cov_dist = 0
            # Adjacent covariances
            cov_adj = a_adj*(corr_adj*na_adj)/a_adj.sum() * geo_mean - cov_dist
            cov_adj[a_dist] = 0
            # Correct rates for diagonal elements
            wcov = zeros(na_adj / 2)
            anb = zeros((na_adj / 2, n))
            vector_sqrt = zeros(na_adj / 2)
            iwcov = 0
            for i in range(1,n):
                for j in range(i):
                    if a_adj[i, j] > 0:
                        wcov[iwcov] = cov_adj[i, j]
                        anb[iwcov, :] = a[i, n:2*n] * a[j, n:2*n]
                        vector_sqrt[iwcov] = geo_mean[i, j]
                        iwcov = iwcov + 1
            # Solve least-squares problem by applying the Moore-Penrose
            # pseudoinverse
            wl = array(matrix(pinv(anb)) * matrix(wcov).transpose())
            # The mean correlation is not necassarily the same anymore
            # => correction required
            if margin_angle > adj_angle:
                #diff_corr_adj = (array(matrix(anb) * matrix(wl).transpose())
                #                 / vector_sqrt).sum() / (na_a / 2)
                diff_corr_adj = (array(matrix(anb) * matrix(wl))
                                 / vector_sqrt).sum() / (na_a / 2)
                diff_cov_adj = diff_corr_adj * na_a / (a_a / geo_mean).sum()
            else:
                #diff_corr_adj = (array(matrix(anb) * matrix(wl).transpose())
                #                 / vector_sqrt).sum() / (na_margin2 / 2)
                diff_corr_adj = (array(matrix(anb) * matrix(wl))
                                 / vector_sqrt).sum() / (na_margin2 / 2)
                diff_cov_adj = diff_corr_adj * na_margin2 / (a_margin2
                                                             / geo_mean).sum()
            wl = wl - diff_cov_adj
            # 2 level mean covariances
            if margin_angle > adj_angle:
                cov_adj2 = ((corr_adj * na_adj - cov_dist
                            * (1. / geo_mean[a_adj > 0]).sum(0))
                            / (a_a / geo_mean).sum())
            else:
                cov_adj2 = ((corr_adj * na_adj - cov_dist
                            * (1. / geo_mean[a_adj > 0]).sum(0))
                            / (a_margin2 / geo_mean).sum())
            al = cov_adj2 + a_param * (wl-cov_adj2)
            # Compute rates for independent Poisson variables
            ma = matrix(a[:, n:2*n])
            #l[:n] = mu - diag(array(ma * matrix(diag(al)).transpose()
            #                        * ma.transpose())) - cov_dist
            l[:n] = (mu - diag(array(ma * matrix(diag(al.flatten()))
                     * ma.transpose())) - cov_dist)
            l[n:2*n] = al.flatten()
            if not corr_dist == 0:
                l[n_l] = cov_dist
    # Output sanity check
    if (l < 0).any():
        raise ArithmeticError, 'Cannot generate covariances, neagative '      \
                               'covariance'
    return l, a
