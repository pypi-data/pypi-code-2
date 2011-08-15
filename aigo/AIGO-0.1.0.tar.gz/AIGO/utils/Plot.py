from pylab import *

from itertools import cycle

from AIGO import logger

def createColorMap():
    import matplotlib
    
    cdict=    {'blue': ((0.0, 1.0, 1.0),
                        (0.000001, 1.0, 1.0),
                        (0.5, 0.0, 0.0),
                        (1.0, 0., 0.)),
               'green': ((0.0, 1.0, 1.0),
                         (0.000001, 0.0, 0.0),
                         (0.5, 1.0, 1.0),
                         (1.0, 0.0, 1.0)),
               'red': ((0.0, 1.0, 1.0),
                       (0.000001, 0.0, 0.0),
                       (0.5, 0.0, 0.0),
                       (1.0, 1.0, 1.0))}
    
    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return my_cmap

def surface2D(X, Y, xname="", yname="", tit=""):
    my_cmap=createColorMap()

    fig=figure()
    ax=fig.add_subplot(1,1,1)
    
    range=[ min(min(X),min(Y)), max(max(X),max(Y))]
    z,x,y=histogram2d(X, Y, bins=20, normed=False )
    im=imshow(transpose(z), origin='lower', cmap=my_cmap,  extent=[x[0], x[-1], y[0], y[-1]], aspect='auto')
    
    xlabel(xname)
    ylabel(yname)
    cb=colorbar()
    cb.set_label("Number of Gene Products")
    title(tit)

    if isinteractive():
        fig.show()

def surface3D(y, zdata, xmin=0, xmax=1, xlab='', ylab='', angle=180, tit=""):
    bins=linspace(xmin,xmax,20)
    
    X, Y = np.meshgrid(0.5*(bins[0:-1]+bins[1:]), y)
    
    Z=X.copy()

    for i in arange(len(y)):
        z,x=histogram(zdata[i], bins=bins)
        Z[i]=z

    fig = figure()
    ax = Axes3D(fig)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet)
    #ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1)
    ax.view_init(30, angle)

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    #ax.set_yticks(y)
    ax.set_zlabel('Number of gene products')

    ax.set_title(tit)
    
    if isinteractive():
        fig.show()

def multiBar(lBar, lLabel, ticLabel, xlab="", ylab="", lloc="upper left", tit="", grid=False):
    #Check size
    s=len(lBar[0])
    for b in lBar[1:]:
        if len(b) != s:
            print ("Check data size")
            return

    fig=figure(figsize=(14,6))
    ax=fig.add_subplot(1,1,1)
      
    allColors= cycle(['b', 'g', 'r' , 'c', 'm', 'y' , 'k', 'w'])
    
    nBar=len(lBar)

    off=0.3
    freq=1.3
        
    loc=arange(off, off+freq*s, freq)[0:s] ##taking the slice shouldn't be ness but it
    w=1./nBar

    maxVal = 0.
    bars=list()
    for i in arange(nBar):
        assert len(loc)==len(lBar[i]) , " require x locations (%s) to be the same as values (%s)" % (len(loc), len(
                lBar[i]))
        bars.append(ax.bar(loc+i*w, lBar[i], width=w, ec='black', fc=allColors.next(), alpha=1.0))
        maxVal = max(lBar[i])
    ax.axes.set_xlim(0, off + (s) * freq)

    ax.set_xticks(loc+nBar*w/2.0)
    ax.set_xticklabels(ticLabel)

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    if grid:
        ax.yaxis.grid()

    ax.set_title(tit)

    leg=legend( [b[0] for b in bars], lLabel, loc=lloc )
    leg.legendPatch.set_alpha(0.5)

    if isinteractive():
        fig.show()


def venn_2S(v, fontsize=16, tit=None):

    #Extract name of sets
    S=None
    for k in v:
        if len(k.split('@'))==2:
            S = k.split('@')

    if S is None:
        print "Sorry, can't identify the two sets in venn_2S"
        return False

    centers = [(cos(n*2*pi/2), sin(n*2*pi/2)) for n in [0,1]]
    scale = 1.7
    clr = ['yellow', 'blue']

    fig=figure(figsize=(12,12))
    ax=fig.gca(frame_on=False)
    #, autoscale_on=True, aspect='auto')
    ax.set_axis_off()
    subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.01)
        
    for i in range(2):
        name = S[i]
        ax.text(2.1*centers[i][0], 2.1*centers[i][1], name, fontsize=fontsize, bbox=dict(facecolor='white', alpha=0.8),
                stretch='semi-expanded')
        ax.add_patch(Circle(centers[i], scale, facecolor=clr[i], edgecolor='black', fill=True, alpha=0.3))

    # Plot what is in one but neither other
    for i in range(2):
        name = S[i]
        s="%.2f%%" % v[name]
        ax.text(1.5*centers[i][0],1.7*centers[i][1], s, color='black', fontsize=fontsize)

    # Plot intersection of all three
    name='@'.join(S)
    s="%.2f%%" % v[name]
    ax.text(0,0, s, color='black', fontsize=fontsize)

    s="%.2f%%" % (100.0-sum(v.values()))
    ax.text(2.0,2.0, s, color='black', fontsize=fontsize)

    ax.set_xlim(-2.72, 2.72)
    ax.set_ylim(-2.72, 2.72)

    if not tit is None:
        ax.set_title(tit, fontsize=fontsize)

    if isinteractive():
        fig.show()

def venn_3S(v, fontsize=16, tit=None):

    #Extract name of sets
    S=None
    for k in v:
        if len(k.split('@'))==3:
            S = k.split('@')

    if S is None:
        print "Sorry, can't identify the three sets in venn_3S"
        return False

    centers = [(cos(n*2*pi/3), sin(n*2*pi/3)) for n in [0,1,2]]
    scale = 1.7
    clr = ['yellow', 'blue', 'green']
    
    fig=figure(figsize=(12,12))
    ax=fig.gca(frame_on=False)
    ax.set_axis_off()
    subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.01)
    
    for i in range(3):
        name = S[i]
        ax.text(2.1*centers[i][0], 2.1*centers[i][1], name, fontsize=fontsize, bbox=dict(facecolor='white', alpha=0.8),
                stretch='semi-expanded')
        ax.add_patch(Circle(centers[i], scale, facecolor=clr[i], edgecolor='black', fill=True, alpha=0.3))

    # Plot what is in one but neither other
    for i in range(3):
        name = S[i]
        s="%.2f%%" % v[name]
        ax.text(1.5*centers[i][0],1.7*centers[i][1], s, color='black', fontsize=fontsize)

    # Plot pairs of intersections
    D=S*2
    for i in range(3):
        name='@'.join(sorted(D[i:i+2]))
        s="%.2f%%" % v[name]
        ax.text(1.3*cos(i*2*pi/3 + pi/3), 1.3*sin(i*2*pi/3 + pi/3), s, color='black', fontsize=fontsize)

    # Plot intersection of all three
    name='@'.join(S)
    s="%.2f%%" % v[name]
    ax.text(0,0, s, color='black', fontsize=fontsize)

    s="%.2f%%" % (100.0-sum(v.values()))
    ax.text(2.0,2.0, s, color='black', fontsize=fontsize)

    ax.set_xlim(-2.8, 2.8)
    ax.set_ylim(-2.8, 2.8)

    if not tit is None:
        ax.set_title(tit, fontsize=fontsize)

    if isinteractive():
        fig.show()


def venn_NS(v,tit=None):
    logger.info(tit)
    
    idx=argsort( [len(key) for key in v.keys()])
    for key in array(v.keys())[idx]:
        logger.info("%s \t: %.2f" % (key.replace('@', '\t ^ '), v[key]))

    logger.info("TOTAL\t: %.2f" % (100.0-sum(v.values()) ) )

    
