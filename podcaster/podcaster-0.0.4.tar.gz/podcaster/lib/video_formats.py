# -*- coding:utf-8 -*-
import collections

# Video formats : https://secure.wikimedia.org/wikipedia/en/wiki/YouTube#Quality_and_codecs

VideoFormat = collections.namedtuple('VideoFormat', 'id,description,extension,content_type,supported')

VIDEO_FORMATS = (
    VideoFormat('5', 'FLV 400x240', 'flv', 'video/x-flv', 0),
    VideoFormat('34', 'FLV 640x360', 'flv', 'video/x-flv', 0),
    VideoFormat('35', 'FLV 854x480', 'flv', 'video/x-flv', 0),
    VideoFormat('18', 'MP4 480x360', 'mp4', 'video/mp4', 1),
    VideoFormat('22', 'MP4 1280x720', 'mp4', 'video/mp4', 1),
    VideoFormat('37', 'MP4 1920x1080', 'mp4', 'video/mp4', 1),
    VideoFormat('38', 'MP4 4096x3072', 'mp4', 'video/mp4', 1),
    VideoFormat('43', 'WebM 854x480', '???', 'video/???', 0),
    VideoFormat('45', 'WebM 1280x720', '???', 'video/???', 0),
    VideoFormat('17', '3GP 176x144', '???', 'video/???', 0),
)

_itunes_supported_extensions = ('m4a', 'mp3', 'mov', 'mp4', 'm4v', 'pdf')

SUPPORTED_FORMATS = [vf for vf in VIDEO_FORMATS if vf.supported and vf.extension in _itunes_supported_extensions]
PREFERED_FORMAT = '18'

def get_format(id):
    for f in VIDEO_FORMATS:
        if f.id == id:
            return f

def get_lower_resolutions(format):
    if format not in SUPPORTED_FORMATS:
        return []
    resolutions = [vf for vf in SUPPORTED_FORMATS if vf.extension == format.extension][::-1]
    return resolutions[resolutions.index(format):]
