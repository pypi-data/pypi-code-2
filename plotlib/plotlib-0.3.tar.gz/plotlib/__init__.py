def plot(*args):
    for item in args:
        decideObject(item)

def decideObject(obj):
    x = y = [0.0]
    from vsat.MotionDos import MotionDos
    if isinstance(obj, MotionDos):
        x,y = obj.getXY()
        plt.plot(x,y)
    from plotlib.Line import Line
    if isinstance(obj, Line):
        x,y = obj.getXY()
    plt.plot(x,y)
    plt.show()
    return  

def plotSqe(arg, **kwds):
    if type(arg)==type([]):
        from NcPlottableSet import NcPlottableSet
        return NcPlottableSet(arg,  **kwds)
    if type(arg)==type(''):
        from NcPlottableSet import NcPlottableSet
        return NcPlottableSet(arg,  **kwds)