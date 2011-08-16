#!/usr/bin/python
# Filename: scisel.py

from numpy import *
from dtrange import *

def scisel(indata, \
           start= None,end= None,step = None, coords = None, \
           outstart = None, outend = None, outstep = None, outcoords = None):
    # aim:
    # selection from a data set with a given datetime and timestep
    # notes:
    # - we are using numpy arrays
    # - ordered data is needed.
    # - we expect that the data at the asked sample time exists. If not, a nan will be added.

    if (coords == None):
        coords = dtrange(start, end, step)

    if (outcoords == None):
        outcoords = dtrange(outstart, outend, outstep)
    if (outcoords == None):
        outcoords = coords
    steps = len(outcoords)
    outdata = tile(None,steps)
    idx = 0
    outidx = 0
    for datetime in coords:
        if ((datetime >= outcoords[0]) & (datetime <= outcoords[steps - 1]) & \
            (outidx < steps)):
            if ((datetime >= outcoords[outidx])):
                while ((outidx < steps) & (outcoords[outidx] < datetime)):
                    outidx = outidx + 1
                if (datetime == outcoords[outidx]):
                    outdata[outidx] = indata[idx]
                outidx = outidx + 1
        idx = idx + 1
    return outdata

