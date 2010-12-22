'''Helpers to access AESO's asset list at
<http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet>.
'''

########################################################################
## Standard library imports
import csv
import shutil
import re
import urllib
import urllib2


def urlopen_asset_list():
    '''Returns a file-like object containing data returned by the ETS
    asset list webservice.

    :rtype: file-like object as returned by urlopen.

    .. versionadded:: 0.6

    Usage example::

        >>> # 3rd Party Libraries
        >>> from aeso import asset
        >>>
        >>> f = asset.urlopen_asset_list()
        >>> text = f.read()
        >>> f.close()


    .. note::

        The raw ETS asset list report can be accessed at
        <http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet>.
    '''

    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet'
    parameters = {
        'contentType' : 'csv',
    }

    encoded_params = urllib.urlencode(parameters)
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet?contentType=html
    f = urllib2.urlopen(url, encoded_params)

    return f


def dump_asset_list(f_out):
    '''Downloads asset list report and writes it to file-object *f*.

    .. versionadded:: 0.6

    Usage example::

        >>> # 3rd Party Libraries
        >>> from aeso import asset
        >>>
        >>> f = open('asset_list_report.csv', 'w')
        >>> asset.dump_asset_list(f)
        >>> f.close()
    '''

    f_in = urlopen_asset_list()
    shutil.copyfileobj(f_in, f_out)


_RE_DATEHOUR = re.compile('(\d+)/(\d+)/(\d+) (\d+)$')


class AssetType(object):
    '''Asset type enumeration.

    .. versionadded:: 0.6
    '''

    #:
    SOURCE = 'source'

    #:
    SINK = 'sink'

    _lut = {
        SOURCE : 'source',
        SINK : 'sink',
    }

    @classmethod
    def from_str(klass, string):
        '''Converts some simple strings to enumeration values.'''
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            #raise ValueError('Unknown asset type {0}.'.format(repr(string)))
            raise ValueError('Unknown asset type ' + repr(string))


class AssetStatus(object):
    '''Asset state enumeration.

    .. versionadded:: 0.6
    '''

    #:
    ACTIVE = 'active'

    #:
    INACTIVE = 'inactive'

    #:
    RETIRED = 'retired'

    #:
    SUSPENDED = 'suspended'

    _lut = {
        ACTIVE : 'active',
        INACTIVE : 'inactive',
        RETIRED : 'retired',
        SUSPENDED : 'suspended',
    }

    @classmethod
    def from_str(klass, string):
        '''Converts some simple strings to enumeration values.'''
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            raise ValueError('Unknown asset status ' + repr(string))
            #raise ValueError('Unknown asset status {0}.'.format(repr(string)))


_RE_ASSETNAME = re.compile('<[^>]*>\s*<[^>]*>(.*)')
def _normalize_asset_name(string):
    #'<A NAME=3Anchor"></A>301A 3070 Ret #1'
    match = _RE_ASSETNAME.match(string)
    if match:
        return match.group(1)
    else:
        return string


class Asset(object):
    '''Represents an asset be it an :class:`AssetType.SINK` and :class:`AssetType.SOURCE`

    .. versionadded:: 0.6
    '''

    def __init__(self, asset_name, asset_id, asset_type, status, participant_name, participant_id):
        self._asset_name = asset_name
        self._asset_id = asset_name
        self._asset_type = asset_type
        self._status = status
        self._participant_name = participant_name
        self._participant_id = participant_id

    @property
    def asset_name(self):
        ''':class:`str` property.'''
        return self._asset_name

    @property
    def asset_id(self):
        ''':class:`str` property.'''
        return self._asset_id

    @property
    def asset_type(self):
        ''':class:`AssetType` property.'''
        return self._asset_type

    @property
    def status(self):
        ''':class:`AssetStatus` property.'''
        return self._status

    @property
    def participant_name(self):
        ''':class:`str` property.'''
        return self._participant_name

    @property
    def participant_id(self):
        ''':class:`str` property.'''
        return self._participant_id


def parse_asset_list_file(f):
    '''Yields Asset objects extracted from the open file-object *f*.

    .. versionadded:: 0.6

    Usage example::

        >>> # 3rd Party Libraries
        >>> from aeso import asset
        >>>
        >>>
        >>> f = asset.urlopen_asset_list()
        >>> assets = list(asset.parse_asset_list_file(f))
        >>> f.close()'''
    reader = csv.reader(f)
    for idx, line in enumerate(reader):
        # ["Williams Lk Gen St - BCH","IPI1","Source","Retired","Inland Pacific Energy Services","IPES"]
        try:
            if idx > 2 and len(line) > 0:
                yield Asset(_normalize_asset_name(line[0]), line[1], AssetType.from_str(line[2]), AssetStatus.from_str(line[3]), line[4], line[5])
        except IndexError:
            # raised when number of cells in row is incorrect.
            #raise ValueError('Unable to parse line {0}: {1}'.format(idx, repr(line)))
            raise ValueError('Unable to parse line ' + str(idx) + ': ' + repr(line))

