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
Chi-square tests and base class for tests
"""

import os
from numpy  import  argsort, array, atleast_2d, logical_not, zeros
from scipy.optimize import fmin_slsqp, fsolve
from scipy.stats    import kendalltau, chi2
from math import sqrt, ceil

import spikecountmodels.config as config
import spikecountmodels.tools.files as filetools
from spikecountmodels.tools.matrix   import field
from spikecountmodels.marginal       import *
from spikecountmodels.copula         import *
from spikecountmodels.model          import *
from spikecountmodels.copulamodel    import *
from spikecountmodels.isingmodel     import *
from spikecountmodels.comppoissmodel   import *


class ChiSquareTest:
    """
    Main class for Chi-square tests and other statistical tests
    """
    def test(self, data_x, data_y, alpha = 0.05, *moreargs):
        """
        The test function, takes two data sets and usually returns a tuple
        (h, p) where h is True or False depending on whether the hypothesis
        is true or false, i.e. p < alpha, and p is the calculated
        probability.
        In this main class, the function only raises a NotImplementedError.
        
        @type  data_x: 1d-array or list
        @param data_x: Data set
        @type  data_y: 1d-array or list
        @param data_y: Data set
        """
        raise NotImplementedError, '%s TEST not implemented' % self.__class__
    
    def control_false_discovery_rate(self, p, alpha = .05,
                                     assumption = 'general'):
        """
        Controls the False Discovery Rate (FDR) using the Benjamini-Hochberg
        controlling procedure (Benjamini and Hochberg 1995, Benjamini and
        Yekutieli 2001).
        
        @type  p: 1-d array or list
        @param p: Probability values of the hypotheses
        @type  alpha: Scalar
        @param alpha: Significance level of the FDR
        @type  assumption: String
        @param assumption: One of I{general} and I{noneg}. If I{noneg} is
                           selected then a less conservative version of the
                           procedure is selected and it is assumed that there
                           is no negative dependence between the test
                           statistics.
        @rtype:  1-d array
        @return: Vector of boolean rejections (1 or 0) of the hypotheses
        """
        p = array(p).flatten()
        if (p < 0).any() or (p > 1).any():
            raise ValueError, 'p must be a vector of p-values'
        if assumption.lower() == 'general':
            alpha = alpha / array(range(1, len(p) + 1)).sum()
        elif not assumption.lower() == 'noneg':
            raise ValueError, 'assumption must be one of "general" and "noneg"'
        # Correct number of rejections
        m = len(p)
        order = argsort(p)
        p_sort = p[order]
        k = (p_sort <= array(range(1, m + 1)).transpose() / float(m)
             * alpha).nonzero()[0]
        h = zeros(p.shape, 'int')
        if len(k) > 0:
            h[order[:k+1]] = 1
        return h


class ChiSquareFrankTest(ChiSquareTest):
    """
    Chi-square test with a Frank Copula based model with discrete empirical
    marginals.
    """
    def test(self, data_x, data_y, alpha):
        """
        Perform test.
        
        @type  data_x: 1-d array or list
        @param data_x: First data array
        @type  data_y: 1-d array or list
        @param data_y: Second data array (same length as I{data_x})
        @type  alpha: Scalar
        @param alpha: Significance level
        @rtype:  Tuple
        @return: (h, p) where p is the probability for the hypothesis and h
                 is True if p < alpha
        """
        if not ((type(alpha) == type(1) or type(alpha) == type(.1)) and
                (0 <= alpha <= 1)):
            raise ValueError, 'alpha must be a scalar between 0 and 1'
        x = array(data_x).flatten()
        y = array(data_y).flatten()
        if not len(x) == len(y):
            raise ValueError, 'Data arrays have to be of same length'
        
        # Generate contingency table
        cont = zeros((max(x)+1, max(y)+1))
        for i in range(len(x)):
            cont[x[i], y[i]] = cont[x[i], y[i]] + 1
        margin = DiscreteEmpiricalMarginal()
        margin.fit(array([x, y]).transpose())
        # Parametrized margin:
        tau, p = kendalltau(x, y)
        copula = FrankCopula()
        copula.alpha = copula.param_kendall(tau)
        # Expected counts
        x2, y2 = meshgrid(range(cont.shape[0]), range(cont.shape[1]))
        x2 = atleast_2d(x2.transpose().flatten())
        y2 = atleast_2d(y2.transpose().flatten())
        ep = concatenate((x2, y2)).transpose()
        dm = CopulaBasedModel(copula, margin)
        econt = dm.pdf(ep).reshape(cont.shape)*len(x)
        # Apply ordered expected frequencies procedure (see Loukas 1986)
        ordering = argsort(-econt.flatten())
        econt_array = econt.flatten()[ordering]
        cont_array = cont.flatten()[ordering]
        # Group according to minimum expected frequency (MEF)
        mef = 1
        econt_group = zeros(len(econt_array))
        cont_group = zeros(len(econt_array))
        ig = 0
        for i in range(len(econt_array)):
            econt_group[ig] = econt_group[ig] + econt_array[i]
            cont_group[ig] = cont_group[ig] + cont_array[i]
            if econt_group[ig] >= mef and i < len(econt_array) - 1:
                ig = ig + 1
        econt_group = econt_group[:ig + 1]
        cont_group = cont_group[:ig + 1]
        k = logical_not(econt_group == 0)
        test_stat = (((cont_group[k]-econt_group[k])**2)/econt_group[k]).sum()
        # DOF, -1 for copula parameter
        df = (cont.shape[0] - 1) * (cont.shape[1] - 1) - 1
        if df > 0:
            p = 1 - chi2.cdf(test_stat, df)
        else:
            p = 1
        h = p < alpha
        return h, p


class ChiSquareIndependenceTest(ChiSquareTest):
    """
    ???
    """
    def test(self, data_x, data_y, alpha):
        """
        Perform test.
        
        @type  data_x: 1-d array or list
        @param data_x: First data array
        @type  data_y: 1-d array or list
        @param data_y: Second data array (same length as I{data_x})
        @type  alpha: Scalar
        @param alpha: Significance level
        @rtype:  Tuple
        @return: (h, p) where p is the probability for the hypothesis and h
                 is True if p < alpha
        """
        if not ((type(alpha) == type(1) or type(alpha) == type(.1)) and
                (0 <= alpha <= 1)):
            raise ValueError, 'alpha must be a scalar between 0 and 1'
        x = array(data_x).flatten()
        y = array(data_y).flatten()
        if not len(x) == len(y):
            raise ValueError, 'Data arrays have to be of same length'
        
        n = len(x)
        # Generate contingency table
        cont = zeros((max(x)+1, max(y)+1))
        for i in range(len(x)):
            cont[x[i], y[i]] = cont[x[i], y[i]] + 1
        # Expected counts
        econt = zeros(cont.shape)
        for i in range(cont.shape[0]):
            for j in range(cont.shape[1]):
                econt[i, j] = cont[i, :].sum() * cont[:, j].sum() / n
        # Apply ordered expected frequencies procedure (see Loukas 1986)
        ordering = argsort(-econt.flatten())
        econt_array = econt.flatten()[ordering]
        cont_array = cont.flatten()[ordering]
        # Group according to minimum expected frequency (MEF)
        mef = 1
        econt_group = zeros(len(econt_array))
        cont_group = econt_group
        ig = 0
        for i in range(len(econt_array)):
            econt_group[ig] = econt_group[ig] + econt_array[i]
            cont_group[ig] = cont_group[ig] + cont_array[i]
            if econt_group[ig] >= mef and i < len(econt_array) - 1:
                ig = ig + 1
        econt_group = econt_group[:ig + 1]
        cont_group = cont_group[:ig + 1]
        k = logical_not(econt_group == 0)
        test_stat = (((cont_group[k]-econt_group[k])**2)/econt_group[k]).sum()
        # DOF, -1 for copula parameter
        df = (cont.shape[0] - 1) * (cont.shape[1] - 1) - 1
        if df > 0:
            p = 1 - chi2.cdf(test_stat, df)
        else:
            p = 1
        h = p < alpha
        return h, p


class ChiSquareNormalTest(ChiSquareTest):
    """
    Chi-square test with a Gaussian Copula based model with discrete empirical
    marginals.
    """
    def test(self, data_x, data_y, alpha):
        """
        Perform test.
        
        @type  data_x: 1-d array or list
        @param data_x: First data array
        @type  data_y: 1-d array or list
        @param data_y: Second data array (same length as I{data_x})
        @type  alpha: Scalar
        @param alpha: Significance level
        @rtype:  Tuple
        @return: (h, p) where p is the probability for the hypothesis and h
                 is True if p < alpha
        """
        if not ((type(alpha) == type(1) or type(alpha) == type(.1)) and
                (0 <= alpha <= 1)):
            raise ValueError, 'alpha must be a scalar between 0 and 1'
        x = array(data_x).flatten()
        y = array(data_y).flatten()
        if not len(x) == len(y):
            raise ValueError, 'Data arrays have to be of same length'
        
        # Generate contingency table
        cont = zeros((max(x)+1, max(y)+1))
        for i in range(len(x)):
            cont[x[i], y[i]] = cont[x[i], y[i]] + 1
        margin = DiscreteEmpiricalMarginal()
        margin.fit(array([x, y]).transpose())
        # Parametrized margin:
        copula = GaussianCopula()
        dm = CopulaBasedModel(copula, margin)
        f = lambda rho: -(log(dm.pdf(array([x, y]).transpose(), rho))).sum()
        rho = fmin_slsqp(f, 0, bounds = [(-1, 1)])
        dm.set_copula_parameter(rho)
        # Expected counts
        x2, y2 = meshgrid(range(cont.shape[0]), range(cont.shape[1]))
        x2 = x2.flatten()
        y2 = y2.flatten()
        econt = dm.pdf(array([x2, y2]).transpose()).reshape(cont.shape)*len(x)
        # Apply ordered expected frequencies procedure (see Loukas 1986)
        ordering = argsort(-econt.flatten())
        econt_array = econt.flatten()[ordering]
        cont_array = cont.flatten()[ordering]
        # Group according to minimum expected frequency (MEF)
        mef = 1
        econt_group = zeros(len(econt_array))
        cont_group = econt_group
        ig = 0
        for i in range(len(econt_array)):
            econt_group[ig] = econt_group[ig] + econt_array[i]
            cont_group[ig] = cont_group[ig] + cont_array[i]
            if econt_group[ig] >= mef and i < len(econt_array) - 1:
                ig = ig + 1
        econt_group = econt_group[:ig + 1]
        cont_group = cont_group[:ig + 1]
        k = logical_not(econt_group == 0)
        test_stat = (((cont_group[k]-econt_group[k])**2)/econt_group[k]).sum()
        # DOF, -1 for copula parameter
        df = (cont.shape[0] - 1) * (cont.shape[1] - 1) - 1
        if df > 0:
            p = 1 - chi2.cdf(test_stat, df)
        else:
            p = 1
        h = p < alpha
        return h, p
