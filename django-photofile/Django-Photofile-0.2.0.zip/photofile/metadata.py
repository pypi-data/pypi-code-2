#coding=utf-8
import os
import time
import datetime
import re
import Image
from PIL.ExifTags import TAGS

try:
    import pyexiv2
    PYEXIV2_SUPPORT = True
except ImportError:
    PYEXIV2_SUPPORT = False


# http://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def ExtractMakeAndModel(data):
    "Extracts make and model from data produced by pyexiv2."    
    make = data.get('Exif.Image.Make', None)
    model = data.get('Exif.Image.Model', None)
    if make and model:
        return make.value, model.value
    return None, None

def ExtractLocationData(data):
    try: location_name = ', '.join(data['Iptc.Application2.LocationName'].values)
    except: location_name = None
    try: city = ', '.join(data['Iptc.Application2.City'].values)
    except: city = None
    try: province_state = ', '.join(data['Iptc.Application2.ProvinceState'].values)
    except: province_state = None
    try: country_code = ', '.join(data['Iptc.Application2.CountryCode'].values)
    except: country_code = None
    try: country_name = ', '.join(data['Iptc.Application2.CountryName'].values)
    except KeyError: country_name = None
    return location_name, city, province_state, country_code, country_name

def ExtractGPSInfo(data):
    "Extracts longitude, latitude and altitude from data produced by pyexiv2."
    # http://linfiniti.com/2009/06/reading-geotagging-data-from-blackberry-camera-images/
    myLonDirection = None
    myLonDegrees = None
    myLonMinutes = None
    myLatDirection = None
    myLatDegrees = None
    myLatMinutes = None
    try:
        # Will be either 'E' or 'W'
        myLonDirection = data['Exif.GPSInfo.GPSLongitudeRef']
        # Will return a rational number like : '27/1'
        myLonDegrees = data['Exif.GPSInfo.GPSLongitude'][0]
        # Will return a rational number like : '53295/1000'
        myLonMinutes = data['Exif.GPSInfo.GPSLongitude'][1]
        # Will be either 'N' or 'S'
        myLatDirection = data['Exif.GPSInfo.GPSLatitudeRef']
        # Will return a rational number like : '27/1'
        myLatDegrees = data['Exif.GPSInfo.GPSLatitude'][0]
        # Will return a rational number like : '56101/1000'
        myLatMinutes = data['Exif.GPSInfo.GPSLatitude'][1]
    except:
        return (None, None, None)

    # Get the degree and minute values

    myRegexp = re.compile( '^[0-9]*' )
    myLonDegreesFloat = float(myRegexp.search( str(myLonDegrees) ).group())
    myLatDegreesFloat = float(myRegexp.search( str(myLatDegrees) ).group())
    myLonMinutesFloat = float(myRegexp.search( str(myLonMinutes) ).group())
    myLatMinutesFloat = float(myRegexp.search( str(myLatMinutes) ).group())

    # Divide the values by the divisor 

    myRegexp = re.compile( '[0-9]*$' )
    myLon = myLonDegreesFloat / float(myRegexp.search( str(myLonDegrees) ).group())
    myLat = myLatDegreesFloat / float(myRegexp.search( str(myLatDegrees) ).group())
    myLonMin = myLonMinutesFloat / float(myRegexp.search( str(myLonMinutes) ).group())
    myLatMin = myLatMinutesFloat / float(myRegexp.search( str(myLatMinutes) ).group())

    # We now have degrees and decimal minutes, so convert to decimal degrees...

    myLon = myLon + (myLonMin / 60)
    myLat = myLat + (myLatMin / 60)

    # Use a negative sign as needed

    if myLonDirection == 'W': myLon = 0 - myLon
    if myLatDirection == 'S': myLat = 0 - myLat

    try:
        altitude = data['Exif.GPSInfo.GPSAltitude'][0]
    except:
        altitude = None

    print myLon, myLat, altitude
    return (myLon, myLat, altitude)

def exiv2ToDict(metadata):
    result = {}
    keys = metadata.exif_keys
    keys.extend(metadata.iptc_keys)
    keys.extend(metadata.xmp_keys)
    for key in keys:
        result[key] = metadata[key]
    return result

def prettyPrintexiv2(metadata):
    result = {}
    for k,v in metadata.items():
        if hasattr(v, 'values'):
            result[k] = ' '.join(v.values)
        else:
            result[k] = str(v.value)
    return result

def ExtractPhotoMetadata(filename):
    """
    """
    if not PYEXIV2_SUPPORT:
        return {}
    
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    result = exiv2ToDict(metadata)
    result['width'], result['height'] = metadata.dimensions
    return result

def get_metadata(filename):
    def _fractToSimple(frac):
        if not frac:
            return None
        try:
            f,n = frac
            return round(float(f) / float(n), 1)
        except:
            return None            
           
    result = {
        'camera_model': None,
        'orientation': None,
        'exposure_time': None,
        'fnumber': None,
        'exposure_program': None,
        'iso_speed': None,
        'metering_mode': None,
        'light_source': None,
        'flash_used': None,
        'focal_length': None,
        'longitude': None,
        'latitude': None,
        'altitude': None,
        'exposure_mode': None,
        'whitebalance': None,
        'focal_length_in_35mm': None,
        'width': None,
        'height': None
        }

    try:
        metadata = get_exif(filename)
        tm = time.strptime(metadata['DateTime'],"%Y:%m:%d %H:%M:%S")
        result['exif_date'] = datetime.datetime.fromtimestamp(time.mktime(tm))
        result['camera_model'] = metadata.get("Model", None)
        result['orientation'] = metadata.get("Orientation", None)
        result['exposure_time'] = _fractToSimple(metadata.get("ExposureTime", None))
        result['fnumber'] = _fractToSimple(metadata.get("FNumber", None))
        result['exposure_program'] = metadata.get("ExposureProgram", None)
        result['iso_speed'] = metadata.get("ISOSpeedRatings", None)
        result['metering_mode'] = metadata.get("MeteringMode", None)
        result['light_source'] = metadata.get("LightSource", None)
        result['flash_used'] = metadata.get("Flash", None)
        result['focal_length'] = _fractToSimple(metadata.get("FocalLength", None))
        result['width'] = metadata.get('ExifImageWidth', None)
        result['height'] = metadata.get('ExifImageHeight', None)        
        #longitude, latitude, altitude = ExtractGPSInfo(metadata)
        #result['longitude'] = longitude
        #result['latitude'] = latitude
        #result['altitude'] = altitude
        #result['exposure_mode'] = metadata.get("Exif.Photo.ExposureMode", None)
        #result['whitebalance'] = metadata.get("Exif.Photo.WhiteBalance", None)
        #result['focal_length_in_35mm'] = metadata.get("Exif.Photo.FocalLengthIn35mmFilm", None)

        # 'GPSInfo', ''MakerNote','DateTimeDigitized',
        # 'DateTimeOriginal', 'UserComment', 'SceneType', 'Software', 'MaxApertureValue',
    except Exception, e:
        if PYEXIV2_SUPPORT:
            try:
                metadata = ExtractPhotoMetadata(filename)
                try:
                    result['exif_date'] = metadata['Exif.Image.DateTime'].value
                except:
                    result['exif_date'] = datetime.datetime.fromtimestamp(os.stat(filename).st_ctime)
                result['camera_model'] = metadata.get("Exif.Image.Model", None)
                result['orientation'] = metadata.get("Exif.Image.Orientation", None)
                if result['orientation']:
                    result['orientation'] = result['orientation'].value
                result['exposure_time'] = metadata.get("Exif.Photo.ExposureTime", None)
                result['fnumber'] = metadata.get("Exif.Photo.FNumber", None)
                result['exposure_program'] = metadata.get("Exif.Photo.ExposureProgram", None)
                result['iso_speed'] = metadata.get("Exif.Photo.ISOSpeedRatings", None)
                result['metering_mode'] = metadata.get("Exif.Photo.MeteringMode", None)
                result['light_source'] = metadata.get("Exif.Photo.LightSource", None)
                result['flash_used'] = metadata.get("Exif.Photo.Flash", None)
                result['focal_length'] = metadata.get("Exif.Photo.FocalLength", None)
                longitude, latitude, altitude = ExtractGPSInfo(metadata)
                result['longitude'] = longitude
                result['latitude'] = latitude
                result['altitude'] = altitude
                result['exposure_mode'] = metadata.get("Exif.Photo.ExposureMode", None)
                result['whitebalance'] = metadata.get("Exif.Photo.WhiteBalance", None)
                result['focal_length_in_35mm'] = metadata.get("Exif.Photo.FocalLengthIn35mmFilm", None)
                result['width'] = metadata.get('ExifImageWidth', None)
                result['height'] = metadata.get('ExifImageHeight', None)
            except Exception, e:
                pass #print "Error using pyexiv for %s" % filename, e
    if not 'exif_date' in result:
        result['exif_date'] = datetime.datetime.fromtimestamp(os.stat(filename).st_ctime)
    return result                 
