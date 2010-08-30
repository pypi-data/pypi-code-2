# Continuous Wavelet Transform
# Copyright 2006 by Flavio Codeco Coelho
import math, pylab
import numpy
#import numarray as numpy

def cwt(x, nvoice, wavelet, oct=2, scale=4):
    """
    Continuous Wavelet Transform
    Usage
    >>> cwt(x,nvoice,wavelet,oct,scale)
    Inputs:
    x        signal, dyadic length n=2^J, real-valued
    nvoice   number of voices/octave
    wavelet  string 'Gauss', 'DerGauss','Sombrero', 'Morlet'
    octave   Default=2
    scale    Default=4
    Outputs
    cwt      matrix n by nscale where
             nscale = nvoice .* noctave
    """
    #preparation
    x = numpy.asarray(x)
    n = len(x)
    xhat = numpy.fft.fft(x)
    xi = numpy.concatenate((numpy.arange(n/2+1), numpy.arange(-n/2+1,0))) * (2*numpy.pi/n)

    #root
    omega0 = 5

    # or(?)
    #omega0 = numpy.pi * 2

    #noctave = floor(log(n,2))-1
    noctave = int(math.floor(math.log(n,2))-oct)
    nscale  = nvoice * noctave

    #cwt = numpy.zeros((n,nscale),numpy.Float)
    cwt = []

    exp = numpy.exp
    sqrt = numpy.sqrt
    ifft = numpy.fft.ifft
    for jo in xrange(noctave):
        for jv in xrange(1,nvoice+1):
            qscale = scale*(2**(jv/float(nvoice)))
            omega = xi * (n/qscale)

            # fft of wavelet
            if wavelet == 'Gauss':
                #window = exp((-omega**2)/2.)
                # simple optimization - inplace operations
                omega *= omega
                omega *= -0.5
                exp(omega, omega)
                window = omega

            elif wavelet == 'DerGauss':
                window = 1j*omega*exp(-omega**2/2.)
            elif wavelet == 'Sombrero':
                window = (omega**2)*exp(-omega**2/2.)
            elif wavelet =='Morlet':
                window = exp(-(omega-omega0)**2/2.)-exp(-(omega**2+omega0**2)/2.)

            #Renormalization
            window *= 1./sqrt(qscale)
            what = window*xhat # convolution
            w = ifft(what)

            cwt.append(w.real)

        scale *= 2
    cwt = numpy.vstack(cwt)

    return cwt

def calcCWTScale(sz):
    """
    CalcCWTScale -- Calculate Scales and TickMarks for CWT Display
    Usage:
    xtick,ytick = CalcCWTScale(sz);
    Inputs:
    sz      size of CWT array
    Outputs:
    xtick   vector of positions
    ytick   vector of log2(scales)
    """
    n = sz[1]; nscale = sz[0] #because the plot will be transposed
    noctave = math.floor(numpy.log2(n))-2
    nvoice  = nscale / noctave
    xtick   = pylab.linspace(0,n,n)
    ytick   = pylab.linspace(int(n/2),0,nscale)
    return (xtick,ytick)


def imageCWT(c,cmap=None, title='Scalogram',interpolation='bilinear',origin='image'):
    """
    plot the cwt with the apropriate scaling
    """
    xtick,ytick = calcCWTScale(c.shape)
    #print len(xtick),len(ytick)
    A=pylab.imshow(c,origin=origin, interpolation=interpolation)
    xidx = pylab.linspace(0,len(xtick)-1,len(A.axes.get_xticks())).astype(numpy.int)
    yidx = pylab.linspace(0,len(ytick)-1,len(A.axes.get_yticks())).astype(numpy.int)
    A.axes.set_xticks(xidx)
    A.axes.set_yticks(yidx)
    A.axes.set_xticklabels([str(int(x)) for x in xtick[xidx]])
    A.axes.set_yticklabels([str(int(y)) for y in ytick[yidx]])
    A.axes.set_aspect('auto')
    pylab.xlabel('time(samples)')
    pylab.ylabel('scale')
    pylab.title(title)
    #pylab.show()


if __name__=='__main__':

    #data = numpy.sin(numpy.linspace(0, 8*6.14, 512))

    x = numpy.linspace(0, 1024, 2*1024)
    data = 2*numpy.sin(2*numpy.pi/4 * x) * numpy.exp(-(x-400)**2/(2*300**2)) + \
           numpy.sin(2*numpy.pi/32*x) * numpy.exp(-(x-700)**2/(2*100**2)) + \
           numpy.sin(2*numpy.pi/32 * (x/(1+x/1000)) )


    pylab.figure()
    pylab.plot(data)

    #interpolation = 'nearest'
    interpolation = 'bilinear'
    origin = 'image'

    #import time
    for wname in ['Gauss', 'DerGauss', 'Sombrero', 'Morlet']:
        pylab.figure()
        #t = time.clock()
        c = cwt(data, nvoice=8, wavelet=wname, oct=2, scale=4)
        #print time.clock() - t
        #c = abs(c)
        imageCWT(c,title='%s wavelet' % wname,origin=origin,interpolation=interpolation)
    pylab.show()








