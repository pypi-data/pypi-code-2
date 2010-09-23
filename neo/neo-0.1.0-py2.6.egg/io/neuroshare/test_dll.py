

import ctypes
from ctypes import byref, c_char_p, c_uint32, c_char, c_double, c_int16, c_int32 , c_ulong
from numpy import *


dllname = 'NSCEDSON'
#dllname = 'nsAOLibrary'

#ctypes.cdll.LoadLibrary(dllname)
#neuroshare = ctypes.CDLL(dllname)

neuroshare = ctypes.windll.LoadLibrary(dllname)
#neuroshare = ctypes.CDLL(dllname)


print dir(neuroshare)

filename = 'File_spike2_1.smr'
#fid = open(filename)
#print fid.fileno()


#
#typedef struct {
#uint32 dwLibVersionMaj;
#uint32 dwLibVersionMin;
#uint32 dwAPIVersionMaj;
#uint32 dwAPIVersionMin;
#char szDescription[64];
#char szCreator[64];
#uint32 dwTime_Year;
#uint32 dwTime_Month;
#uint32 dwTime_Day;
#uint32 dwFlags;
#uint32 dwMaxFiles
#uint32 dwFileDescCount;
#ns_FILEDESC FileDesc[16];
#} ns_LIBRARYINFO;
class ns_LIBRARYINFO(ctypes.Structure):
    _fields_ = [('dwLibVersionMaj', c_uint32),
                ('dwLibVersionMin', c_uint32),
                ('dwAPIVersionMaj', c_uint32),
                ('dwAPIVersionMin', c_uint32),
                ('szDescription', c_char*64),
                ('szCreator',c_char*64),
                ('dwTime_Year',c_uint32),
                ('dwTime_Month',c_uint32),
                ('dwTime_Day',c_uint32),
                ('dwFlags',c_uint32),
                ('dwMaxFiles',c_uint32),
                ('dwFileDescCount',c_uint32),
                ('FileDesc',c_uint32*16),
                ]

info = ns_LIBRARYINFO()
neuroshare.ns_GetLibraryInfo(byref(info) , ctypes.sizeof(info))
print 'API ver' , info.dwAPIVersionMaj, '.',info.dwAPIVersionMin

hFile = c_uint32(0)
neuroshare.ns_OpenFile(c_char_p(filename) ,byref(hFile))
print 'hFile',hFile


#typedef struct {
#char szFileType[32];
#uint32 dwEntityCount;
#double dTimeStampResolution
#double dTimeSpan;
#char szAppName[64];
#uint32 dwTime_Year;
#uint32 dwTime_Month;
#uint32 dwReserved;
#uint32 dwTime_Day;
#uint32 dwTime_Hour;
#uint32 dwTime_Min;
#uint32 dwTime_Sec;
#uint32 dwTime_MilliSec;
#char szFileComment[256];
#} ns_FILEINFO;

class ns_FILEINFO(ctypes.Structure):
    _fields_ = [('szFileType', c_char*32),
                ('dwEntityCount', c_uint32),
                ('dTimeStampResolution', c_double),
                ('dTimeSpan', c_double),
                ('szAppName', c_char*64),
                ('dwTime_Year',c_uint32),
                ('dwTime_Month',c_uint32),
                ('dwReserved',c_uint32),
                ('dwTime_Day',c_uint32),
                ('dwTime_Hour',c_uint32),
                ('dwTime_Min',c_uint32),
                ('dwTime_Sec',c_uint32),
                ('dwTime_MilliSec',c_uint32),
                ('szFileComment',c_char*256),
                ]
fileinfo = ns_FILEINFO()

neuroshare.ns_GetFileInfo(hFile, byref(fileinfo) , ctypes.sizeof(fileinfo))
print fileinfo.szFileComment
print fileinfo.szFileType
print fileinfo.dTimeStampResolution
print fileinfo.dwEntityCount

#typedef struct {
#char szEntityLabel[32];
#uint32 dwEntityType;
#uint32 dwItemCount;

#} ns_ENTITYINFO;
class ns_ENTITYINFO(ctypes.Structure):
    _fields_ = [('szEntityLabel', c_char*32),
                ('dwEntityType',c_uint32),
                ('dwItemCount',c_uint32),
                ]
    
entity_types = { 0 : 'ns_ENTITY_UNKNOWN' ,
                    1 : 'ns_ENTITY_EVENT' ,
                    2 : 'ns_ENTITY_ANALOG' ,
                    3 : 'ns_ENTITY_SEGMENT' ,
                    4 : 'ns_ENTITY_NEURALEVENT' ,
                    }

#typedef struct {
#uint32 dwEventType;
#uint32 dwMinDataLength;
#uint32 dwMaxDataLength;
#char szCSVDesc [128];
#} ns_EVENTINFO;

class ns_EVENTINFO(ctypes.Structure):
    _fields_ = [
                ('dwEventType',c_uint32),
                ('dwMinDataLength',c_uint32),
                ('dwMaxDataLength',c_uint32),
                ('szCSVDesc', c_char*128),
                ]


#typedef struct{
#double dSampleRate;
#double dMinVal;
#double dMaxVal;
#char szUnits[16];
#double dResolution;
#double dLocationX;
#double dLocationY;
#double dLocationZ;
#double dLocationUser;
#double dHighFreqCorner;
#uint32 dwHighFreqOrder;
#char szHighFilterType[16];
#double dLowFreqCorner;
#uint32 dwLowFreqOrder;
#char szLowFilterType[16];
#char szProbeInfo[128];
#} ns_ANALOGINFO;


class ns_ANALOGINFO(ctypes.Structure):
    _fields_ = [
                ('dSampleRate',c_double),
                ('dMinVal',c_double),
                ('dMaxVal',c_double),
                ('szUnits', c_char*16),
                ('dResolution',c_double),
                ('dLocationX',c_double),
                ('dLocationY',c_double),
                ('dLocationZ',c_double),
                ('dLocationUser',c_double),
                ('dHighFreqCorner',c_double),
                ('dwHighFreqOrder',c_uint32),
                ('szHighFilterType', c_char*16),
                ('dLowFreqCorner',c_double),
                ('dwLowFreqOrder',c_uint32),
                ('szLowFilterType', c_char*16),
                ('szProbeInfo', c_char*128),
            ]

#typedef struct {
#uint32 dwSourceCount;
#uint32 dwMinSampleCount;
#uint32 dwMaxSampleCount;
#double dSampleRate;
#char szUnits[32];
#} ns_SEGMENTINFO;

class ns_SEGMENTINFO(ctypes.Structure):
    _fields_ = [
                ('dwSourceCount',c_uint32),
                ('dwMinSampleCount',c_uint32),
                ('dwMaxSampleCount',c_uint32),
                ('dSampleRate',c_double),
                ('szUnits', c_char*32),
                ]


#ns_SEGSOURCEINFO
#typedef struct {
#double dMinVal;
#double dMaxVal;
#double dResolution;
#double dSubSampleShift;
#double dLocationX;
#double dLocationY;
#double dLocationZ;
#double dLocationUser;
#double dHighFreqCorner;
#uint32 dwHighFreqOrder;
#char szHighFilterType[16];
#double dLowFreqCorner;
#uint32 dwLowFreqOrder;
#char szLowFilterType[16];
#char szProbeInfo[128];
#} ns_SEGSOURCEINFO;


class ns_SEGSOURCEINFO(ctypes.Structure):
    _fields_ = [
                ('dMinVal',c_double),
                ('dMaxVal',c_double),
                ('dResolution',c_double),
                ('dSubSampleShift',c_double),
                ('dLocationX',c_double),
                ('dLocationY',c_double),
                ('dLocationZ',c_double),
                ('dLocationUser',c_double),
                ('dHighFreqCorner',c_double),
                ('dwHighFreqOrder',c_uint32),
                ('szHighFilterType', c_char*16),
                ('dLowFreqCorner',c_double),
                ('dwLowFreqOrder',c_uint32),
                ('szLowFilterType', c_char*16),
                ('szProbeInfo', c_char*128),                
                ]

#typedef struct {
#uint32 dwSourceEntityID;
#uint32 dwSourceUnitID;
#char szProbeInfo[128];
#} ns_NEURALINFO;

class ns_SEGSOURCEINFO(ctypes.Structure):
    _fields_ = [
                ('dwSourceEntityID',c_uint32),
                ('dwSourceUnitID',c_uint32),
                ('szProbeInfo',c_char*128),
                ]







for dwEntityID in range(fileinfo.dwEntityCount):
    print 'dwEntityID' , dwEntityID
    entityInfo = ns_ENTITYINFO()
    neuroshare.ns_GetEntityInfo( hFile, dwEntityID,
                                byref(entityInfo), ctypes.sizeof(entityInfo))
    print 'type', entityInfo.dwEntityType,entity_types[entityInfo.dwEntityType], 'count', entityInfo.dwItemCount
    
    # EVENT
    if entity_types[entityInfo.dwEntityType] == 'ns_ENTITY_EVENT': 
        pEventInfo = ns_EVENTINFO()
        neuroshare.ns_GetEventInfo ( hFile,  dwEntityID, 
                                    byref(pEventInfo), ctypes.sizeof(pEventInfo))
        print pEventInfo.szCSVDesc, pEventInfo.dwEventType, pEventInfo.dwMinDataLength, pEventInfo.dwMaxDataLength
        
        if pEventInfo.dwEventType == 0: #TEXT
            pData = ctypes.create_string_buffer(pEventInfo.dwMaxDataLength)
        elif pEventInfo.dwEventType == 1:#CVS
            pData = ctypes.create_string_buffer(pEventInfo.dwMaxDataLength)
        elif pEventInfo.dwEventType == 2:# 8bit
            pData = ctypes.c_byte(0)
        elif pEventInfo.dwEventType == 3:# 16bit
            pData = ctypes.c_int16(0)
        elif pEventInfo.dwEventType == 4:# 32bit
            pData = ctypes.c_int32(0)
        pdTimeStamp  = c_double(0.)
        pdwDataRetSize = c_uint32(0)
        for dwIndex in range(entityInfo.dwItemCount ):
            neuroshare.ns_GetEventData ( hFile, dwEntityID, dwIndex,
                                byref(pdTimeStamp), byref(pData),
                                ctypes.sizeof(pData), byref(pdwDataRetSize) )
            #print 'dwIndex' , dwIndex , pdTimeStamp, pData , pdwDataRetSize

    # analog
    if entity_types[entityInfo.dwEntityType] == 'ns_ENTITY_ANALOG': 
        pAnalogInfo = ns_ANALOGINFO()
        neuroshare.ns_GetAnalogInfo( hFile, dwEntityID,
                                byref(pAnalogInfo),
                                ctypes.sizeof(pAnalogInfo) )
        print 'dSampleRate' , pAnalogInfo.dSampleRate , pAnalogInfo.szUnits
        dwStartIndex = c_uint32(0)
        dwIndexCount = entityInfo.dwItemCount
        dwIndexCount = 999
        # FIXME
        pdwContCount = c_uint32(0)
        pData = zeros( (entityInfo.dwItemCount,), dtype = 'f4')
        neuroshare.ns_GetAnalogData ( hFile,  dwEntityID,  dwStartIndex,
                         dwIndexCount, byref( pdwContCount) , pData.ctypes.data)
        print 'pdwContCount', pdwContCount, dwIndexCount
        sig = pData[:pdwContCount.value]
        print sig.shape
        
    
    #segment
    if entity_types[entityInfo.dwEntityType] == 'ns_ENTITY_SEGMENT': 
        
        pdwSegmentInfo = ns_SEGMENTINFO()
        neuroshare.ns_GetSegmentInfo( hFile,  dwEntityID,
                                         byref(pdwSegmentInfo), ctypes.sizeof(pdwSegmentInfo) )
        print 'pdwSegmentInfo.dwSourceCount' , pdwSegmentInfo.dwSourceCount
        for dwSourceID in range(pdwSegmentInfo.dwSourceCount) :
            pSourceInfo = ns_SEGSOURCEINFO()
            neuroshare.ns_GetSegmentSourceInfo( hFile,  dwEntityID, dwSourceID,
                            byref(pSourceInfo), ctypes.sizeof(pSourceInfo) )
        
        pdTimeStamp  = c_double(0.)
        pData = zeros( (pdwSegmentInfo.dwMaxSampleCount), dtype = 'f4')
        dwDataBufferSize = pdwSegmentInfo.dwMaxSampleCount
        pdwSampleCount = c_uint32(0)
        pdwUnitID= c_uint32(0)
        for dwIndex in range(entityInfo.dwItemCount ):
            neuroshare.ns_GetSegmentData ( hFile,  dwEntityID,  dwIndex,
                    byref(pdTimeStamp), pData.ctypes.data,
                     dwDataBufferSize, byref(pdwSampleCount),
                    byref(pdwUnitID ) )
            #print 'dwDataBufferSize' , dwDataBufferSize,pdwSampleCount , pdwUnitID
            nsample ,nsource = pdwSampleCount.value,pdwSegmentInfo.dwSourceCount
            waveform = pData[:nsample].reshape(nsample/nsource ,nsource)
            #print waveform.shape
            

    # neuralevent
    if entity_types[entityInfo.dwEntityType] == 'ns_ENTITY_NEURALEVENT': 
        
        pNeuralInfo = ns_SEGSOURCEINFO()
        
        neuroshare.ns_GetNeuralInfo ( hFile,  dwEntityID,
                         byref(pNeuralInfo), ctypes.sizeof(pNeuralInfo))
        print pNeuralInfo.dwSourceUnitID
        pData = zeros( (entityInfo.dwItemCount,), dtype = 'f4')
        dwStartIndex = 0
        dwIndexCount = entityInfo.dwItemCount
        neuroshare.ns_GetNeuralData( hFile,  dwEntityID,  dwStartIndex,
                                         dwIndexCount,  pData.ctypes.data)
        print pData.shape
        



    
    
    
    

neuroshare.ns_CloseFile(hFile)





