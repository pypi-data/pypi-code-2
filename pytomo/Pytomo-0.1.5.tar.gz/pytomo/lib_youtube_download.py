#!/usr/bin/env python2.5
"""Module to download youtube video for a limited amount of time and
calculate the data downloaded within that time


Usage : ./complete_yt_dl.py http://www.youtube.com/watch?v=-5aTKyaVbyE 30

"""

from __future__ import with_statement
import httplib
import math
import re
import socket
import sys
import time
import urllib
import urllib2
import tempfile

# only for logging
import logging
from time import strftime
from os import sep

import pytomo.kaa_metadata as kaa_metadata
from pytomo.kaa_metadata.core import ParseError

# for python2.5 only
from cgi import parse_qs

import pytomo.config_pytomo as config_pytomo

STD_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.12) \
Gecko/20101028 Firefox/3.6.12',
   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'en-us,en;q=0.5',
}

PLAYING_STATE = True
BUFFERING_STATE = False

class DownloadError(Exception):
    """Download Error exception.

    This exception may be thrown by FileDownloader objects if they are not
    configured to continue on errors. They will contain the appropriate
    error message.
    """
    pass

class UnavailableVideoError(Exception):
    """Unavailable Format exception.

    This exception will be thrown when a video is requested
    in a format that is not available for that video.
    """
    pass

class ContentTooShortError(Exception):
    """Content Too Short exception.

    This exception may be raised by FileDownloader objects when a file they
    download is too small for what the server announced first, indicating
    the connection was probably interrupted.
    """
    pass

class FileDownloader(object):
    """File Downloader class.

    File downloader objects are the ones responsible of downloading the
    actual video file and writing it to disk if the user has requested
    it, among some other tasks. In most cases there should be one per
    program. As, given a video URL, the downloader doesn't know how to
    extract all the needed information, task that InfoExtractors do, it
    has to pass the URL to one of them.

    For this, file downloader objects have a method that allows
    InfoExtractors to be registered in a given order. When it is passed
    a URL, the file downloader handles it to the first InfoExtractor it
    finds that reports being able to handle it. The InfoExtractor extracts
    all the information about the video or videos the URL refers to, and
    asks the FileDownloader to process the video information, possibly
    downloading the video.

    File downloaders accept a lot of parameters. In order not to saturate
    the object constructor with arguments, it receives a dictionary of
    options instead. These options are available through the params
    attribute for the InfoExtractors to use. The FileDownloader also
    registers itself as the downloader in charge for the InfoExtractors
    that are added to it, so this is a "mutual registration".

    Available options:

    quiet:            Do not print messages to stdout.
    forceurl:         Force printing final URL.
    forcetitle:       Force printing title.
    forcethumbnail:   Force printing thumbnail URL.
    forcedescription: Force printing description.
    simulate:         Do not download the video files.
    format:           Video format code.
    format_limit:     Highest quality format to try.
    outtmpl:          Template for output names.
    ignoreerrors:     Do not stop on download errors.
    ratelimit:        Download speed limit, in bytes/sec.
    nooverwrites:     Prevent overwriting files.
    retries:          Number of times to retry for HTTP error 5xx
    continuedl:       Try to continue downloads if possible.
    noprogress:       Do not print the progress bar.
    playliststart:    Playlist item to start at.
    playlistend:      Playlist item to end at.
    logtostderr:      Log messages to stderr instead of stdout.
    """
    params = None
    _ies = []
    #_pps = []
    _download_retcode = None
    _total_bytes = None
    _total_time = None
    _format_downloaded = None

    def __init__(self, download_time):
        """Create a FileDownloader object with the given options."""
        self._ies = []
        #self._pps = []
        self._download_retcode = 0
        self._num_downloads = 0
        if (config_pytomo.LOG_FILE == '-') or (not config_pytomo.LOG_FILE):
            self._screen_file = sys.stdout
        else:
            # I don't like it this way...
            self._screen_file = open(config_pytomo.LOG_FILE_TIMESTAMP, 'a')
        self.state = BUFFERING_STATE
        self.accumulated_playback = None
        self.accumulated_buffer = None
        self.current_buffer = 0.0
        self.interruptions = 0
        self.seen_timestamp = None
        self.encoding_rate = None
        self.data_len = None
        self.data_duration = None
        self.max_instant_thp = None
        try:
            self.download_time = int(download_time)
        except ValueError:
            config_pytomo.LOG.exception(
                "Please provide a number as max download time. Got : %s"
                % download_time)
            self.download_time = config_pytomo.DOWNLOAD_TIME
            config_pytomo.LOG.info('Set max download_time as: %d'
                                   % self.download_time)
        if self.download_time <= 0:
            self.download_time = 600
        #self.quiet = quiet
        #self.params = params

    def set_total_time(self, total_time):
        """Set total time taken to actually download the video."""
        self._total_time = total_time

    def get_total_time(self):
        ' Returns the time taken to domnload the file'
        return self._total_time

    def set_total_bytes(self, total_bytes):
        """Set total bytes."""
        self._total_bytes = total_bytes

    def get_total_bytes(self):
        'The total bytes downloaded in total_time'
        return self._total_bytes

    def set_format(self, vid_format):
        """Set format."""
        self._format_downloaded = vid_format

    def get_format(self):
        'Returns the format of file downloaded'
        return self._format_downloaded

    @staticmethod
    def format_bytes(byte_counter):
        'Formatting the bytes'
        if byte_counter is None:
            return 'N/A'
        if type(byte_counter) is str:
            byte_counter = float(byte_counter)
        if byte_counter == 0.0:
            exponent = 0
        else:
            exponent = long(math.log(byte_counter, 1024.0))
        suffix = 'bkMGTPEZY'[exponent]
        converted = float(byte_counter) / float(1024**exponent)
        return '%.2f%s' % (converted, suffix)

    @staticmethod
    def calc_percent(byte_counter, data_len):
        "Computes remaining percent of download"
        if data_len is None:
            return '---.-%'
        return '%6s' % ('%3.1f%%'
                        % (float(byte_counter) / float(data_len) * 100.0))

    @staticmethod
    def calc_eta(start, now, total, current):
        "Computes the remaining time"
        if total is None:
            return '--:--'
        dif = now - start
        if current == 0 or dif < 0.001: # One millisecond
            return '--:--'
        rate = float(current) / dif
        eta = long((float(total) - float(current)) / rate)
        (eta_mins, eta_secs) = divmod(eta, 60)
        if eta_mins > 99:
            return '--:--'
        return '%02d:%02d' % (eta_mins, eta_secs)

    @staticmethod
    def calc_speed(start, now, byte_counter):
        "Computes download speed"
        diff = now - start
        if byte_counter == 0 or diff < 0.001: # One millisecond
            return '%10s' % '---b/s'
        return '%10s' % ('%sb/s'
                         % FileDownloader.format_bytes(float(byte_counter)
                                                       / diff))

    @staticmethod
    def best_block_size(elapsed_time, data_block_len):
        '''Function to determine the best block size tht is to be used for the
        remaining data'''
        new_min = max(data_block_len / 2.0, 1.0)
        # Do not surpass 4 MB
        new_max = min(max(data_block_len * 2.0, 1.0), 4194304)
        if elapsed_time < 0.001:
            return long(new_max)
        rate = data_block_len / elapsed_time
        if rate > new_max:
            return long(new_max)
        if rate < new_min:
            return long(new_min)
        return long(rate)

    def add_info_extractor(self, add_ie):
        """Add an InfoExtractor object to the end of the list."""
        self._ies.append(add_ie)
        add_ie.set_downloader(self)

    def to_screen(self, message, skip_eol=False):
        """Print message to stdout if not in quiet mode."""
        #if not self.quiet:
        terminator = [u'\n', u''][skip_eol]
        print >> self._screen_file, (u'%s%s' % (message, terminator)),
        self._screen_file.flush()

    @staticmethod
    def to_stderr(message):
        """Print message to stderr."""
        print >> sys.stderr, message

    @staticmethod
    def trouble(message=None):
        """Determine action to take when a download problem appears.

        Depending on if the downloader has been configured to ignore
        download errors or not, this method may throw an exception or
        not when errors are found, after printing the message.
        """
        if message is not None:
            #self.to_stderr(message)
            config_pytomo.LOG.debug('trouble message: %s' % message)
        #if not self.params.get('ignoreerrors', False):
        raise DownloadError(message)
        #self._download_retcode = 1

    def report_progress(self, progress_stats):
        """Report download progress."""
        self.to_screen('\r[download] %(percent_str)s of %(data_len_str)s at \
%(speed_str)s ETA %(eta_str)s Bytes %(byte_counter)d Inst_thp \
%(instant_thp)skb/s  Buf_dur %(accumulated_buffer)f' % progress_stats,
                       skip_eol=True)

    def report_retry(self, count, retries):
        """Report retry in case of HTTP error 5xx"""
        self.to_screen(u'[download] Got server HTTP error. \
Retrying (attempt %d of %d)...' % (count, retries))

    def report_finish(self):
        """Report download finished."""
        #if self.params.get('noprogress', False):
        self.to_screen(u'\n[download] Download completed')
        #else:
            #self.to_screen(u'')


    def process_info(self, info_dict):
        """Process a single dictionary returned by an InfoExtractor."""
#        # Do nothing else if in simulate mode
#        if self.params.get('simulate', False):
#            # Forced printings
#            if self.params.get('forcetitle', False):
#                print info_dict['title']
#            if self.params.get('forceurl', False):
#                print info_dict['url']
#            if (self.params.get('forcethumbnail', False)
#                and 'thumbnail' in info_dict):
#                print info_dict['thumbnail']
#            if (self.params.get('forcedescription', False)
#                and 'description' in info_dict):
#                print info_dict['description']
#            return
        try:
            template_dict = dict(info_dict)
            template_dict['epoch'] = unicode(long(time.time()))
            template_dict['autonumber'] = unicode('%05d' % self._num_downloads)
        except (ValueError, KeyError), err:
            self.trouble(u'ERROR: invalid system charset or erroneous output \
template')
            return
        try:
            total_download_time = self._do_download(
                                        info_dict['url'].encode('utf-8'),
                                      )
        except (OSError, IOError), err:
            raise UnavailableVideoError
        except (httplib.HTTPException, socket.error), err:
            self.trouble(u'ERROR: unable to download video data: %s' % str(err))
            return
        except (ContentTooShortError, ), err:
            self.trouble(
                u'ERROR: content too short (expected %s bytes and served %s)'
                % (err.expected, err.downloaded))
            return

        self.set_total_time(total_download_time)
        return total_download_time

    def download(self, url_list):
        """Download a given list of URLs."""

        for url in url_list:
            suitable_found = False
            for ie_var in self._ies:
                # Go to next InfoExtractor if not suitable
                if not ie_var.suitable(url):
                    continue

                # Suitable InfoExtractor found
                suitable_found = True

                # Extract information from URL and process it
                ie_var.extract(url)

                # Suitable InfoExtractor had been found; go to next URL
                break

            if not suitable_found:
                self.trouble(u'ERROR: no suitable InfoExtractor: %s' % url)

        return self._download_retcode


    @staticmethod
    def establish_connection(url):
        """Set up the connection
        Return the data stream
        """
        data = None
        proxy = urllib2.ProxyHandler(config_pytomo.PROXIES)
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        basic_request = urllib2.Request(url, None, STD_HEADERS)
        request = urllib2.Request(url, None, STD_HEADERS)
        count = 0
        retries = 0
        while count <= retries:
            # Establish connection
            try:
                data = urllib2.urlopen(request)
                break
            except (urllib2.HTTPError, ), err:
                if (err.code < 500 or err.code >= 600) and err.code != 416:
                    # Unexpected HTTP error
                    raise
                elif err.code == 416:
                    # Unable to resume (requested range not satisfiable)
                    try:
                        # Open the connection again without the range header
                        data = urllib2.urlopen(basic_request)
                    except (urllib2.HTTPError, ), err:
                        if err.code < 500 or err.code >= 600:
                            raise
                    else:
                        # Examine the reported length
                        #open_mode = 'wb'
                        pass
            # Retry
            count += 1
        if count > retries:
            config_pytomo.LOG.error(u'ERROR: giving up after %d retries'
                                    % retries)
        return data

    def compute_interruptions(self, data_block_len, current_time):
        "Compute the number of interruptions in the playback"
        if not self.encoding_rate:
            # start of download: do not keep track of the bytes
            # downloaded before getting the encoding rate because video data do
            # not appear before encoding rate!
            # NO: self.start_buffered_bytes += data_block_len
            return
        self.current_buffer += data_block_len / self.encoding_rate
        if self.state == PLAYING_STATE:
            self.current_buffer -= (current_time - self.seen_timestamp)
            self.seen_timestamp = current_time
            if self.current_buffer < config_pytomo.MIN_PLAYOUT_BUFFER_SIZE:
                self.interruptions += 1
                self.state = BUFFERING_STATE
                config_pytomo.LOG.debug(
                    "Entering buffering state: %d itr and buffered %f"
                    % (self.interruptions, self.current_buffer))
        elif self.current_buffer > config_pytomo.BUFFERING_VIDEO_DURATION:
            config_pytomo.LOG.debug(
                "Entering playing state with %f sec buffered"
                % self.current_buffer)
            self.state = PLAYING_STATE
            self.seen_timestamp = current_time
            # do not update current time if not in playing state (or just
            # switched)
        else:
            # buffering
            pass

    def compute_encoding_rate(self, data_block, meta_file):
        """Compute the encoding rate
        if found in the temp file, close the file and set the value in the
        object
        """
        meta_file.write(data_block)
        meta_file.flush()
        try:
            data_duration = get_data_duration(meta_file.name)
        except ParseError, mes:
            config_pytomo.LOG.debug('data duration not yet found: %s'
                                   % mes)
            data_duration = None
        if data_duration:
            self.data_duration = data_duration
            self.encoding_rate = self.data_len / data_duration
            config_pytomo.LOG.debug("Encoding rate is: %.2fkb/s"
                                    % (self.encoding_rate / 1e3))
            meta_file.close()

    def _do_download(self, url):
        '''Module that handles the download of the file and
        calculates the time, bytes downloaded'''
        data = self.establish_connection(url)
        if not data:
            config_pytomo.LOG.error('could not establish connection to url: %s'
                                    % url)
            return None
        # content-length in bytes
        self.data_len = float(data.info().get('Content-length', None))
        byte_counter = 0
        accumulated_playback = 0.0
        accumulated_buffer = 0.0
        block_size = 1024
        start = time.time()
        meta_file = tempfile.NamedTemporaryFile()
        while True:
            # Download and write
            before = time.time()
            if not ((before - start) > self.download_time):
                # read in bytes
                data_block = data.read(block_size)
            else:
                break
            if not self.encoding_rate:
                self.compute_encoding_rate(data_block, meta_file)
            data_block_len = len(data_block)
            if data_block_len == 0:
                break
            after = time.time()
            self.compute_interruptions(data_block_len, after)
            if self.state == PLAYING_STATE:
                accumulated_playback += (after - before)
            elif self.state == BUFFERING_STATE:
                accumulated_buffer += (after - before)
            else:
                config_pytomo.LOG.error("Unexpected state case")
            byte_counter += data_block_len
            block_size = self.best_block_size(after - before, data_block_len)
            instant_thp = (8e-3 * data_block_len / (after - before)
                           if (after - before) != 0 else None)
            self.max_instant_thp = max(self.max_instant_thp, instant_thp)
            if config_pytomo.LOG_LEVEL == config_pytomo.DEBUG:
                # Progress message
                progress_stats = {
                    'percent_str': self.calc_percent(byte_counter,
                                                     self.data_len),
                    'data_len_str': self.format_bytes(self.data_len),
                    'eta_str': self.calc_eta(start, time.time(), self.data_len,
                                             byte_counter),
                    'speed_str': self.calc_speed(start, time.time(),
                                                 byte_counter),
                    # in order to avoid None convertion to float in
                    # report_progress and still have information
                    'instant_thp': str(instant_thp),
                    'byte_counter': byte_counter,
                    'accumulated_buffer': accumulated_buffer,
                }
                self.report_progress(progress_stats)
        self.set_total_bytes(byte_counter)
        self.accumulated_playback = accumulated_playback
        self.accumulated_buffer = accumulated_buffer
        config_pytomo.LOG.info("nb of interruptions: %d" % self.interruptions)
        return (after - start)

class InfoExtractor(object):
    """Information Extractor class.

    Information extractors are the classes that, given a URL, extract
    information from the video (or videos) the URL refers to. This
    information includes the real video URL, the video title and simplified
    title, author and others. The information is stored in a dictionary
    which is then passed to the FileDownloader. The FileDownloader
    processes this information possibly downloading the video to the file
    system, among other possible outcomes. The dictionaries must include
    the following fields:

    id:     Video identifier.
    url:        Final video URL.
    uploader:   Nickname of the video uploader.
    title:      Literal title.
    stitle:     Simplified title.
    ext:        Video filename extension.
    format:     Video format.
    player_url: SWF Player URL (may be None).

    The following fields are optional. Their primary purpose is to allow
    youtube-dl to serve as the backend for a video search function, such
    as the one in youtube2mp3.  They are only used when their respective
    forced printing functions are called:

    thumbnail:  Full URL to a video thumbnail image.
    description:    One-line video description.

    Subclasses of this one should re-define the _real_initialize() and
    _real_extract() methods, as well as the suitable() static method.
    Probably, they should also be instantiated and added to the main
    downloader.
    """

    _ready = False
    _downloader = None

    def __init__(self, downloader=None):
        """Constructor. Receives an optional downloader."""
        self._ready = False
        self.set_downloader(downloader)


    def initialize(self):
        """Initializes an instance (authentication, etc)."""
        if not self._ready:
            self._real_initialize()
            self._ready = True

    def extract(self, url):
        """Extracts URL information and returns it in list of dicts."""
        self.initialize()
        return self._real_extract(url)

    def set_downloader(self, downloader):
        """Sets the downloader for this IE."""
        self._downloader = downloader

    def _real_initialize(self):
        """Real initialization process. Redefine in subclasses."""
        pass

    def _real_extract(self, url):
        """Real extraction process. Redefine in subclasses."""
        pass

class YoutubeIE(InfoExtractor):
    """Information extractor for youtube.com."""

    _VALID_URL = (r'^((?:https?://)?(?:youtu\.be/|(?:\w+\.)?'
                  + r'youtube(?:-nocookie)?\.com/(?:(?:v/)'
                  + r'|(?:(?:watch(?:_popup)?(?:\.php)?)?(?:\?|#!?)(?:.+&)?'
                  + r'v=))))?([0-9A-Za-z_-]+)(?(1).+)?$')
    _LANG_URL = (r'http://www.youtube.com/?' +
                 r'hl=en&persist_hl=1&gl=US&persist_gl=1&opt_out_ackd=1')
    _LOGIN_URL = 'https://www.youtube.com/signup?next=/&gl=US&hl=en'
    _AGE_URL = 'http://www.youtube.com/verify_age?next_url=/&gl=US&hl=en'
    _NETRC_MACHINE = 'youtube'
    # Listed in order of quality
    _available_formats = ['38', '37', '22', '45', '35', '34', '43', '18', '6',
                          '5', '17', '13']
    _video_extensions = {
        '13': '3gp',
        '17': 'mp4',
        '18': 'mp4',
        '22': 'mp4',
        '37': 'mp4',
        # You actually don't know if this will be MOV, AVI or whatever
        '38': 'video',
        '43': 'webm',
        '45': 'webm',
    }

    @staticmethod
    def suitable(url):
        'Returns True if URL is suitable to this IE else False'
        return (re.match(YoutubeIE._VALID_URL, url) is not None)

    def report_lang(self):
        """Report attempt to set language."""
        self._downloader.to_screen(u'[youtube] Setting language')

    def report_video_webpage_download(self, video_id):
        """Report attempt to download video webpage."""
        self._downloader.to_screen(u'[youtube] %s: Downloading video webpage'
                                   % video_id)

    def report_infopage_download(self, video_id):
        """Report attempt to download video info webpage."""
        self._downloader.to_screen(
            u'[youtube] %s: Downloading video info webpage' % video_id)

    def report_information_extraction(self, video_id):
        """Report attempt to extract video information."""
        self._downloader.to_screen(
            u'[youtube] %s: Extracting video information' % video_id)

    def get_video_info(self, video_id):
        """Get video info
        Return the video
        """
        proxy = urllib2.ProxyHandler(config_pytomo.PROXIES)
        opener = urllib2.build_opener(proxy)
        self.report_video_webpage_download(video_id)
        video_info = None
        for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
            video_info_url = ('http://www.youtube.com/get_video_info?\
&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el_type))
            request = urllib2.Request(video_info_url, None, STD_HEADERS)
            try:
                #opener_request = opener.open(request)
                #video_info_webpage = opener_request.read()
                video_info_webpage = urllib2.urlopen(request).read()
                video_info = parse_qs(video_info_webpage)
                if 'token' in video_info:
                    break
            except (urllib2.URLError, httplib.HTTPException, socket.error), err:
                self._downloader.trouble(
                    u'ERROR: unable to download video info webpage: %s'
                    % str(err))
                return
        if 'token' not in video_info:
            if 'reason' in video_info:
                self._downloader.trouble(u'ERROR: YouTube said: %s'
                                         % video_info['reason'][0].decode(
                                             'utf-8'))
            else:
                self._downloader.trouble(u'ERROR: "token" parameter not in \
video info for unknown reason')
            return None
        return video_info


    @staticmethod
    def get_swf(video_webpage, mobj):
        "Attempt to extract SWF player URL"
        mobj = re.search(r'swfConfig.*?"(http:\\/\\/.*?watch.*?-.*?\.swf)"',
                         video_webpage)
        if mobj is not None:
            player_url = re.sub(r'\\(.)', r'\1', mobj.group(1))
        else:
            player_url = None
        return player_url

    def get_video_url_list(self, video_id, video_token, video_info,
                           req_format=None):
        """Decide which formats to download with req_format (default is best
        quality)
        Return video url list
        """
        video_url_list = None
        #req_format = self._downloader.params.get('format', None)
        get_video_template = ('http://www.youtube.com/get_video?'
                              + 'video_id=%s&t=%s&eurl=&el=&ps=&asv=&fmt=%%s'
                              % (video_id, video_token))
        if 'fmt_url_map' in video_info:
            url_map = dict(tuple(pair.split('|'))
                           for pair in video_info['fmt_url_map'][0].split(','))
#            format_limit = None
#            #self._downloader.params.get('format_limit', None)
#            if (format_limit is not None
#                and format_limit in self._available_formats):
#                format_list = self._available_formats[
#                    self._available_formats.index(format_limit):]
#            else:
            format_list = self._available_formats
            existing_formats = [x for x in format_list if x in url_map]
            if len(existing_formats) == 0:
                self._downloader.trouble(
                    u'ERROR: no known formats available for video')
                return None
            if req_format is None:
                video_url_list = [(existing_formats[0],
                                   url_map[existing_formats[0]])] # Best quality
            elif req_format == '-1':
                # All formats
                video_url_list = [(f, url_map[f]) for f in existing_formats]
            else:
                if req_format in url_map:
                    # Specific format
                    video_url_list = [(req_format, url_map[req_format])]
                else:
                    # Specific format
                    video_url_list = [(req_format, get_video_template
                                       % req_format)]
        else:
            self._downloader.trouble(u'ERROR: no fmt_url_map or conn '
                                     'information found in video info')
            return None
        return video_url_list

    def _real_extract(self, url):
        "Extract informations from url"
        # Extract video id from URL
        mobj = re.match(self._VALID_URL, url)
        if mobj is None:
            self._downloader.trouble(u'ERROR: invalid URL: %s' % url)
            return
        video_id = mobj.group(2)
        video_info = self.get_video_info(video_id)
        if not video_info:
            return
        # Start extracting information
        self.report_information_extraction(video_id)
        video_token = urllib.unquote_plus(video_info['token'][0])
        video_url_list = self.get_video_url_list(video_id, video_token,
                                                 video_info)
        for format_param, video_real_url in video_url_list:
            # At this point we have a new video
            self._downloader.set_format(format_param)
            # Extension
            video_extension = self._video_extensions.get(format_param, 'flv')
            # Find the video URL in fmt_url_map or conn paramters
            try:
                # Process video information
                self._downloader.process_info({
                    'id':       video_id.decode('utf-8'),
                    'url':      video_real_url.decode('utf-8'),
                    'ext':      video_extension.decode('utf-8'),
                    'format':   (format_param is None and u'NA'
                                 or format_param.decode('utf-8')),
                })
            except UnavailableVideoError, _:
                self._downloader.trouble(u'ERROR: unable to download video '
                                         '(format may not be available)')

def get_data_duration(meta_file_name):
    """Return the length (duration) of data or None
    when found, close the file
    """
    info = kaa_metadata.parse(meta_file_name)
    if (info and 'length' in info):
        data_duration = info.length
        return data_duration
    return None

def get_youtube_info_extractor(download_time=config_pytomo.DOWNLOAD_TIME):
    "Return an info extractor for YouTube with correct mocks"
    youtube_ie = YoutubeIE()
    # only to have trouble/to_screen functions in case of errors
    file_downloader = FileDownloader(download_time)
    file_downloader.add_info_extractor(youtube_ie)
    # Mock because only partial consturction of object
    youtube_ie.report_video_webpage_download = (lambda x:
                            config_pytomo.LOG.debug("Download webpage %s" % x))
    return youtube_ie

def get_youtube_cache_url(url):
    "Return the cache url of the video"
    youtube_ie = get_youtube_info_extractor()
    mobj = re.match(youtube_ie._VALID_URL, url)
    if not mobj:
        config_pytomo.LOG.warning('\n'.join(('url: %s not valid' % url,
                                     'only Youtube download is implemented')))
        return None
    video_id = mobj.group(2)
    try:
        video_info = youtube_ie.get_video_info(video_id)
    except DownloadError, mes:
        config_pytomo.LOG.error(mes)
        return None
    except Exception, mes:
        config_pytomo.LOG.exception('Uncaught exception: %s' % mes)
        return None
    video_token = urllib.unquote_plus(video_info['token'][0])
    # req_format='-1' for all available formats
    # req_format=None for best available format
    try:
        video_url_list = youtube_ie.get_video_url_list(video_id, video_token,
                                                       video_info,
                                                       req_format=None)
    except DownloadError, mes:
        config_pytomo.LOG.error(mes)
        return None
    except Exception, mes:
        config_pytomo.LOG.exception('Uncaught exception: %s' % mes)
        return None
    if video_url_list:
        cache_url = video_url_list[0][1]
        config_pytomo.LOG.debug('Cache url found: %s' % cache_url)
        return cache_url

def get_download_stats(ip_address_uri,
                       download_time=config_pytomo.DOWNLOAD_TIME):
    """Return a tuple of stats for download from an url based on ip address
    Simpler version because cache url is already there: uses only _do_download
    """
    file_downloader = FileDownloader(download_time)
    try:
        download_time = file_downloader._do_download(ip_address_uri)
    except DownloadError, mes:
        config_pytomo.LOG.error(mes)
        return None
    except Exception, mes:
        config_pytomo.LOG.exception('Uncaught exception: %s' % mes)
        return None
    if download_time:
        return [download_time,
                file_downloader.data_duration,
                file_downloader.data_len,
                file_downloader.encoding_rate,
                file_downloader.get_total_bytes(),
                file_downloader.interruptions,
                file_downloader.accumulated_buffer,
                file_downloader.accumulated_playback,
                file_downloader.current_buffer,
                file_downloader.max_instant_thp,
               ]
    return None

def main(argv=None):
    "Program Wrapper"
    if argv is None:
        argv = sys.argv[1:]
    config_pytomo.LOG = logging.getLogger('pytomo')
    # to not have console output
    config_pytomo.LOG.propagate = False
    config_pytomo.LOG.setLevel(config_pytomo.LOG_LEVEL)
    timestamp = strftime("%Y-%m-%d.%H_%M_%S")
    if config_pytomo.LOG_FILE == '-':
        handler = logging.StreamHandler(sys.stdout)
    else:
        log_file = sep.join((config_pytomo.LOG_DIR,
                             '.'.join((timestamp, config_pytomo.LOG_FILE))))
        try:
            with open(log_file, 'a') as _:
                pass
        except IOError:
            print >> sys.stderr, ("Problem opening file: %s" % log_file)
            return 1
        handler = logging.FileHandler(filename=log_file)
        # for complete_yt_dl
        config_pytomo.LOG_FILE_TIMESTAMP = log_file
    log_formatter = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)d - "
                                      "%(levelname)s - %(message)s")
                                      #"%(funcName)s:%(lineno)d - "
    handler.setFormatter(log_formatter)
    config_pytomo.LOG.addHandler(handler)
    url = [argv[0]]
    if len(argv) < 2:
        d_time = config_pytomo.DOWNLOAD_TIME
    else:
        d_time = argv[1]
    # Information extractors
    youtube_ie = YoutubeIE()
    # File downloader
    file_downloader = FileDownloader(d_time)
    print "Download time: %d" % file_downloader.download_time
    file_downloader.add_info_extractor(youtube_ie)
    try:
        retcode = file_downloader.download(url)
    except DownloadError:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(u'\nERROR: Interrupted by user')
    dict_res = {'retcode' : retcode,
                'total_time ': file_downloader.get_total_time(),
                'total_bytes ': file_downloader.get_total_bytes(),
                'video_format':  file_downloader.get_format(),
                'encoding_rate': file_downloader.encoding_rate,
                'interruptions': file_downloader.interruptions}
    return dict_res

if __name__ == '__main__':
    sys.exit(main())

