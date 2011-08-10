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
Ising model
"""

import sys
import math
import copy
from numpy  import (abs, array, diag, empty, exp, eye, logical_and, logical_or,
                    matrix, ones, sqrt, tile, zeros)
from scipy.optimize import fmin
from mpl_toolkits.axes_grid import make_axes_locatable

import spikecountmodels.config as config
from spikecountmodels.tools.matrix   import *
from spikecountmodels.tools.stats    import *
from spikecountmodels.marginal       import *
from spikecountmodels.copula         import *
from spikecountmodels.model          import *


class IsingModel(SpikeCountModel):
    """
    Ising model
    """
    def __init__(self, field_strength, coupling, dimension = None):
        """
        Initialize
        
        @type  field_strength: 1-d array
        @param field_strength: Field strenght vector h
        @type  coupling: 2-d array
        @param coupling: Coupling matrix J
        @type  dimension: Integer
        @param dimension: Model dimension
        """
        coupling = array(matrix(coupling))
        if dimension == None:
            self.dimension = len(field_strength)
        else:
            self.dimension = dimension
        if not (coupling.shape[0] == coupling.shape[1]
                and (diag(coupling) == 0).all()
                and (coupling == coupling.transpose()).all()):
            raise ValueError, 'coupling must be a symmetric matrix with zero '\
                              'diagonal'
        if not coupling.shape[0] == self.dimension:
            raise ValueError, 'coupling must be a quadratic matrix of size '  \
                              '"dimension"'
        if not len(field_strength) == self.dimension:
            raise ValueError, 'field_strength must have length "dimension"'
        self.field_strength = field_strength
        self.coupling = coupling
        
    def pdf(self, eval_points):
        """
        Calculates the probability density for samples I{eval_points} of the
        copula based model.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        eval_points = array(matrix(eval_points))
        if not logical_or(eval_points == 1, eval_points == 0).all():
            raise ValueError, 'eval_points must be a binary matrix'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        # Calculate
        bcomb = binary_combinations(d)
        # Normalization factor
        fsm = matrix(self.field_strength).transpose()
        bj = array(matrix(bcomb) * matrix(self.coupling))
        bh = array(matrix(bcomb) * fsm).flatten()
        z = (exp(bh + (bj * bcomb).sum(1) / 2.)).sum()
        # Exact calculation
        xh = array(matrix(eval_points) * fsm).flatten()
        xj = array(matrix(eval_points) * matrix(self.coupling).transpose())
        return exp(xh + (xj * eval_points).sum(1) / 2) / z

    def count_pdf(self, eval_points, max_dimension = 10, max_samples = 1000):
        """
        Counts the probability density for samples I{eval_points} of the
        copula based model.
        
        @type  eval_points: 2-d array or list
        @param eval_points: array of points at which the CDF is evaluated,
                            where each row contains a d-dimensional vector
                            corresponding to one data point.
        @rtype:  1-d array
        @return: Vector of probability densities for each row of I{eval_points}
        """
        eval_points = array(matrix(eval_points))
        if not logical_or(eval_points == 1, eval_points == 0).all():
            raise ValueError, 'eval_points must be a binary matrix'
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        # Calculate
        bcomb = binary_combinations(d)
        # Normalization factor
        fsm = matrix(self.field_strength).transpose()
        bj = array(matrix(bcomb) * matrix(self.coupling))
        bh = array(matrix(bcomb) * fsm).flatten()
        z = (exp(bh + (bj * bcomb).sum(1) / 2.)).sum()
        # Binary combinations w.r.t. max_dimension
        bcombt = binary_combinations(max_dimension)
        sbcombt = bcombt.sum(1)
        el = []
        p = zeros(eval_points.shape[0])
        for k in range(eval_points.shape[0]):
            for i in range(d):
                el.append(bcombt[sbcombt == eval_points[k, i], :])
            s = 0
            y = zeros((d, max_dimension))
            # Indices for el
            l = zeros(d, dtype = 'int')
            # For all feasible combinations of l
            lcontinue = True
            loopcount = 0
            while lcontinue and loopcount < config.WHILE_LOOP_ABORT:
                loopcount = loopcount + 1
                if loopcount == config.WHILE_LOOP_ABORT:
                    raise OverflowError, 'While loop took to long'
                for i in range(d):
                    if (array(el[i].shape) == 0).any():
                        # TODO: hack: check this
                        y[i, :] = 0
                    else:
                        y[i, :] = el[i][l[i], :]
                s2 = zeros(max_dimension)
                for t in range(max_dimension):
                    yj = array(matrix(y[:, t])
                                         * matrix(self.coupling)).flatten()
                    s2[t] = s2[t] + (yj * y[:, t]).sum() / 2.
                s = s + exp(s2.sum())
                # Loop increment
                l[0] = l[0] + 1
                li = 0
                while lcontinue and l[li] >= el[li].shape[0]:
                    l[li] = 0
                    li = li + 1
                    if li >= d:
                        lcontinue = False
                    else:
                        l[li] = l[li] + 1
            xh = array(matrix(eval_points[k, :])
                       * matrix(self.field_strength).transpose())
            p[k] = exp(xh) * s / z**max_dimension
        return p
        
    def estimate_parameters(self, m, r):
        """
        Estimate the model parameters and set the arguments of the current
        instance to the estimated parameters.
        
        @type  m: 2-d array
        @param m: ???
        @type  r: 2-d array
        @param r: ???
        @rtype:  Tuple
        @return: (h, J) with Field strenght vector h and coupling matrix J
        """
        m = array(matrix(m))
        d = array(m.shape).max()
        m = m.flatten()
        y = zeros(d + (d * (d - 1)) / 2)
        objfun = lambda x: _ising_model_validation(x, m, r)
        y = fmin(objfun, y)
        h = y[:d]
        j = _vector_to_matrix(y[d + 1:], d)
        # Apply Boltzmann learning (Roudi et al. 2009)
        eta = 1e-3
        precision = 1e-3
        maxdiff = precision
        while maxdiff >= precision:
            e_m, e_r = ising_model_moments(h, j)
            h = h + eta * (m - e_m)
            j = j + eta * (r - e_r)
            maxdiff2 = (abs(m - e_m)).max() + (r - e_r).max()
            if maxdiff2 - maxdiff < maxdiff / sqrt(2):
                eta = eta * 1.001
            elif maxdiff2 - maxdiff > 0:
                eta = eta / 1.001
            maxdiff = maxdiff2
        return h, j


def _ising_model_validation(x, m, r):
    """Helper function"""
    d = len(m)
    h = x[:d]
    j = _vector_to_matrix(x[d + 1:], d)
    [e_m, e_r] = ising_model_moments(h, j)
    return ((e_m - m)**2).sum() + ((e_r - r)**2).sum()

def _vector_to_matrix(v, d):
    """Helper function"""
    m = zeros((d, d))
    k = 1
    for i in range(d - 1):
        for j in range(i):
            m[i+1, j] = v[k]
            m[j, i+1] = v[k]
            k = k + 1
    return m

def ising_model_moments(h, j):
    """
    Calculate moments for Ising model
    """
    d = len(h)
    bcomb = binary_combinations(d)
    # Compute expectation
    m = IsingModel(h, j, d)
    p = m.pdf(bcomb)
    e_m = (tile(p, (d, 1)).transpose() * bcomb).sum(0)
    p_p = zeros(4)
    b4  = binary_combinations(2)
    e_r = zeros((d, d))
    for i in range(d):
        for j in range(i+1):
            for k in range(4):
                p_p[k] = p[logical_and(bcomb[:, i] == b4[k, 0],
                                       bcomb[:, j] == b4[k, 1])].sum()
            e_r[i, j] = (p_p * (b4[:, 0] - e_m[i]) * (b4[:, 1] - e_m[j])).sum()
    e_r = e_r / sqrt(array(matrix(e_r.diagonal()).transpose()
                           * matrix(e_r.diagonal())))
    e_r = e_r + e_r.transpose()
    e_r = e_r - diag(diag(e_r)) + eye(d)
    return e_m, e_r