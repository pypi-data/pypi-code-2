# -*- coding: utf-8 -*-
import urllib
import json
from collections import namedtuple

YANDEX_GEO_URL = 'http://geocode-maps.yandex.ru/1.x/'

class GeoError(Exception):
    pass


class Country(object):
    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<Country: %s>' % str(self)


Position = namedtuple('Position', ('lat', 'lon'))


class GeoResult(object):
    def __init__(self, country, locality, pos, area=None, subarea=None):
        self.country = country
        self.locality = locality
        self.pos = pos or ()
        self.area = area
        self.subarea = subarea

    def __unicode__(self):
        pieces = map(unicode, filter(None, [self.country, self.area, self.subarea, self.locality]))
        return u', '.join(pieces) + (' (%f, %f)' % self.pos)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<GeoResult: %s>' % str(self)


class Geocoder(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, geoquery, results=1, plng='ru', kind='locality'):
        query = {
            'results': results,
            'format': 'json',
            'plng': plng,
            'kind': kind,
            'key': self.api_key,
        }

        if isinstance(geoquery, (tuple, list)):
            query['geocode'] = ','.join(map(str, reversed(geoquery[:2])))
        else:
            query['geocode'] = str(geoquery)

        url = YANDEX_GEO_URL + ('?%s' % urllib.urlencode(query))
        res = json.load(urllib.urlopen(url))
        if u'response' in res:
            return create_result(res)
        else:
            raise GeoError(res[u'error'][u'message'])


def create_result(res):
    r = res[u'response'][u'GeoObjectCollection']
    result_list = []

    for geoobj in (o[u'GeoObject'] for o in r[u'featureMember']):
        pos = Position(*reversed(map(float, geoobj[u'Point'][u'pos'].split())))
        address_dict = geoobj[u'metaDataProperty'][u'GeocoderMetaData'][u'AddressDetails']
        country = Country(address_dict[u'Country'][u'CountryName'],
                          address_dict[u'Country'][u'CountryNameCode'])

        if u'AdministrativeArea' in address_dict[u'Country']:
            area_dict = address_dict[u'Country'][u'AdministrativeArea']
            area = area_dict[u'AdministrativeAreaName']
            subarea = area_dict[u'SubAdministrativeArea'][u'SubAdministrativeAreaName']
            locality = area_dict[u'SubAdministrativeArea'][u'Locality'][u'LocalityName']
        else:
            area = None
            subarea = None
            locality = address_dict[u'Country'][u'Locality'][u'LocalityName']

        area_dict = address_dict[u'Country']
        result_list.append(GeoResult(country, locality, pos, area=area, subarea=subarea))
    return result_list


if __name__ == '__main__':
    g = Geocoder('API-KEY')
    res = g.geocode((59.93772, 30.313622)) # lat, lon
    print res


