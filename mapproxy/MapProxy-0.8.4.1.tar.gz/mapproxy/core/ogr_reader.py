# This file is part of the MapProxy project.
# Copyright (C) 2010 Omniscale <http://omniscale.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mapproxy.core.libutils import load_library
import ctypes
from ctypes import c_void_p, c_char_p, c_int

def init_libgdal():
    libgdal = load_library('libgdal')
    
    if not libgdal: return
    
    libgdal.OGROpen.argtypes = [c_char_p, c_int, c_void_p]
    libgdal.OGROpen.restype = c_void_p

    libgdal.CPLGetLastErrorMsg.argtypes	= []
    libgdal.CPLGetLastErrorMsg.restype = c_char_p

    libgdal.OGR_DS_GetLayer.argtypes = [c_void_p, c_int]
    libgdal.OGR_DS_GetLayer.restype = c_void_p

    libgdal.OGR_FD_GetName.argtypes = [c_void_p]
    libgdal.OGR_FD_GetName.restype = c_char_p

    libgdal.OGR_L_GetLayerDefn.argtypes = [c_void_p]
    libgdal.OGR_L_GetLayerDefn.restype = c_void_p

    libgdal.OGR_DS_Destroy.argtypes = [c_void_p]

    libgdal.OGR_DS_ExecuteSQL.argtypes = [c_void_p, c_char_p, c_void_p, c_char_p]
    libgdal.OGR_DS_ExecuteSQL.restype = c_void_p
    libgdal.OGR_DS_ReleaseResultSet.argtypes = [c_void_p, c_void_p]

    libgdal.OGR_L_ResetReading.argtypes = [c_void_p]
    libgdal.OGR_L_GetNextFeature.argtypes = [c_void_p]
    libgdal.OGR_L_GetNextFeature.restype = c_void_p

    libgdal.OGR_F_Destroy.argtypes = [c_void_p]

    libgdal.OGR_F_GetGeometryRef.argtypes = [c_void_p]
    libgdal.OGR_F_GetGeometryRef.restype = c_void_p

    libgdal.OGR_G_ExportToWkt.argtypes = [c_void_p, ctypes.POINTER(c_char_p)]
    libgdal.OGR_G_ExportToWkt.restype = c_void_p

    libgdal.VSIFree.argtypes = [c_void_p]

    libgdal.OGRRegisterAll()
    
    return libgdal

libgdal = init_libgdal()

class OGRShapeReaderError(Exception):
    pass

class OGRShapeReader(object):
    def __init__(self, datasource, where=None):
        self.datasource = datasource
        self.opened = False
        self._ds = None
        
    def open(self):
        if self.opened: return
        self._ds = libgdal.OGROpen(self.datasource, False, None)
        if self._ds is None:
            msg = libgdal.CPLGetLastErrorMsg()
            if not msg:
                msg = 'failed to open %s' % self.datasource
            raise OGRShapeReaderError(msg)

    def wkts(self, where=None):
        if not self.opened: self.open()
        
        if where:
            if not where.lower().startswith('select'):
                layer = libgdal.OGR_DS_GetLayer(self._ds, 0)
                layer_def = libgdal.OGR_L_GetLayerDefn(layer)
                name = libgdal.OGR_FD_GetName(layer_def)
                where = 'select * from %s where %s' % (name, where)
            layer = libgdal.OGR_DS_ExecuteSQL(self._ds, where, None, None)
        else:
            layer = libgdal.OGR_DS_GetLayer(self._ds, 0)
        if layer is None:
            msg = libgdal.CPLGetLastErrorMsg()
            raise OGRShapeReaderError(msg)
        
        libgdal.OGR_L_ResetReading(layer)
        while True:
            feature = libgdal.OGR_L_GetNextFeature(layer)
            if feature is None:
                break
            geom = libgdal.OGR_F_GetGeometryRef(feature)
            res = c_char_p()
            libgdal.OGR_G_ExportToWkt(geom, ctypes.byref(res))
            yield res.value
            libgdal.VSIFree(res)
            libgdal.OGR_F_Destroy(feature)
        
        if where:
            libgdal.OGR_DS_ReleaseResultSet(self._ds, layer)
    
    def close(self):
        if self.opened:
            libgdal.OGR_DS_Destroy(self._ds)
            self.opened = False
    
    def __del__(self):
        self.close()
        
if __name__ == '__main__':
    import sys
    reader = OGRShapeReader(sys.argv[1])
    where = None
    if len(sys.argv) == 3:
        where = sys.argv[2]
    for wkt in reader.wkts(where):
        print wkt