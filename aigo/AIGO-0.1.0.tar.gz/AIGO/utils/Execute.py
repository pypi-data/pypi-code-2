from AIGO.Statistics import registerStat as rS
from AIGO.Analyse import AnalyseFA


def batchExecute(lFunc, effector, *args, **kargs):
    for func in lFunc:
        if hasattr(effector, func):
            if isinstance (effector, AnalyseFA) and not rS.isRegistered(func):
                print "Warning, call of an unregistered statistics : %s"  % func
                
            getattr(effector, func)(*args, **kargs)
