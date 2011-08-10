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
Base class for spike count model
"""

import sys
import math
import copy
from numpy  import  array, atleast_2d, concatenate, ones, round

import spikecountmodels.config as config
from spikecountmodels.tools.matrix   import *
from spikecountmodels.tools.stats    import *
from spikecountmodels.marginal       import *
from spikecountmodels.copula         import *


class SpikeCountModel:
    """
    Main class for models
    """
    def cdf(self, eval_points):
        """
        Cumulative distribution function.
        Raises NotImplementedError for main class.
        """
        eval_points = atleast_2d(eval_points)
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        raise NotImplementedError, '%s CDF not implemented' % self.__class__
    
    def pdf(self, eval_points):
        """
        Probability density function.
        Raises NotImplementedError for main class.
        """
        eval_points = atleast_2d(eval_points)
        d = eval_points.shape[1]
        if not d == self.dimension:
            raise ValueError, 'Dimension of data does not fit model dimension'
        raise NotImplementedError, '%s PDF not implemented' % self.__class__
    
    def rand(self, n = 1):
        """
        Generate random samples for the model
        Raises NotImplementedError for main class.
        """
        raise NotImplementedError, '%s RAND not implemented' % self.__class__
    
    def fit(self, data):
        """
        Fit model parameters according to data.
        Raises NotImplementedError for main class.
        """
        raise NotImplementedError, '%s FIT not implemented' % self.__class__
    
    def plot(self, function, spike_range, options = {}):
        """
        Function to plot the CDF or PDF in the given range
        
        @type  function: Function
        @param function: Function to plot
        @type  spike_range: Tuple
        @param spike_range: Tuple [xmin, xmax, ymin, ymax] or [xmax, ymax]
        @type  options: Dictionary
        @param options: Option set for the plot:
                            - B{color}: True or False (default: False)
                            - B{plot_steps}: Density of the grid in 3d-plot
                            (Integer, default: 25)
                            - B{xlabel}: Label for the x-axis (String)
                            - B{ylabel}: Label for the y-axis (String)
                            - B{vmin}: Minimum value for color scale (if none
                            is specified use max(0, min(data)))
                            - B{vmax}: Maximum value for color scale (if none
                            is specified use min(10, max(data)))
        """
        # load matplotlib modules
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import pylab
        from mpl_toolkits.axes_grid import make_axes_locatable
        
        # Specify default options
        default = {}
        # coloring (colored or black/white)
        default['color']        = False
        # Axis labels
        default['xlabel']       = 'N1 (#spikes/bin)'
        default['ylabel']       = 'N2 (#spikes/bin)'
        # Min./Max. values for color scale, None = min/max data value
        default['vmin']         = None
        default['vmax']         = None
        # Set default options where nothing specified
        for key in default.keys():
            if not key in options:
                options[key] = default[key]
        if not self.dimension == 2:
            raise NotImplementedError, 'Plot works only for two-dimensional ' \
                                       'copulas'
        if not len(spike_range) == self.dimension:
            raise ValueError, 'spike_range must be either a list of d '       \
                              'numbers or a list of d tuples (lower, upper) ' \
                              'where d is the model dimension'
        for i in range(len(spike_range)):
            if isscalar(spike_range[i]):
                spike_range[i] = (0, spike_range[i])
        xmin = int(spike_range[0][0])
        xmax = int(spike_range[0][1]) + 1
        ymin = int(spike_range[1][0])
        ymax = int(spike_range[1][1]) + 1
        x, y = mgrid[xmin:xmax, ymin:ymax]
        mx = atleast_2d(x.flatten())
        my = atleast_2d(y.flatten())
        ep = concatenate((mx, my)).transpose()
        data = function(ep).reshape(x.shape).transpose()
        xmargin = self.marginals[0].pdf(range(xmin, xmax))
        ymargin = self.marginals[1].pdf(range(ymin, ymax))
        maxs = (xmargin.max(), ymargin.max())
        max_round = [xmargin.max(), ymargin.max()]
        for i in range(2):
            if max_round[i] > 0:
                max_round[i] = round(maxs[i])
                decimals = 0
                while max_round[i] == 0.:
                    decimals = decimals + 1
                    max_round[i] = round(maxs[i], decimals)
                if max_round[i] > maxs[i]:
                    max_round[i] = max_round[i] - .5 * .1**decimals
            else:
                max_round[i] = 0.1
        yleft = ymargin.max() - ymargin
        if options['color']:
            col = None
            barcol = None
        else:
            col = cm.gray
            barcol = 'black'
        scale = 5. / array([(xmax - xmin), (ymax - ymin)]).max()
        relx = int((xmax - xmin) * scale)
        rely = int((ymax - ymin) * scale)
        fig = plt.figure(1, figsize=(relx + 4, rely + 2))
        ax_plot = plt.subplot(111)
        divider = make_axes_locatable(ax_plot)
        ax_marx = divider.new_vertical(1, 0.2, sharex = ax_plot)
        ax_mary = divider.new_horizontal(1, 0.2, True, sharey = ax_plot)
        fig.add_axes(ax_marx)
        fig.add_axes(ax_mary)
        plot = ax_plot.imshow(data, cmap = col, origin = 'lower',
                              extent = [xmin-.5, xmax-.5, ymin-.5, ymax-.5],
                              vmin = options['vmin'], vmax = options['vmax'],
                              interpolation = 'nearest')
        widths = ones(xmax - xmin)
        heights = ones(ymax - ymin)
        left = array(range(xmin, xmax)).astype('float') - .5
        bottom = array(range(ymin, ymax)).astype('float') - .5
        ax_marx.bar(left, xmargin, widths, color = barcol)
        ax_mary.barh(bottom, ymargin, heights, yleft, color = barcol)
        ax_plot.get_yaxis().tick_right()
        plt.setp(ax_marx.get_xticklabels() + ax_mary.get_yticklabels(),
                 visible=False)
        ax_plot.set_xlabel(options['xlabel'])
        ax_plot.get_yaxis().set_label_position('right')
        ax_plot.set_ylabel(options['ylabel'])
        ax_marx.get_yaxis().set_ticks([0, max_round[0]])
        ax_mary.get_xaxis().set_ticks([0, max_round[1]])
        ax_mary.get_xaxis().set_ticklabels([max_round[1], 0])
        l, b, w, h = ax_plot.get_position().bounds
        ax_plot.set_position([l - .08, b, w, h])
        cb = pylab.colorbar(plot)
        l, b, w, h = cb.ax.get_position().bounds
        cb.ax.set_position([l + .08, b, w, h])
        plt.show()
    
    def plot_cdf(self, range, options = {}):
        """
        Plot the CDF in the given range
        
        @type  range: Tuple
        @param range: Tuple [xmin, xmax, ymin, ymax] or [xmax, ymax]
        @type  options: Dictionary
        @param options: Option set for the plot:
                            - B{color}: True or False (default: False)
                            - B{plot_steps}: Density of the grid in 3d-plot
                            (Integer, default: 25)
                            - B{xlabel}: Label for the x-axis (String)
                            - B{ylabel}: Label for the y-axis (String)
                            - B{vmin}: Minimum value for color scale (if none
                            is specified use max(0, min(data)))
                            - B{vmax}: Maximum value for color scale (if none
                            is specified use min(10, max(data)))
        """
        self.plot(self.cdf, range, options)
    
    def plot_pdf(self, range, options = {}):
        """
        Plot the PDF in the given range
        
        @type  range: Tuple
        @param range: Tuple [xmin, xmax, ymin, ymax] or [xmax, ymax]
        @type  options: Dictionary
        @param options: Option set for the plot:
                            - B{color}: True or False (default: False)
                            - B{plot_steps}: Density of the grid in 3d-plot
                            (Integer, default: 25)
                            - B{xlabel}: Label for the x-axis (String)
                            - B{ylabel}: Label for the y-axis (String)
                            - B{vmin}: Minimum value for color scale (if none
                            is specified use max(0, min(data)))
                            - B{vmax}: Maximum value for color scale (if none
                            is specified use min(10, max(data)))
        """
        self.plot(self.pdf, range, options)
