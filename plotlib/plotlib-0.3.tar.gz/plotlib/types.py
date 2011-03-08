import numpy as np


def image(plottable, plotKwds={}):
    """this is an image plot for irregularly spaced data
    """
    from matplotlib.mlab import griddata
    #from plotlib.mlab import griddata
    qs,yAxiss,scatFuncs = plottable.createPoints()
    
    # define grid.
    try:
        xDivisions = plotKwds.pop('xDivisions')
    except:
        xDivisions = 100
    try:
        yDivisions = plotKwds.pop('yDivisions')
    except:
        yDivisions = 100
    qi = np.linspace(min(qs), max(qs), xDivisions)
    yAxisi = np.linspace(min(yAxiss), max(yAxiss), yDivisions)
    
    # Normalize coordinate system
    def normalize(data):
        data = data.astype(np.float)
        return (data - min(data)) / (max(data) - min(data))
    
    qs_new, qi_new = normalize(qs), normalize(qi)
    yAxiss_new, yAxisi_new = normalize(yAxiss), normalize(yAxisi)
    
    # grid the data.
    scatFunci = griddata(qs_new, yAxiss_new, scatFuncs, qi_new, yAxisi_new)
    #scatFunci = griddata(plottable.q, plottable.yAxis, plottable.scatFunc, qi, yAxisi)
    if hasattr(plottable, 'clip'):
        scatFunci = np.clip(scatFunci, plottable.clip[0], plottable.clip[1])
    # contour the gridded data, plotting dots at the randomly spaced data points.
    try:
        numIntervals = plotKwds.pop('numIntervals')
    except:
        numIntervals = 15
    #CS = self.contour(qi, yAxisi, scatFunci, levels, linewidths=0.5, colors='k')
#            vmin = np.min(scatFunci)
#            vmin = 0.0
#            vmax = np.max(scatFunci)
#            vmax = 0.005
#            norm = colors.Normalize(vmin=vmin, vmax=vmax)

    # we don't want to mask like below but cap values with
    # certain limits
#            import numpy.ma as ma
#            scatFuncm = ma.masked_outside(scatFunci, 0.095, 0.1)   

    CS = plottable.contourf(qi, yAxisi, scatFunci, numIntervals, 
        cmap=plottable.cm.jet, extend = 'both', **plotKwds)
        #norm = norm, **plotKwds)
    plottable.title(plottable.sfLabel)
    plottable.xlabel("Q (1/Ang)")
    plottable.ylabel(plottable.yLabel)
    try:
        bar = plotKwds.pop('bar')
        if bar:
            plottable.colorbar()
    except:
        plottable.colorbar()
    # axes
    #ax.set_ylim(0., 1.)

def points3d(plottable, plotKwds={}):
    if plottable.fileType=='grid':
        q = plottable.q
        y = plottable.yAxis
        scatFunc = plottable.scatFunc
        # set axes limits
        if plotKwds.has_key('ranges'):
            ranges = plotKwds['ranges']
            qMinInd = np.where(q > ranges[0])[0][0]
            qMaxInd = np.where(q < ranges[1])[0][-1]
            yMinInd = np.where(y > ranges[2])[0][0]
            yMaxInd = np.where(y < ranges[3])[0][-1]
        else:
            qMinInd, qMaxInd = (0, len(q)-1)
            yMinInd, yMaxInd = (0, len(y)-1)
            ranges = [np.min(q), np.max(q), y[0], y[-1],
                             np.min(scatFunc), np.max(scatFunc)]
        
        numPoints = (qMaxInd+1 - qMinInd)*(yMaxInd+1 - yMinInd) #this includes many zero points...needs to be fixed
        xs = np.zeros(numPoints)
        ys = np.zeros(numPoints)
        zs = np.zeros(numPoints)
        ind=0
        for i in range(qMinInd, qMaxInd+1):#q
            for j in range(yMinInd, yMaxInd+1):#energy, frequency
                if scatFunc[i,j]>ranges[5] or scatFunc[i,j]<ranges[4]:
                    pass
                else:
                    xs[ind] = q[i]
                    ys[ind] = y[j]
                    zs[ind] = scatFunc[i,j]
                    ind+=1
    else:
        xs = plottable.points[0]
        ys = plottable.points[1]
        zs = plottable.points[2]
        ranges = [np.min(xs), np.max(xs), np.min(ys), np.max(ys),
                         np.min(zs), np.max(zs)]

    # use the engine
    extentTuplet = (0, 1, 0, 1, 0, 1)
    pic = plottable.points3d(xs, ys, zs, mode = '2dcircle', 
                            colormap = 'gist_earth',
                            scale_factor=0.01,# warp_scale=0.3,
                            extent=extentTuplet)
    plottable.axes(pic, xlabel="Q (1/Ang)", ylabel=plottable.yLabel, 
                  zlabel=plottable.sfLabel, extent=extentTuplet,
                  ranges=ranges)
    plottable.outline(pic, extent=extentTuplet)
    plottable.colorbar()
    
def simplePoints3d(plottable, xs=None, ys=None, zs=None, plotKwds={}):
#    # set axes limits 
#    if plotKwds.has_key('ranges'):
#        ranges = plotKwds['ranges']
#        qMinInd = np.where(q > ranges[0])[0][0]
#        qMaxInd = np.where(q < ranges[1])[0][-1]
#        yMinInd = np.where(y > ranges[2])[0][0]
#        yMaxInd = np.where(y < ranges[3])[0][-1]
#    else:
#        qMinInd, qMaxInd = (0, len(q)-1)
#        yMinInd, yMaxInd = (0, len(y)-1)
#        ranges = [np.min(q), np.max(q), y[0], y[-1],
#                         np.min(scatFunc), np.max(scatFunc)]
#    
#    numPoints = (qMaxInd+1 - qMinInd)*(yMaxInd+1 - yMinInd) #this includes many zero points...needs to be fixed
#    xs = np.zeros(numPoints)
#    ys = np.zeros(numPoints)
#    zs = np.zeros(numPoints)
#    ind=0
#    for i in range(qMinInd, qMaxInd+1):#q
#        for j in range(yMinInd, yMaxInd+1):#energy, frequency
#            if scatFunc[i,j]>ranges[5] or scatFunc[i,j]<ranges[4]:
#                pass
#            else:
#                xs[ind] = q[i]
#                ys[ind] = y[j]
#                zs[ind] = scatFunc[i,j]
#                ind+=1

    ranges = [np.min(xs), np.max(xs), np.min(ys), np.max(ys),
                         np.min(zs), np.max(zs)]

    # use the engine
    extentTuplet = (0 , 1, 0, 1, 0, 1)
    pic = plottable.points3d(xs, ys, zs, mode = '2dcircle', 
                            colormap = 'gist_earth',
                            scale_factor=0.01,# warp_scale=0.3,
                            extent=extentTuplet)
    plottable.axes(pic, xlabel="Q (1/Ang)", ylabel=plottable.yLabel, 
                  zlabel=plottable.sfLabel, extent=extentTuplet,
                  ranges=ranges)
    plottable.outline(pic, extent=extentTuplet)
    plottable.colorbar()