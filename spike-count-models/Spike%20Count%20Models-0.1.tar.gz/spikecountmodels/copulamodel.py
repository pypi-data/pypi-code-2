# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2010 Bernstein Center for Computational Neuroscience Berlin   #
# author: André Großardt, based on Matlab code from Arno Onken                #
# contributor(s): Mahmoud Mabrouk                                             #
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
Copula based models
"""

import sys
import math
import copy
from numpy  import (abs, array, atleast_2d, concatenate, isnan, log2,
                    matrix, meshgrid, ones, sqrt, tile, zeros)
from scipy          import iscomplex
from scipy.optimize import fmin_slsqp, fmin_cobyla, fmin_tnc, fmin_l_bfgs_b
from scipy.stats    import norm
import numpy as np
import spikecountmodels.config as config
from spikecountmodels.tools.matrix   import *
from spikecountmodels.tools.stats    import *
from spikecountmodels.marginal       import *
from spikecountmodels.copula         import *
from spikecountmodels.model          import *
from spikecountmodels.tools          import float_info


class CopulaBasedModel(SpikeCountModel):
    
    OPTIMIZATION_FUNC = 0 #1: fmin_slsqp, 1:fmin_cobyla, 2:fmin_tnc,  3:fmin_l_bfgs_b 
    """
    Copula based model
    """
    def __init__(self, copula, marginals, optim_func = 0):
        """
        Initialize
        
        @type  copula: Copula
        @param copula: Copula of the model
        @type  marginals: List of Marginal
        @param marginals: List of marginals
        @type optim_func: integer
        @param optim_func: The optimization function to be used in copula fitting, fmin_slsqp per default
        """
        self.copula    = copula
        self.dimension = copula.dimension
        self.OPTIMIZATION_FUNC = optim_func
        # If only one marginal is specified use this for each dimension
        if not(isinstance(marginals, list)):
            self.marginals = []
            for i in range(self.dimension):
                self.marginals.append(copy.deepcopy(marginals))
        elif not copula.dimension == len(marginals):
            raise ValueError, 'The number of marginals must equal the number '\
                              'of dimensions'
        else:
            self.marginals = marginals
            # Assert that all marginals are discrete or all are continuous
            b = self.has_discrete_marginals()
            for m in self.marginals:
                if not m.is_discrete() == b:
                    raise ValueError, 'Mixing of discrete and continuous '    \
                                      'marginals is not allowed'
    
    def cdf(self, eval_points):
        """
        Calculates the cumulative distribution function for samples
        I{eval_points} of the copula based model. The model can have discrete
        or continuous marginals.
        This function has exponential complexity for the number of elements.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        eval_points = atleast_2d(eval_points)
        p = zeros(eval_points.shape)
        # Calculate Marginal PDFs
        for i in range(self.dimension):
            p[:, i] = self.marginals[i].cdf(eval_points[:, i])
        # Calculate Copula PDF
        return self.copula.cdf(p)
    
    def pdf(self, eval_points, _alpha = None):
        """
        Calculates the probability density for samples I{eval_points} of the
        copula based model. The model can have discrete or continuous
        marginals.
        This function has exponential complexity for the number of elements.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        eval_points = atleast_2d(eval_points)
        # If a copula parameter is specified, use a new copula instead of
        # self.copula. This is ONLY needed for function calls for minimization
        # w.r.t. the copula parameter. Otherwise you should NOT use the
        # _alpha argument
        if _alpha == None:
            copula = self.copula
        else:
            copula = copy.deepcopy(self.copula)
            copula.alpha = _alpha
        trials, n = eval_points.shape
        p = zeros(trials)
        # Case 1: Discrete marginals
        if self.has_discrete_marginals():
            bcomb = binary_combinations(n)
            for i in range(trials):
                x = eval_points[i, :]
                # Apply the inclusion-exclusion principle
                # But only to the subset of elements != 0
                nz = x.nonzero()[0]
                nnz = len(nz)
                if nnz > 0:
                    signs = -ones(2**nnz)
                    signs[bcomb[:2**nnz, n-nnz:n].sum(1) % 2 == 0] = 1
                    x_sub = zeros((2**nnz, n))
                    x_sub[:, nz] = bcomb[:2**nnz, n-nnz:n]
                    mdata = tile(x, (2**nnz, 1)) - x_sub
                    csample = zeros((2**nnz, n))
                    for j in range(n):
                        csample[:, j] = self.marginals[j].cdf(mdata[:, j])
                    subpart = copula.cdf(csample)
                    s = (signs * subpart).sum()
                else:
                    x = atleast_2d(x)
                    csample = zeros(x.shape)
                    for j in range(n):
                        csample[:, j] = self.marginals[j].cdf(x[:, j])
                    s = copula.cdf(csample)
                # Probability must be in (0, 1)
                if s <= 0:
                    p[i] = float_info.epsilon
                elif s >= 1:
                    p[i] = 1 - float_info.epsilon
                else:
                    p[i] = s
            return p
        # Case 2: Continuous marginals
        else:
            # Margin cdf and pdf:
            mpdf = zeros((trials, n))
            cpdf = zeros((trials, n))
            for i in range(n):
                cpdf[:, i] = self.marginals[i].cdf(eval_points[:, i])
                mpdf[:, i] = self.marginals[i].pdf(eval_points[:, i])
            mpdf[np.isnan(mpdf)]=0.00000001
            cpdf[np.isnan(cpdf)]=0.00000001
            if isinstance(self.copula, IndependenceCopula):
                return mpdf.prod(1)
            else:
                return self.copula.gradient(cpdf)*mpdf.prod(1)
        
    
    def gradient(self, eval_points):
        """
        Gradient of the copula based model.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  2-d array
        @return: Gradient
        """
        eval_points = atleast_2d(eval_points)
        trials, n = eval_points.shape
        bcomb = binary_combinations(n)
        if isscalar(self.get_copula_parameter()):
            l = 1
        else:
            l = len(self.get_copula_parameter())
        g = zeros((trials, l))
        # Data for marginals
        for i in range(trials):
            x = eval_points[i, :]
            # Apply the inclusion-exclusion principle
            # But only to the subset of elements != 0
            nz = x.nonzero()[0]
            nnz = len(nz)
            if nnz > 0:
                signs = -ones(2**nnz)
                signs[bcomb[:2**nnz, n-nnz:n].sum(1) % 2 == 0] = 1
                x_sub = zeros((2**nnz, n))
                x_sub[:, nz] = bcomb[:2**nnz, n-nnz:n]
                mdata = tile(x, (2**nnz, 1)) - x_sub
                csample = zeros((2**nnz, n))
                for j in range(n):
                    csample[:, j] = self.marginals[j].cdf(mdata[:, j])
                subpart = self.copula.gradient(csample)
                if len(subpart.shape) == 1:
                    subpart = atleast_2d(subpart).transpose()
                g[i, :] = (tile(signs, (l, 1)).transpose() * subpart).sum(0)
            else:
                x = atleast_2d(x)
                csample = zeros(x.shape)
                for j in range(n):
                    csample[:, j] = self.marginals[j].cdf(x[:, j])
                g[i, :] = self.copula.gradient(csample)
        return g.transpose()
    
    def fit(self, data, data_validation = [], reg_init = 0, marginals = False):
        """
        Inference-for-margins estimator for a copula based distribution.
        Return the fitted parameters AND sets the copula parameters to the
        fitted values.
        
        @type  data: 2-d array or list
        @param data: Observations to be fitted (ntrials-by-dimension)
        @type  data_validation: 1-d array
        @param data_validation: Data validation set for regularization
        @type  reg_init: Scalar
        @param reg_init: Initial regularization parameter
        @type  marginals: Boolean
        @param marginals: If True marginals are also fitted
        @rtype:  Tuple
        @return: (alpha, reg) where alpha is the fitted copula parameter and
                 reg is the regularization parameter
        """
        data_validation = atleast_2d(data_validation)
        data = atleast_2d(data)
        ntrials, d = data.shape
        maxpar = self.copula.number_of_parameters()
        npar = self.copula.real_number_of_parameters()
        # Fit marginals
        if marginals:
            for i in range(d):
                self.marginals[i].fit(data[:, i])
        # Optimize copula parameters
        if len(data_validation.flatten()) == 0:
            # Regularization parameter
            alpha = reg_init
            if isinstance(self.copula, IndependenceCopula):
                self.copula.alpha = []
                return [], alpha
            elif isinstance(self.copula, CopulaMixture):
                rho, z = self._expectation_maximization(data)
                self.copula.set_weights(z)
            else:
                rho = self._cfit(data, alpha)
        else:
            cfit_regularization = lambda alpha_par: self._cfit_valfun(
                                  data_validation, self._cfit(data, alpha_par))
            alpha_start = 0
            # Initial alpha_end as log likelihood difference between
            # unregularized and independent
            copula_backup = self.copula
            self.copula = IndependenceCopula(data_validation.shape[1])
            ind_pdf = self.pdf(data_validation)
            self.copula = copula_backup
            alpha_end = abs(cfit_regularization(0) + (log(ind_pdf)).sum())
            alpha = gridsearch(cfit_regularization, alpha_start, alpha_end)
            rho = self._cfit(data, alpha)
        if maxpar > npar:
            rho = concatenate((rho, zeros(maxpar - npar)))
        self.set_copula_parameter(rho, autocorrect = True)
        return rho, alpha

    def _cfit(self, data, alpha):
        """Helper function"""
        tol = 1e-3
        copula_neg_log = (lambda rho: self._cfit_valfun(data, rho, alpha))
        c = self.copula.constraints()
        if config.DEBUG:
            iprint = 2
        else:
            iprint = -1
        rho = self.get_copula_parameter()
        try:
            if self.OPTIMIZATION_FUNC == 0:
                rho = fmin_slsqp(copula_neg_log, rho, epsilon = .1, acc = tol,
                        bounds = c.bounds(self.copula.real_number_of_parameters()),
                        eqcons = c.eqcons(), iprint = iprint)
            if self.OPTIMIZATION_FUNC == 1:
                rho = fmin_cobyla(copula_neg_log, 
                        x0 = np.asfarray(rho).flatten(), 
                        cons = c.cobyla_constraints(), 
                        rhobeg=2, 
                        rhoend=0.0001,
                        iprint = 1)
                rho = rho[0]
            if self.OPTIMIZATION_FUNC == 2:
                rho = fmin_tnc(copula_neg_log,
                        x0 = np.asfarray(rho).flatten(),
                        fprime = None,                        
                        approx_grad = True,
                        #bounds = c.bounds(self.copula.real_number_of_parameters()), #bounds don't work for this
                        epsilon = .01,
                        disp = 0,
                        stepmx = 0.3)   
                rho = rho[0][0]           
            if self.OPTIMIZATION_FUNC == 3:  
                rho = fmin_l_bfgs_b(copula_neg_log, x0 = np.asfarray(rho).flatten(), bounds = c.bounds(self.copula.real_number_of_parameters()),
                        epsilon = .1, iprint = iprint, approx_grad = True)
                rho = rho[0]
            if iscomplex(rho).any():
                rho = self.get_copula_parameter()
        except Exception, exception:
            if config.DEBUG:
                print 'Run of fmin_slsqp in model, %s raised:' % self.__class__
                print exception
        finally:
            return rho
    
    def _cfit_valfun(self, data, rho, alpha = 0, full_output = False):
        """Helper function"""
        maxpar = self.copula.number_of_parameters()
        npar = self.copula.real_number_of_parameters()
        if isscalar(rho):
            rho = array([rho])
        else:
            rho = array(rho)
        if maxpar > npar:
            rho_full = concatenate((rho, zeros(maxpar - npar)))
        else:
            rho_full = rho
        self.set_copula_parameter(rho_full, True)
        try:
            likelihood = self.pdf(data)
            res = -(log(likelihood)).sum() + alpha * (rho**2).sum() / 2
            if isnan(res):
                res = sys.maxint
            if full_output:
                g = -(self.gradient(data)[:npar, :]
                      / tile(likelihood, (npar, 1))).sum(1) + alpha * rho
        except Exception, exception:
            if config.DEBUG:
                print 'Run of fmin_slsqp in model, %s raised:' % self.__class__
                print exception
            res = sys.maxint
            if full_output:
                g = zeros(size(rho))
        finally:
            if full_output:
                return res, g
            else:
                return res
        
    def _expectation_maximization(self, data):
        """Helper function"""
        ntrials = data.shape[0]
        rho = self.get_copula_parameter()
        if isscalar(rho):
            rho = array([rho])
        else:
            rho = array(rho)
        rho_old = rho - 1
        z_old = zeros(len(rho))
        z = ones(len(rho)) / len(rho)
        cm = zeros((len(rho), ntrials))
        tol = 1e-3
        if config.DEBUG:
            iprint = 2
        else:
            iprint = -1
        while abs(z - z_old).mean() > tol or abs(rho - rho_old).mean() > tol:
            # EM-algorithm, E-step
            for f in range(len(rho)):
                component = zeros(len(rho))
                component[f] = 1
                self.set_copula_parameter(component * rho)
                self.copula.set_weights(component)
                cm[f, :] = self.pdf(data)
            z_old[:] = z
            for f in range(len(rho)):
                z[f] = (z_old[f] * cm[f, :] / (tile(z_old,
                                 (ntrials, 1)).transpose() * cm).sum(0)).mean()
            # M-step:
            rho_old[:] = rho
            copula_neg_log = (lambda rho:
                           self._expectation_maximization_valfun(data, rho, z))
            c = self.copula.constraints()
            if self.OPTIMIZATION_FUNC == 0:
                rho = fmin_slsqp(copula_neg_log, rho, acc = tol, epsilon = .1,
                                 bounds = c.bounds(len(rho)), eqcons = c.eqcons(),
                                 iprint = iprint)
            if self.OPTIMIZATION_FUNC == 1:
                rho = fmin_cobyla(copula_neg_log, 
                        x0 = np.asfarray(rho).flatten(), 
                        cons = c.cobyla_constraints(), 
                        rhobeg=2, 
                        rhoend=0.0001,
                        iprint = 1)
                rho = rho[0]
            if self.OPTIMIZATION_FUNC == 2:
                rho = fmin_tnc(copula_neg_log,
                        x0 = np.asfarray(rho).flatten(),
                        fprime = None,                        
                        approx_grad = True,
                        #bounds = c.bounds(self.copula.real_number_of_parameters()), #bounds don't work for this
                        epsilon = .01,
                        disp = 0,
                        stepmx = 0.3)   
                rho = rho[0][0]           
            if self.OPTIMIZATION_FUNC == 3:
                rho = fmin_l_bfgs_b(copula_neg_log, x0 = np.asfarray(rho).flatten(), bounds = c.bounds(self.copula.real_number_of_parameters()),
                        epsilon = .1, iprint = iprint, approx_grad = True)
                rho = rho[0]
            # Check bounds
            if isscalar(rho):
                if rho < c.lb(1):
                    rho = c.lb(1)
                elif rho > c.ub(1):
                    rho = c.ub(1)
            else:
                lb = array(c.lb(len(rho)))
                ub = array(c.ub(len(rho)))
                rho[rho < lb] = lb[rho < lb]
                rho[rho > ub] = ub[rho < ub]
        return rho, z
    
    def _expectation_maximization_valfun(self, data, rho, z):
        """Helper function"""
        self.set_copula_parameter(rho)
        self.copula.set_weights(z)
        try:
            likelihood = self.pdf(data)
            res = -(log(likelihood)).sum()
        except Exception, exception:
            if config.DEBUG:
                print 'Run of em valfun in model, %s raised:' % self.__class__
                print exception
            res = sys.maxint
        finally:
            return res
            
    def correlation(self, limits):
        """
        Calculates Pearson's correlation coefficient of a copula-based
        distribution with discrete marginals.
        
        @type  limits: 2-d array
        @param limits: Maximum of variables x and y: [max(x) max(y)]
        @rtype:  Scalar
        @return: Correlation coefficient
        """
        if not self.dimension == 2:
            raise NotImplementedError, 'correlation is only implemented for ' \
                                       'two dimensional copulas'
        x = range(limits[0]+1)
        y = range(limits[1]+1)
        xg, yg = meshgrid(x, y)
        shape = xg.shape
        xy = array([xg.flatten(), yg.flatten()]).transpose()
        # Generate probability matrix
        p = (self.pdf(xy)).reshape(shape).transpose()
        # Marginals
        p_x = p.sum(1)
        p_y = p.sum(0)
        # Expectations
        mu_x = (p_x * x).sum()
        mu_y = (p_y * y).sum()
        var_x = (p_x * x * x).sum() - mu_x * mu_x
        var_y = (p_y * y * y).sum() - mu_y * mu_y
        mu_xy = (p * xg.transpose() * yg.transpose()).sum()
        if not var_x * var_y == 0:
            return (mu_xy - mu_x * mu_y) / sqrt(var_x * var_y)
        else:
            return 0.
    
    def rand(self, cases = 1):
        """
        Generates samples from the copula based model.
        
        @type  cases: Integer
        @param cases: Number of samples to generate
        @rtype:  2-d array
        @return: cases-by-dimension array of samples
        """
        cr = self.copula.rand(cases)
        mr = zeros(cr.shape)
        for i in range(self.dimension):
            mr[:, i] = self.marginals[i].inverse(cr[:, i])
        return mr
    
    def estimate_entropy(self, err_eps = 1e-2, alpha = .01, samples = 10000):
        """
        Estimate entropy of the model.
        
        @type  err_eps: Scalar
        @param err_eps: Target standard error
        @type  alpha: Scalar
        @param alpha: Level ???
        @type  samples: Integer
        @param samples: Number of samples to calculate in each step
        @rtype:  Tuple
        @return: (Entropy, standard error)
        """
        # Confidence interval
        conf = norm.ppf(1 - alpha)
        std_err = float_info.max
        h = 0.
        varsum = 0.
        k = 0
        while std_err >= err_eps:
            # Generate samples
            x = self.rand(samples)
            # Compute probability of samples
            p = self.pdf(x)
            k = k + 1
            # Monte-Carlo estimate of entropy
            h = h + (-(log2(p)).sum() / samples - h) / k
            # Estimate standard error
            varsum = varsum + ((-log2(p) - h)**2).sum()
            std_err = conf * sqrt(varsum / (k * samples * (k * samples - 1)))
        return h, std_err
    
    def estimate_kl_divergence(self, copula_based_model_2, err_eps = 1e-3,
                               alpha = .01, samples = 10000):
        """
        Monte-Carlo estimation of the Kullback-Leibler divergence of two
        copula-based models of the same dimension.
        The first model is the current instance.
        
        @type  copula_based_model_2: CopulaBasedModel
        @param copula_based_model_2: Second model
        @type  err_eps: Scalar
        @param err_eps: Target standard error
        @type  alpha: Scalar
        @param alpha: Level ???
        @type  samples: Integer
        @param samples: Number of samples to calculate in each step
        @rtype:  Tuple
        @return: (KL divergence, standard error)
        """
        # Confidence interval for err_eps and level alpha
        # Normal approximation for large sample number
        conf = norm.ppf(1 - alpha)
        kl = 0
        std_err = float_info.max
        h = 0.
        varsum = 0.
        k = 0
        while std_err >= err_eps:
            k = k + 1
            # Generate samples
            x = self.rand(samples)
            # Compute probability of samples
            p1 = self.pdf(x)
            p2 = copula_based_model_2.pdf(x)
            # Monte-Carlo estimate of entropy
            h = h + (log2(p1 / p2)).sum()
            kl = h / (k * samples)
            # Estimate standard error
            varsum = varsum + ((log2(p1 / p2) - kl)**2).sum()
            std_err = conf * sqrt(varsum / (k * samples * (k * samples - 1)))
            if config.DEBUG:
                print 'Debug Info:'
                print 'current loop count: %s' % k
                print 'current std. error: %s' % std_err
        return kl, std_err
    
    def has_discrete_marginals(self):
        """
        Returns True if the marginals of the model are discrete
        """
        return self.marginals[0].is_discrete()
    
    def set_copula_parameter(self, alpha, autocorrect = False):
        """
        Set the copula parameter
        
        @param alpha: New copula parameter
        @type  autocorrect: Boolean
        @param autocorrect: If True the parameter is corrected instead of
                            raising an error if it is not in the right range.
        """
        self.copula.set_param(alpha, autocorrect)
    
    def get_copula_parameter(self):
        """
        Return the copula parameter
        """
        return self.copula.get_param()
    
    def set_marginal_parameter(self, marginal, mu):
        """
        Set the parameter of one of the marginals
        
        @type  marginal: Integer
        @param marginal: Number of the marginal to modify (starting with 0)
        @param mu: New marginal parameter
        """
        self.marginals[marginal].set_param(mu)
    
    def get_marginal_parameter(self, marginal):
        """
        Get the parameter of one of the marginals
        
        @type  marginal: Integer
        @param marginal: Number of the marginal (starting with 0)
        @return: Marginal parameter
        """
        return self.marginals[marginal].get_param()
    
    def str(self):
        """
        Return a string describing the copula.
        """
        str = 'Copula Based Model with\nCopula: %s\n' % self.copula.str()
        str = str + 'Marginals:'
        for m in self.marginals:
            str = str + '\n' + m.str()
        return str


def estimate_kl_divergence(copula_based_model_1, copula_based_model_2,
                           err_eps = 1e-3, alpha = .01, samples = 10000):
    """
    Monte-Carlo estimation of the Kullback-Leibler divergence of two
    copula-based models of the same dimension.
    
    @type  copula_based_model_1: CopulaBasedModel
    @param copula_based_model_1: First model
    @type  copula_based_model_2: CopulaBasedModel
    @param copula_based_model_2: Second model
    @type  err_eps: Scalar
    @param err_eps: Target standard error
    @type  alpha: Scalar
    @param alpha: Level ???
    @type  samples: Integer
    @param samples: Number of samples to calculate in each step
    @rtype:  Tuple
    @return: (KL divergence, standard error)
    """
    return copula_based_model_1.estimate_kl_divergence(copula_based_model_2,
                                                       err_eps, alpha, samples)

def estimate_mutual_information(models, prob_s, err_eps = .0005, alpha = .01,
                                samples = 1000):
    """
    Monte-Carlo estimation of the mutual information of a copula-based
    distribution with discrete margins.
    All models must have the same dimension.
    
    @type  models: List of CopulaBasedModel
    @param models: Models of same family with different marginals
    @type  prob_s: List
    @param prob_s: List of probability vectors
    @type  err_eps: Scalar
    @param err_eps: Target standard error
    @type  alpha: Scalar
    @param alpha: Level ???
    @type  samples: Integer
    @param samples: Number of samples to calculate in each step
    @rtype:  Tuple
    @return: (Mutual information, standard error)
    """
    # Confidence interval for err_eps and level alpha
    # Normal approximation for large sample number
    conf = norm.ppf(1 - alpha)
    mi = 0
    p = zeros((len(models), samples))
    std_err = float_info.max
    varsum = 0.
    k = 0
    while std_err >= err_eps:
        h = zeros(samples)
        k = k + 1
        for s in range(len(models)):
            # Generate samples
            x = models[s].rand(samples)
            for i in range(len(models)):
                p[i, :] = models[i].pdf(x)
            # Monte-Carlo estimate
            h = h + prob_s[s] * (log2(p[s, :]) - log2((tile(prob_s,
                                        (samples, 1)).transpose() * p).sum(0)))
        mi = mi + (h.mean() - mi) / k
        # Estimate standard error
        varsum = varsum + ((h - mi)**2).sum()
        std_err = conf * sqrt(varsum / (k * samples * (k * samples - 1)))
        if config.DEBUG:
            print 'Debug Info:'
            print 'current loop count: %s' % k
            print 'current std. error: %s' % std_err
    return mi, std_err

def estimate_posterior_kl_divergence(models1, models2, prob_s, err_eps = .0005,
                                     alpha = .01, samples = 10000):
    """
    Monte-Carlo estimation of the posterior Kullback-Leibler divergence of a
    copula-based distribution with discrete margins.
    All models in models1 and models2 must have the same dimension.
    
    @type  models1: List of CopulaBasedModel
    @param models1: Models of first family with different marginals
    @type  models2: List of CopulaBasedModel
    @param models2: Models of second family with same marginals as the
                    corresponding model in I{models1}
    @type  prob_s: List
    @param prob_s: List of probability vectors
    @type  err_eps: Scalar
    @param err_eps: Target standard error
    @type  alpha: Scalar
    @param alpha: Level ???
    @type  samples: Integer
    @param samples: Number of samples to calculate in each step
    @rtype:  Tuple
    @return: (KL divergence, standard error)
    """
    # Confidence interval for err_eps and level alpha
    # Normal approximation for large sample number
    conf = norm.ppf(1 - alpha)
    kl = 0
    p1 = zeros((len(models1), samples))
    p2 = zeros((len(models1), samples))
    p1_post = zeros((len(models1), samples))
    p2_post = zeros((len(models1), samples))
    std_err = float_info.max
    varsum = 0.
    k = 0
    while std_err >= err_eps:
        h = zeros(samples)
        k = k + 1
        for s in range(len(models1)):
            # Generate samples
            x = models1[s].rand(samples)
            for i in range(len(models1)):
                p1[i, :] = models1[i].pdf(x)
                p2[i, :] = models2[i].pdf(x)
            # Apply Bayes to compute posterior probabilities
            div1 = (p1 * tile(prob_s, (samples, 1)).transpose()).sum(0)
            div2 = (p2 * tile(prob_s, (samples, 1)).transpose()).sum(0)
            for i in range(len(models1)):
                p1_post[i, :] = p1[i, :] * prob_s[i] / div1
                p2_post[i, :] = p2[i, :] * prob_s[i] / div2
            # Monte-Carlo estimate
            h = h + prob_s[s] * (p1_post * log2(p1_post / p2_post)).sum(0)
        kl = kl + (h.mean() - kl) / k
        # Estimate standard error
        varsum = varsum + ((h - kl)**2).sum()
        std_err = conf * sqrt(varsum / (k * samples * (k * samples - 1)))
        if config.DEBUG:
            print 'Debug Info:'
            print 'current loop count: %s' % k
            print 'current std. error: %s' % std_err
    return kl, std_err
