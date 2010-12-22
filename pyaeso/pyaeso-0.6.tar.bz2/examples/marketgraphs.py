#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2009 Keegan Callin

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see
#~ <http://www.gnu.org/licenses/gpl-3.0.html>.

#######################################################################
## Imports

# Standard library imports
import datetime
import time
import decimal
from decimal import Decimal
import collections
import time
import sys
import re
import stat
import os
import os.path
import math
from StringIO import StringIO

# Plotting libraries
NUMPY = 'numpy'
MATPLOTLIB = 'matplotlib'
PYAESO = 'pyaeso'
SCIPY = 'scipy'
package_urls = {
    NUMPY : 'http://numpy.scipy.org',
    MATPLOTLIB : 'http://matplotlib.sourceforge.net',
    PYAESO : 'http://pypi.python.org/pypi/pyaeso',
    SCIPY : 'http://scipy.org/Download',
}

missing_packages = []
try:
    import numpy
except ImportError:
    missing_packages.append(NUMPY)

try:
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import matplotlib.ticker as ticker
    import pylab
except ImportError:
    missing_packages.append(MATPLOTLIB)

try:
    from scipy.ndimage.filters import maximum_filter1d
    from scipy.ndimage.filters import minimum_filter1d
except ImportError:
    missing_packages.append(SCIPY)

# Other 3rd Party Libraries
try:
    from pyaeso import ets
except ImportError:
    missing_packages.append(PYAESO)

if missing_packages:
    if len(missing_packages) == 1:
        print 'A required package is missing.  Please install it before proceeding.'
    else:
        print 'Please install the following missing packages before proceeding.'

    for m in missing_packages:
        print '*', m, '(available as of 2009-12-09 from <' + package_urls[m] + '>)'

    sys.exit(1)


#######################################################################
## Program Code

class QpTimeSeries(object):
    '''Quantity/Price Time series.'''

    def __init__(self, t, price, demand):
        self.t = numpy.array(t)
        self.price = numpy.array(price)
        self.demand = numpy.array(demand)

        if len(self.t)  != len(self.price) or len(self.t) != len(self.demand):
            raise IndexError('Lists t, price, and demand must all have the same length')


    @classmethod
    def from_pointlist(klass, pointlist):
        t = [p.t for p in pointlist]
        price = [float(p.price) for p in pointlist]
        demand = [float(p.demand) for p in pointlist]

        return QpTimeSeries(t, price, demand)


class FigureData(object):
    def __init__(self,
            t,
            demand_series,
            price_series,
            range_t,
            range_demand_series,
            range_price_series,
            demand_min_series,
            demand_max_series,
            price_min_series,
            price_max_series):
        self.t = t
        self.demand_series = demand_series
        self.price_series = price_series

        self.range_t = range_t
        self.range_demand_series = range_demand_series
        self.range_price_series = range_price_series
        self.demand_min_series = demand_min_series
        self.demand_max_series = demand_max_series
        self.price_min_series = price_min_series
        self.price_max_series = price_max_series


        if len(self.t) != len(self.demand_series):
            raise IndexError('Array t must have the same length as demand_series.')
        elif len(self.range_t) != len(self.demand_min_series) or \
                len(self.range_t) != len(self.demand_max_series):
            raise IndexError('Array range_t must have the same length as demand_min_series and demand_max_series.')
        elif len(self.t) != len(self.price_series):
            raise IndexError('Array t must have the same length as price_series.')
        elif len(self.range_t) != len(self.range_demand_series) or \
                len(self.range_t) != len(self.range_price_series):
            raise IndexError('Array range_t must have the same length as range_demand_series and range_price_series.')
        elif len(self.range_t) != len(self.price_min_series) or \
                len(self.range_t) != len(self.price_max_series):
            raise IndexError('Array range_t must have the same length as price_min_series and price_max_series.')


    def save(self, f):
        numpy.save(f, self.t)
        numpy.save(f, self.demand_series)
        numpy.save(f, self.price_series)
        numpy.save(f, self.range_t)
        numpy.save(f, self.range_demand_series)
        numpy.save(f, self.range_price_series)
        numpy.save(f, self.demand_min_series)
        numpy.save(f, self.demand_max_series)
        numpy.save(f, self.price_min_series)
        numpy.save(f, self.price_max_series)


    @classmethod
    def load(klass, f):
        t = numpy.load(f)
        demand_series = numpy.load(f)
        price_series = numpy.load(f)
        range_t = numpy.load(f)
        range_demand_series = numpy.load(f)
        range_price_series = numpy.load(f)
        demand_min_series = numpy.load(f)
        demand_max_series = numpy.load(f)
        price_min_series = numpy.load(f)
        price_max_series = numpy.load(f)

        return klass(t, demand_series, price_series, range_t, range_demand_series, range_price_series, demand_min_series, demand_max_series, price_min_series, price_max_series)


def downsample(array, period, offset = 0):
    return numpy.array([array[i] for i in xrange(offset, len(array), period)])


def block_avg_filter(array, size):
    # Convolution function is a sliding-average filter.
    sliding_avg = numpy.convolve(array, 1./size * numpy.ones(size), mode = 'valid')

    # Downsample such that the last sampled point is the last element
    # of sliding_avg array.
    return downsample(sliding_avg, size, (len(sliding_avg) - 1) % size)


def block_max_filter(array, size):
    sliding_max = maximum_filter1d(array, size)

    # Downsample such that the last sampled point is the last element
    # of sliding_max array.
    return downsample(sliding_max, size, size - 1 + len(sliding_max) % size)


def block_min_filter(array, size):
    sliding_min = minimum_filter1d(array, size)

    # Downsample such that the last sampled point is the last element
    # of sliding_min array.
    return downsample(sliding_min, size, size - 1 + len(sliding_min) % size)


def format_date(x, pos = None):
    return datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d')


def demand_figure(data):
    '''Plots market clearing demand vs. time.'''

    # Create figure and setup graph
    fig = plt.figure()
    graph = fig.add_subplot(1, 1, 1)
    graph.set_title('Weekly Mean Power Demand (MW) vs. Date')
    graph.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    graph.set_xlabel('Date')
    graph.set_ylabel('Weekly Mean Power Demand (MW)')
    graph.grid(True)
    fig.autofmt_xdate()

    # Plot data range and average
    graph.fill_between(data.range_t, data.demand_min_series, data.demand_max_series, color='#e0e0ff')
    graph.plot(data.t, data.demand_series, '-')

    graph.set_ylim(0, graph.get_ylim()[1]) # set y-range
    return fig # return figure to be used for rendering


def price_figure(data):
    '''Plots market clearing price vs. time.'''

    # Create figure and setup graph
    fig = plt.figure()
    graph = fig.add_subplot(1, 1, 1)
    graph.set_title('Weekly Mean Power Price ($/MW) vs. Date')
    graph.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    graph.set_xlabel('Date')
    graph.set_ylabel('Weekly Mean Power Price ($/MW)')
    graph.grid(True)
    fig.autofmt_xdate()

    # Plot price range and average
    #graph.fill_between(data.range_t, data.price_min_series, data.price_max_series, color='#e0e0ff')
    graph.plot(data.t, data.price_series, '-')

    #graph.set_ylim(0, graph.get_ylim()[1]) # set y-range
    graph.set_ylim(0, 100) # set y-range
    return fig # return figure to be used for rendering


def equilibrium_figure(data):
    '''Plots market clearing points.'''

    # Create figure and setup graph
    fig = plt.figure()
    graph = fig.add_subplot(1, 1, 1)
    graph.set_title('Yearly Market Equilibrium Points')
    graph.set_xlabel('Yearly Mean Power Demand (MW)')
    graph.set_ylabel('Yearly Mean Power Price ($/MW)')
    graph.grid(True)

    # Plot equilibrium points
    graph.plot(data.range_demand_series, data.range_price_series, marker='o')
    for i in xrange(len(data.range_t)):
        x = data.range_demand_series[i]
        y = data.range_price_series[i]

        # Label points
        graph.text(x, y, datetime.datetime.fromtimestamp(data.range_t[i]).strftime('%Y'))

    return fig # return figure to be used for rendering


def create_figure_data(f, dump_timing = False):
    # Load data file
    data = [d for d in ets.parse_pool_price_file(f) if d.demand is not None]
    if not data:
        raise EOFError('Data file is empty')

    # Convert data list to numpy arrays
    series = QpTimeSeries.from_pointlist(data)

    # Calculate some point averages.
    size = 7*24
    start_idx = size - 1 + len(series.t) % size
    avg_t = numpy.array([time.mktime(series.t[i].timetuple()) for i in xrange(start_idx, len(series.t), size)])
    demand_avg_series = block_avg_filter(series.demand, size)
    price_avg_series = block_avg_filter(series.price, size)

    # Calculate max/min timescale
    size = 365*24
    start_idx = size - 1 + len(series.t) % size
    range_t = numpy.array([time.mktime(series.t[i].timetuple()) for i in xrange(start_idx, len(series.t), size)])
    range_demand_series = block_avg_filter(series.demand, size)
    range_price_series = block_avg_filter(series.price, size)

    # Calculate min series
    demand_min_series = block_min_filter(series.demand, size)
    price_min_series = block_min_filter(series.price, size)

    # Calculate max series
    demand_max_series = block_max_filter(series.demand, size = size)
    price_max_series = block_max_filter(series.price, size = size)

    return FigureData(avg_t, demand_avg_series, price_avg_series, range_t, range_demand_series, range_price_series, demand_min_series, demand_max_series, price_min_series, price_max_series)


def download_and_create_figure_data(start_date, end_date):
    '''Download raw csv files, process them, and return data necessary
    for drawing the figure.'''

    # Download data from website and buffer it
    f = StringIO()
    ets.dump_pool_price(f, start_date, end_date)
    csvdata = f.getvalue()
    f.close()

    # To speed things, save cvsdata to disk and cache it rather than
    # calling dump_pool_price each time.

    # Create data necessary for drawing
    f = StringIO(csvdata)
    data = create_figure_data(f)
    f.close()

    return data


def  main():
    start_date = datetime.date(1995, 1, 1)
    end_date = datetime.date.today()

    data = download_and_create_figure_data(start_date, end_date)

    fn = 'market-demand.png'
    print 'Generating', fn
    fig = demand_figure(data)
    f = open(fn, 'wb')
    fig.savefig(f, format='png', dpi=80, transparent=False, bbox_inches="tight", pad_inches=0.15)
    #fig.savefig(f, format='pdf', transparent=False, bbox_inches="tight", pad_inches=0.1, orientation = 'landscape', papertype = 'letter')
    f.close()

    fn = 'market-price.png'
    print 'Generating', fn
    fig = price_figure(data)
    f = open(fn, 'wb')
    fig.savefig(f, format='png', dpi=80, transparent=False, bbox_inches="tight", pad_inches=0.15)
    #fig.savefig(f, format='pdf', transparent=False, bbox_inches="tight", pad_inches=0.1, orientation = 'landscape', papertype = 'letter')
    f.close()

    fn = 'market-equilibrium.png'
    print 'Generating', fn
    fig = equilibrium_figure(data)
    f = open(fn, 'wb')
    fig.savefig(f, format='png', dpi=80, transparent=False, bbox_inches="tight", pad_inches=0.20)
    #fig.savefig(f, format='pdf', transparent=False, bbox_inches="tight", pad_inches=0.1, orientation = 'landscape', papertype = 'letter')
    f.close()

    return 0


if __name__ == '__main__':
    sys.exit(main()) #~425
