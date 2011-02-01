# -*- coding: utf-8 -*-
"""
Spike train utility methods.

Utility methods for reading spike train files as well
as to analyze spike train matrices and vectors.

AUTHORS:

- THOMAS MCTAVISH (2010-03-01): initial version
"""
# While this software is under the permissive MIT License, 
# (http://www.opensource.org/licenses/mit-license.php)
# We ask that you cite the neuronpy package (or tools used in this package)
# in any publications and contact the author with your referenced publication.
#
# Format:
# McTavish, T.S. NeuronPy library, version 0.1, http://bitbucket.org/tommctavish/neuronpy
#
# Copyright (c) 2010 Thomas S. McTavish
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__version__ = 0.1

import pickle
import bisect
from itertools import izip
import numpy
from neuronpy.util import listutil
from neuronpy.util import vartest
from neuronpy.math import kernel as mathkernel
from scipy import ndimage

        
def index(a, x):
    """Locate the leftmost value of an ascending sorted list exactly equal 
    to x"""
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError

def subset_file(file_name, out_file_name, spike_ids):
    """Read the spike data formatted from NEURON where each line is a timestamp
    of spike followed by a cell (or other spike generator) id that gave the
    spike. Echo a new file in the same format, but only of those spike_ids
    specified as a list."""
    in_file = open(file_name, 'r') # Open the file
    out_file = open(out_file_name, 'w')
    for a_line in in_file:
        tosplit = a_line.split()
        idx = int(tosplit[1])
        # See if this idx is in the list
        try:
            index(spike_ids, idx)
        except ValueError:
            continue
        
        out_file.write(a_line)
    in_file.close()
    out_file.close()
    

def read_file(file_name, spike_ids=None):
    """
    Read the spike data formatted from NEURON where each line is a timestamp
    of spike followed by a cell (or other spike generator) id that gave the
    spike.

    :param file_name: Name of the spike file to read.
    :param spike_ids: If specified, a subset of ids to load. This should be an
        sorted-ascending list.
    
    :return: The data in a dict where the key is the cell id
        and the list of spike times is the data associated with the cell.
    """
    the_file = open(file_name, 'r') # Open the file
    data = dict()
    for a_line in the_file:
        tosplit = a_line.split()
        idx = int(tosplit[1])
        if spike_ids is not None:
            # See if this idx is in the list
            try:
                index(spike_ids, idx)
            except ValueError:
                continue

        tval = float(tosplit[0])
            
        if idx in data:
            spikes_idx = data[idx]
            spikes_idx.append(tval)
            data[idx] = spikes_idx
        else:
            data[idx] = [tval]
    the_file.close()
    
    return data
    
def read_file_to_vector(file_name, spike_ids=None):
    """
    Read the spike data formatted from NEURON where each line is a timestamp
    of spike followed by a cell (or other spike generator) id that gave the
    spike.

    :param file_name: Name of the spike file to read.
    :param spike_ids: If specified, a subset of ids to load. This should be an
        sorted-ascending list.
    
    :return: The data in a vector of tuples of the format (time, gid).
    """
    the_file = open(file_name, 'r') # Open the file
    data = []
    for a_line in the_file:
        tosplit = a_line.split()
        idx = int(tosplit[1])
        if spike_ids is not None:
            # See if this idx is in the list
            try:
                index(spike_ids, idx)
            except ValueError:
                continue

        tval = float(tosplit[0])
        data.append((tval, idx))
    the_file.close()
    
    return data

def pickle_spikes(filename, spikes):
    with open(filename, 'w') as pickle_file: # Make a new file
        pickle.dump(spikes, pickle_file)    # Write spikes

def netconvecs_to_dict(t_vec, id_vec):
    """
    Convert data from NetCon.record(tvec, idvec) vectors into a dict
    where the keys of the dict are the ids and the value is a list of
    timestamps associated with that id.
    
    :param tvec: Timestamp vector.
    :param idvec: Associated ids of each timestamp.
    
    .. NOTE: idvec and tvec must be the same length.
    
    Example::

        # nclist is a list of NetCons
        t_vec = nrn.Vector()
        id_vec = nrn.Vector()
        
        for i in range(len(nclist)):
            nclist[i].record(t_vec, id_vec, i)

        simulate()
        
    :return: The data in a dict where the key is the cell id
        and the list of spike times is the data associated with the cell.
    """
    data = dict()
    for (ts, idx) in izip(t_vec, id_vec):
        if idx in data:
            spikes_idx = data[idx]
            spikes_idx.append(ts)
            data[idx] = spikes_idx
        else:
            data[idx] = [ts]
    
    return data

def netconvecs_to_listoflists(t_vec, id_vec):
    """
    Convert data from NetCon.record(tvec, idvec) vectors into a dict
    where the keys of the dict are the ids and the value is a list of
    timestamps associated with that id.
    
    :param tvec: Timestamp vector.
    :param idvec: Associated ids of each timestamp.
    
    .. NOTE: idvec and tvec must be the same length.
    
    Example::

        # nclist is a list of NetCons
        t_vec = nrn.Vector()
        id_vec = nrn.Vector()
        
        for i in range(len(nclist)):
            nclist[i].record(t_vec, id_vec, i)

        simulate()
        
    :return: The data as a list of lists with each row being the spike
        times.
    """
    as_dict = netconvecs_to_dict(t_vec, id_vec)
    return dictspikes_to_listoflists(as_dict)

def dictspikes_to_listoflists(dict_data):
    lol = []
    for v in dict_data.itervalues():
        lol.append(v) # v should be a list.
    return lol

def print_spikes(data, idx=0, window=None):
    """
    Print the spike times of cell idx within window window.
    
    :param data: This should be a 2D array or
        a set or dict where the spikes from a given cell can be
        accessed as data[idx]. The spikes also need to be sorted
        if window is specified.
        
    :param idx: id(s) from ``data`` to extract. If blank, then this will 
        retrieve the spikes of ``0``. If a integer, it will return
        the spikes of that index. If a list of integers, then it will
        return those spikes in the list.
        
    :param window: A tuple, (lo, hi), specifying the window range of 
        values to return. 
    """
    try :
        spikes = get_spikes(data, idx, window)
        for spike in spikes:
            print(spike)
    except:
        raise

def get_spikes(data, idx=0, window=None):
    """
    Get the spikes from the cell with this idx within a time window.
    
    :param data: is the spike data. This should be a 2D array or
        a set or dict where the spikes from a given cell can be
        accessed as data[idx]. The spikes also need to be sorted
        in time if window is specified.
        
    :param idx: id(s) from ``data`` to extract. If blank, then this will 
        retrieve the spikes of ``0``. If an integer, it will return
        the spikes of that index. If a list of integers, then it will
        return those spikes in the list.
        
    :param window: A tuple, (lo, hi), specifying the window range of 
        values to return.
        
    :return: If idx is a scalar, then this will return the spikes
        associated with one cell. If idx is a list of indices, then
        a dict of lists will be returned.
    """
    # Make an empty copy.
    if isinstance(idx, list):
        ret = dict()
        for i in idx:
            ret[i] = _get_spikes_sub(data, i, window)
        return ret
    else:
        return _get_spikes_sub(data, idx, window)

def _get_spikes_sub(data, idx=0, window=None):
    """
    Get the spikes from the cell with this idx within window window.
    
    :param data: is the spike data. This should be a 2D array or
        a set or dict where the spikes from a given cell can be
        accessed as data[idx]. The spikes also need to be sorted
        if window is specified.
        
    :param idx: is the id from data to extract.
    
    :param window: a tuple, (low, high), specifying the window range of 
        values to return.
        
    :return: A list of spike times or an empty list if no spikes are valid. 
    """
    try :
        if type(window) is tuple and len(window)==2:
            spikes = data[idx]
            low = bisect.bisect_left(spikes, window[0])
            high = bisect.bisect_right(spikes, window[1])
            return spikes[low:high]
        else:
            if idx in data:
                return data[idx]
            else:
                return [] # Empty array
    except:
        raise

def get_isi_vec(spikes):
    """
    Given an ordered list of spike times, return its interspike interval 
    vector.
    
    :param train: 1D list or numpy array of spike times
    
    :return: A 1D vector of length len(spikes)-1 of the time differences in spikes.
    """
    vec = range(len(spikes)-1)
    for i in range(1, len(spikes)):
        vec[i-1] = spikes[i] - spikes[i-1]
    return vec

def get_mean_isi(train):
    """Get the mean interspike interval of a given spike train.
    
    :param train: 1D list or numpy array of spike times
    :return: Mean interspike interval.
    """
    isi_vec = get_isi_vec(train)
    return numpy.median(isi_vec)
    
def get_median_isi(train):
    """Get the median interspike interval of a given spike train.
    
    :param train: 1D list or numpy array of spike times
    :return: Median interspike interval.
    """
    isi_vec = get_isi_vec(train)
    return numpy.median(isi_vec)
    
def permute_vec(vec):
    """Permute a 1D array."""
    return numpy.random.shuffle(vec)
    
def get_spike_bounds(spikes):
    """
    From a 2D array of spike data, retrieve the minimum and maximum spike 
    times.
    """
    spikes_min_x = spikes_max_x = 0
    if isinstance(spikes, list) is False:
        raise TypeError('spikes is not a list.')
    if len(spikes) == 0:
        raise listutil.ListEmptyError('spikes')
    spikes_copy = listutil.flatten_from_2d(spikes)
    if len(spikes_copy) == 0:
        raise listutil.ListEmptyError('spikes')
    spikes_min_x = min(spikes_copy)
    spikes_max_x = max(spikes_copy)
        
    return spikes_min_x, spikes_max_x
        
def get_flattened(spikes):
    """
    Project the spike times from a 2d spike map to an ordered list in one
    dimension. This is similar to numpy's flatten() method, but numpy requires
    a rectangular matrix. In our case, each row of the spikes array can have
    a variable number of spike times, and even be empty.
    """
    flattened = listutil.flatten_from_2d(spikes)
    return numpy.sort(flattened)
    
def get_permuted_train(train, num_copies=1, smear = False):
    """
    With a given spike train, capture its interspike intervals and permute
    them into a new spike train.
    
    :param train: is the spike train to permute. It is unaffected.
    
    :param num_copies: is the number of times the spike train is permutted. 
        The default value of 1 returns a permutted vector the same length as
        the original train. A value of 2 would return a vector twice the
        length.
    """
    isi = get_isi_vec(train)
    mean_isi = numpy.mean(isi)
    rval = []
    vec = isi[:]

    for i in xrange(num_copies):
        numpy.random.shuffle(vec)
        cumsum = numpy.cumsum(vec)
        if smear:
            randnum = numpy.random.uniform(-mean_isi/2., mean_isi/2.)
            cumsum = numpy.add(cumsum, randnum)
        try:
            cumsum = numpy.add(cumsum, rval[-1])
        except IndexError: # rval probably does not yet exist
            pass
    
        rval = numpy.concatenate([rval, cumsum])
    
    return rval

def get_histogram(spikes, window=None, dt=1, bins=None):
    r"""
    Get the histogram of one or more spike trains. This is a means of quantizing 1D spikes
    as well.
    
    :param spikes: A 1D python list, or 1D or 2D numpy array of spike times.
    
    :param window: A tuple, (lo, hi), specifying a subset in time if the complete
            spikes are not used. The default value of ``None`` uses the complete spikes.
            
    :param dt: Is the time bin to discretize by. Default is 1.
    
    :param bins: A numpy array specifying the histogram edges. Default is ``None``. If
            bins is specified, then it ignores window and dt.
    
    :return: A tuple of the form (discrete, bin_edges).
    
    .. seealso:: http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html 
    """
    if spikes is None:
        errstr = 'spikes is None and should be a python list, list of lists, '
        errstr += 'or numpy array.'
        raise TypeError(errstr)
    if isinstance(spikes[0], list):
#    shape = numpy.shape(spikes)
#    if len(shape) == 0:
#        if isinstance(spikes, list) is False and \
#                isinstance(spikes, numpy.ndarray) is False:
#            raise TypeError('spikes must be a python list or numpy array.')
#        else:
#            raise ValueError('spikes has no dimension')
#    if len(shape) > 1:
        spks = get_flattened(spikes)
    else:
        spks = spikes
        
    if window is None:
        window = (spks[0], spks[-1])
        
    if bins is None:
        bins = numpy.arange(window[0], window[1], dt)
        bins = numpy.append(bins, window[1])
        
    return numpy.histogram(spks, bins)
    
def filter(spikes, kernel=[1.], origin='center', window=None, dt=1):
    """Convolve a 1D spike train with a kernel and return the resulting vector. This is
    useful for blurring or otherwise smearing spike times with a particular
    function, like a gaussian, a linear decay.
    
    :param spikes: A 1D python list or numpy array of spike times.
    
    :param kernel: A 1D python list or numpy array of filter values. Care might need
        to be taken to ensure that this sums to 1 to keep the magnitude the same.
        By default this is [1.0], which means that the output is a copy of the input.
    .. seealso:: :mod:`neuronpy.math.kernel` 
 
    :param origin: can be a string or an integer.:
    - *integer*
      is an integer to specify the offset of the kernel
      applied in the convolution. This needs to be between 0 and
      the length of the kernel - 1. By default, this is 0 and therefore
      centers the kernel. A negative value shifts the kernel to the 
      right and a positive value shifts the kernel to the left.
    - *string*
      Can be 'left', 'center', or 'right'
   
    :param window: A tuple, (lo, hi), specifying a subset in time if the complete
            spikes are not used. The default value of ``None`` uses the complete spikes.
            
    :param dt: Is the time bin to discretize by. Default is 1.
        
    :return: A 1D vector of the filtered spikes.
    """
    vartest.is1Dvector(spikes, 'spikes')
    org = validate_kernel_and_origin(kernel, origin)
    (discrete, bin_edges) = get_histogram(spikes, window=window, dt=dt)
    return ndimage.convolve1d(numpy.asfarray(discrete), weights=kernel, origin=org, \
            mode='constant')


def validate_kernel_and_origin(kernel, origin):
    """
    Confirm that the origin for this kernel is valid. Raise an exception if not.
    
    :param origin: can be a string or an integer.:
    - *integer*
      is an integer to specify the offset of the kernel
      applied in the convolution. This needs to be between 0 and
      the length of the kernel - 1. By default, this is 0 and therefore
      centers the kernel. A negative value shifts the kernel to the 
      right and a positive value shifts the kernel to the left.
    - *string*
      Can be 'left', 'center', or 'right'
      
    :return: a valid integer if a string was used.
    """
    vartest.is1Dvector(kernel, 'kernel')
    if isinstance(origin, str):
        valid = ['left', 'center', 'right']
        vartest.inlist(origin, valid, 'origin')
        lenk = len(kernel)
        if origin=='left':
            _origin = -int(numpy.ceil(lenk/2.0))
        elif origin=='right':
            _origin = int(numpy.ceil(lenk/2.0)) - 1
        else:
            _origin = 0
    else:
        _origin = origin
    vartest.isint(_origin, 'origin')
    lenk = len(kernel)
    min = -int(numpy.ceil(lenk/2.0))
    max = -min - 1
    vartest.inrange(_origin, min, max, 'origin')

    return _origin
    
def filter_correlogram(train_a, train_b=None, kernel=None, origin=None, window=None, \
        dt=1., mode='full'):
    """Perform a cross-correlation between two spike trains. This performs
    numpy's correlation function,
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.correlate.html after
    filtering the spike trains passed in.
    
    :param train_a: List of spike times in one train.
    
    :param train_b: List of spike times in another train. Default is ``None``, which
        means that autocorrelation is performed on ``train_a``.
    
    :param kernel: Is the 1D filter that is applied to the two trains before they are
        correlated. By default, this is ``None``, which makes it take on a Gaussian of
        sigma=2 using the dt parameter passed in, if used.
        
    :param origin: Offset for the filter. .. seealso:: :func:`filter`.
    
    :param window: Time window to evaluate. By default, this is ``None``, which means that
        the first inputs.

    """
    vartest.is1Dvector(train_a, 'train_a')
    if train_b is not None:
        vartest.is1Dvector(train_a, 'train_b')
    if kernel is None:
        kernel = mathkernel.gauss_1d(sigma=2., dt=dt)
    if origin is None:
        origin = 0
    if window is None:
        if train_b is None:
            window = (train_a[0], train_a[-1])
        else:
            window = (numpy.min([train_a[0], train_b[0]]), \
                    numpy.max([train_a[-1], train_b[-1]]))
                    
    fa = filter(train_a, kernel, origin, window, dt)
    norm_factor = numpy.correlate(fa, fa, mode='valid')
    if train_b is not None:
        fb = filter(train_b, kernel, origin, window, dt)
        norm_factor = numpy.max([norm_factor, numpy.correlate(fb, fb, mode='valid')])
    else:
        fb = fa
    return numpy.divide(numpy.correlate(fa, fb, mode=mode, old_behavior=False), \
            float(norm_factor))
    
                     
def get_sync_traits(train_a, train_b, window=5):
    """
    For two spike trains, get their masks where they have spikes that occur
    within ``window`` time of each other and the ratio of correlated vs. 
    total spikes in both trains.
    
    :param train_a: List of spike times in one train.
    
    :param train_b: List of spike times in another train.
    
    :param window: Time window to search for correlated inputs.
    
    :return: mask_a, mask_b, ratio -- the correlated masks and the ratio of
        correlated vs. total spikes in both trains.
    """
    mask_a, mask_b = get_sync_masks(train_a, train_b, window)
    len_a = len(train_a)
    len_b = len(train_b)
    num_sync_a = numpy.sum(mask_a)
    num_sync_b = numpy.sum(mask_b)
    ratio = float(num_sync_a + num_sync_b) / float(len_a + len_b)
    
    return num_sync_a, num_sync_b, mask_a, mask_b, ratio
        
def get_phase_correlation(reference_train, sliding_train, window=5, \
            sliding_intervals=13, isi=None):
    r"""
    Get the number of corresponding spikes within some time window between
    two trains across a number of time-shifted trials.
    
    The number of correlated spikes between two trains that are within some 
    time constant of each other is simply the fraction:
        
    .. math::    
        
        \phi_{0} = \frac{\small{\textrm{
        number of correlated spikes within a time window}}}{\small{\textrm{
        total number of spikes in both trains.}}}
    
    where :math:`\phi_{0}` is the fraction with no delay between the trains.
    To determine the correlation at some arbitrary delay, :math:`\tau`, we
    can re-write the equation as:
        
    .. math::
        
        \phi_{\tau} = \frac{\small{\textrm{
        number of correlated spikes within a time window}}}{\small{\textrm{
        total number of spikes in both trains.}}}
       
    where :math:`\tau` is the time one train is shifted relative to the 
    reference train.
    
    When the trains are spiking fairly regularly and oscillating around a
    particular frequency, it is useful to vary :math:`\tau` over the interval
    
    .. math::
        
        \tau=\left[\frac{-median\_isi}{2},  \frac{median\_isi}{2}\right]
        
    where ``median_isi`` is the median interspike interval of the reference 
    train. This permits a measure of the relative phase of one spike train 
    over the other. As :math:`\tau` varies over this interval, the individual 
    values of :math:`\phi_{\tau}` can be stored in a vector, :math:`\Phi`.
        
    :param reference_train: Spike times of the reference train. It is 
        assumed that the spike times are ordered sequentially.
    
    :param sliding_train: Spike times of the train that shifts in time.
        It is assumed that the spike times are ordered sequentially.
    
    :param window: Time window to say that two spikes are synchronized.
        This has a default value of 5.
        
    :param sliding_intervals: Number of iterations to perform, sliding
        ``sliding_train`` from [-1/2, 1/2] the median of ``reference_train``'s
        interspike interval. This should be an odd number to ensure a 
        precise sample about 0 delay.
        
    :param isi: If specified, this value will override the median interspike
        interval of the reference train.
        
    :return: The following values:
            
            * ``relative_sync``, which is the value of the number of 
                correlated spikes with no delay offset between the spike 
                train, divided by the mean of the :math:`\Phi`.
            * ``phi_0``, which is the number of correlated spikes within the 
                time window divided by the total number of spikes in both 
                trains.
            * ``mu``, the mean of the :math:`\Phi` vector.
            * ``phi_vec``, the :math:`\Phi` vector.
            
    .. seealso:: :func:`coincidence_factor_phase` 
    """
    num_sync_a, num_sync_b, mask_a, mask_b, phi_0 = get_sync_traits( \
            reference_train, sliding_train, window)
            
    if isi is None or not isinstance(isi, float):
        isi = get_mean_isi(reference_train)
        
    phi_vec = numpy.zeros(sliding_intervals)
    idx = 0
    shift = isi/sliding_intervals/2.
    for i in numpy.linspace(-isi/2.+shift, isi/2.-shift, sliding_intervals):
        vec = numpy.add(sliding_train, i)
        num_sync_a, num_sync_b, mask_a, mask_b, ratio = get_sync_traits( \
                reference_train, vec, window)
        phi_vec[idx] = ratio
        idx += 1
        
    mu = numpy.mean(phi_vec)
    
    return phi_0/mu, phi_0, mu, phi_vec
    
def coincidence_factor(ref, comp, window=5, isi=None):
    r"""
    The coincidence factor :math:`\Gamma` between two spike trains is defined as

    .. math::
        
       \Gamma = \frac{N_\mathrm{coinc}- E \left( N_\mathrm{coinc} \right)}
       {\frac{1}{2}\left(N_\mathrm{ref}+N_\mathrm{comp}\right) - 
       E \left( N_\mathrm{coinc} \right)}

    where :math:`N_{\mathrm{ref}}` are the number of spikes in the reference train,
    :math:`N_{\mathrm{comp}}` is the number of spikes in the comparing train, 
    :math:`N_{\mathrm{coinc}}` is the number of coincident spikes within a time window 
    :math:`\Delta`, :math:`E \left( N_\mathrm{coinc} \right) = 2 v \Delta N_{\mathrm{ref}}` 
    is the expected number of coincident spikes that would be given by chance 
    if the spikes in the comparing train were generated by a homogeneous 
    Poisson process with its rate :math:`v`. This correlation measure has the range 
    [-1, 1] where 1 is perfectly correlated, 0 is not correlated, and -1 is 
    perfectly anti-correlated.
    
    :param ref: Spike times of the reference train. It is 
        assumed that the spike times are ordered sequentially.
    
    :param comp: Spike times of the train that shifts in time.
        It is assumed that the spike times are ordered sequentially.
    
    :param window: Time window to say that two spikes are synchronized.
        This has a default value of 5.
        
    :param isi: If supplied, this is the isi of the comparing train. Otherwise,
        the rate of the train is computed by taking the last spike minus the
        first spike and dividing by the number of spikes in between.
    
    :return: Coincidence factor
    """
    num_sync_ref, num_sync_comp, mask_a, mask_b, ratio = get_sync_traits( \
            ref, comp, window)
    len_ref = len(ref)
    len_comp = len(comp)
    total_spikes = len_ref + len_comp
    coincidences = (num_sync_ref + num_sync_comp) / 2.
    if isi is None:
        v = (len_comp - 1)/(comp[-1] - comp[0])
    else:
        v = 1./isi
    expected_coincidences = 2 * v * window * len_ref
    return (coincidences - expected_coincidences)*2/ \
            (total_spikes - (2*expected_coincidences))
            
def coincidence_factor_phase(ref, comp, window=5, \
            num_intervals=13, isi=None):
    """
    :param ref: Spike times of the reference train. It is 
        assumed that the spike times are ordered sequentially.
    
    :param comp: Spike times of the comparing train that shifts in time.
        It is assumed that the spike times are ordered sequentially.
    
    :param window: Time window to say that two spikes are synchronized.
        This has a default value of 5.
        
    :param num_intervals: Number of iterations to perform, sliding
        ``comp`` from [-1/2, 1/2] the median of ``ref``'s
        interspike interval. This should be an odd number to ensure a 
        precise sample about 0 delay.
    
    :param isi: If supplied, this is the isi of the comparing train. Otherwise,
        the rate of the train is computed by taking the last spike minus the
        first spike and dividing by the number of spikes in between.
        
    :return: A vector of length ``num_intervals`` that corresponds to 
        coincidence factor values from a shift of -isi/2 to isi/2.
    """        
    phi_vec = numpy.zeros(num_intervals)
    idx = 0
    if isi is None or not isinstance(isi, float):
        isi = get_mean_isi(comp)
    shift = isi/num_intervals/2.
    for i in numpy.linspace(-(isi/2.)+shift, (isi/2.)-shift, num_intervals):
        vec = numpy.add(comp, i)
        phi_vec[idx] = coincidence_factor(ref, vec, window, isi)
        idx += 1
            
    return phi_vec
    
        
def get_frequency(train):
    """
    Get the mean frequency of a spike train.
    """
    try:
        length = len(train)
        first = train[0]
        last = train[-1]            
        return float(length-1)/float(last-first)*1000.
    except: # On any error, just return 0
        return 0
    
def get_sync_masks(train_a, train_b, window=5):
    """
    For two spike trains, return the mask of those trains of spikes that
    are within some time window of co-occurrence in the other train.
    
    :param train_a: A list of spike times.
    
    :param train_b: Another list of spike times.
    
    :param window: Time window +/- about a given spike in one train to look
        for a co-occuring spike in the other train.
        
    :return: Two vectors of ``len(train_a)`` and ``len(train_b)`` where a
        zero indicates that a spike does not co-occur in the other train, and
        1 indicates that a spike co-occurs in the other train within 
        ``window`` time.
    """
    idx_a = 0
    idx_b = 0
    
    mask_a = numpy.zeros_like(train_a)
    mask_b = numpy.zeros_like(train_b)
    
    len_a = len(train_a)
    len_b = len(train_b)
    
    while idx_a < len_a and idx_b < len_b:
        val_a = train_a[idx_a]
        val_b = train_b[idx_b]

        diff = abs(val_a - val_b)
        if diff <= window:
            mask_a[idx_a] = 1
            mask_b[idx_b] = 1
        
        if val_a == val_b:
            idx_a += 1
            idx_b += 1
        else:
            if val_a < val_b:
                idx_a += 1
            else:
                idx_b += 1
    
    return mask_a, mask_b
    
def relative_timing_within_ISI(reference_train, other_train):
    """
    With the reference train, determine its mean interspike interval and then
    iterate through the two trains. For a spike in the reference train,
    determine if there are spikes in the other train within this ISI. If so,
    then add the time difference to a list. Return this list.
    """
    len_a = len(reference_train)
    len_b = len(other_train)
    isi = get_median_isi(reference_train)
    idx_a = 0
    idx_b = 0
    timing_vec = []
    
    while idx_a < len_a and idx_b < len_b:
        val_a = reference_train[idx_a]
        val_b = other_train[idx_b]

        diff = abs(val_a - val_b)
        if diff <= isi:
            timing_vec.append(val_a - val_b)
            
        if val_a == val_b:
            idx_a += 1
            idx_b += 1
        else:
            if val_a < val_b:
                idx_a += 1
            else:
                idx_b += 1
    
    return timing_vec
    
def closest_timing(reference_train, other_train, window=100):
    """
    For each spike in the reference train, determine the closest spike time
    in the other train at least within some window.
    """
    time_dict = {}
    len_a = len(reference_train)
    len_b = len(other_train)
    start_a = 0
    idx_a = 0
    idx_b = 0
    while idx_a < len_a and idx_b < len_b:
        idx_a = start_a
        while idx_a < len_a and idx_b < len_b:
            val_a = reference_train[idx_a]
            val_b = other_train[idx_b]
    
            diff = abs(val_a - val_b)
            if diff > window:
                if val_a - val_b < window:
                    idx_b += 1
                break
            
            if idx_a in time_dict:
                if diff < time_dict[idx_a]:
                    time_dict[idx_a] = val_a - val_b
                else:
                    break
            else:
                time_dict[idx_a] = val_a - val_b
                
            if val_a == val_b:
                idx_a += 1
                idx_b += 1
            else:
                if val_a < val_b:
                    idx_a += 1
                else:
                    idx_b += 1
    
        start_a += 1

    return time_dict