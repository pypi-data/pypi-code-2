# -*- coding: utf-8 -*-

import numpy

import quantities as pq

import numpy as np

print pq.V

q = np.array([1,2,3]) * pq.V

q = [1,2,3] * pq.V
print q

q = pq.Quantity([1,2,3])
print q



class Base(object):
    neoattr = [ ]
    def __init__(self , *args, **kargs):
        print 'ici'
        metadata = { }
        metadata.update(kargs)
        setattr(self, 'metadata' , metadata)
        #~ for k , v in kargs.iteritems():
            #~ if k in self.neoattr:
                #~ setattr(self, k, v)
    
    def __setattr__(self, k, v):
        if k in  self.neoattr :
            self.metadata[k] = v
    
    def __getattr__(self, k):
        print 'k' , k
        if k in getattr(self, 'metadata'):
            return getattr(self, 'metadata')[k]
        else:
            None
    
    


class AnalogSignal(pq.Quantity , Base):
    neoattr = [
                    'signal',
                    'sampling_rate',
                    't_start',
                    'channel',
                    'name',
                    'units',
                    ]
    
    def __init__(self , *args, **kargs):
        #~ pq.Quantity.__init__(self, *args, **kargs)
        
        Base.__init__(self , *args, **kargs)
        
        if 'units' in kargs:
            self._set_units( kargs['units'])
        

q = AnalogSignal([1,2,3] , units = '')
print q

print q.units

