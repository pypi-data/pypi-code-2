from StringIO import StringIO

import numpy
from scipy.io import savemat

from pydap.model import *
from pydap.lib import walk
from pydap.responses.lib import BaseResponse


class MatlabResponse(BaseResponse):

    __description__ = "Matlab v5 file"

    def __init__(self, dataset):
        BaseResponse.__init__(self, dataset)
        self.headers.extend([
                ('Content-description', 'dods_matlab'),
                ('Content-type', 'application/x-matlab'),
                ])

    @staticmethod
    def serialize(dataset):
        buf = StringIO()
        mdict = {}

        # Global attributes.
        nc_global = dataset.attributes.pop('NC_GLOBAL', {})
        for k, v in nc_global.items():
            if not isinstance(v, dict):
                mdict[k] = v
        for k, v in dataset.attributes.items():
            if not isinstance(v, dict):
                mdict[k] = v
        
        # Gridded data.
        for grid in walk(dataset, GridType):
            # Add dimensions.
            for dim, map_ in grid.maps.items():
                if dim not in mdict:
                    mdict[map_.id] = map_[:]
                    for k, v in map_.attributes.items():
                        if not isinstance(v, dict):
                            mdict['%s:%s' % (map_.id, k)] = v
            # Add the var.
            mdict[grid.id] = grid.array[:]
            for k, v in grid.attributes.items():
                if not isinstance(v, dict):
                    mdict['%s:%s' % (grid.id, k)] = v

        # Sequences.
        for seq in walk(dataset, SequenceType):
            # Add vars.
            for child in seq.walk():
                mdict[child.id] = numpy.fromiter(child.data, child.type.typecode)
                for k, v in child.attributes.items():
                    if not isinstance(v, dict):
                        mdict['%s:%s' % (child.id, k)] = v

        savemat(buf, mdict)
        return [ buf.getvalue() ]
                    

def save(dataset, filename):
    f = open(filename, 'w')
    f.write(MatlabResponse(dataset).serialize(dataset)[0])
    f.close()


if __name__ == '__main__':
    import numpy

    dataset = DatasetType(name='foo', attributes={'history': 'Test file created by Matlab response', 'version': 1.0})
    
    dataset['grid'] = GridType(name='grid')
    data = numpy.arange(6)
    data.shape = (2,3)
    dataset['grid']['array'] = BaseType(data=data, name='array', shape=data.shape, type=data.dtype.char)
    x, y = numpy.arange(2), numpy.arange(3) * 10
    dataset['grid']['x'] = BaseType(name='x', data=x, shape=x.shape, type=x.dtype.char, attributes={'units': 'm/s'})
    dataset['grid']['y'] = BaseType(name='y', data=y, shape=y.shape, type=y.dtype.char, attributes={'units': 'degC'})

    seq = dataset['seq'] = SequenceType(name='seq')
    seq['xval'] = BaseType(name='xval', type=Int16)
    seq['xval'].attributes['units'] = 'meters per second'
    seq['yval'] = BaseType(name='yval', type=Int16)
    seq['yval'].attributes['units'] = 'kilograms per minute'
    seq['zval'] = BaseType(name='zval', type=Int16)
    seq['zval'].attributes['units'] = 'tons per hour'
    seq.data = [(1, 2, 1), (2, 4, 4), (3, 6, 9), (4, 8, 16)]

    dataset._set_id()

    save(dataset, 'test.mat')
