#!/usr/bin/env python
#
#  stations2playlist.py
#
#  Copyright 2010 Costin STROIE <costinstroie@eridu.eu.org>
#
#  Stations to playlist is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Stations to playlist is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Stations to playlist.  If not, see <http://www.gnu.org/licenses/>.
#

""" Create a playlist with all stations of a radio such as SKY.fm or Digitally Imported """

__author__ = 'Costin Stroie'
__email__ = 'costinstroie@eridu.eu.org'
__copyright__ = 'Copyright 2010, Costin Stroie'
__license__ = 'GPLv3'
__version__ = '0.1.3'


# Import the required modules
try:
    import json
except ImportError:
    import simplejson as json
import urllib2
import ConfigParser
import Queue
import threading
from optparse import OptionParser

# Radios name and base urls
RADIOS = {'sky': ('SKY.fm', 'http://listen.sky.fm/'),
          'di':  ('Digitally Imported', 'http://listen.di.fm/')}

EXTENSIONS = {'m3u': 'm3u',
              'radiotray': 'xml'}


class ThreadParsePlaylist(threading.Thread):
    """ Parse the playlist """
    def __init__(self, playlist_queue, output, verbose = False):
        threading.Thread.__init__(self)
        self.playlist_queue = playlist_queue
        self.verbose = verbose
        self.output = output

    def run(self):
        while True:
            # Get the stream name and url from the queue
            name, playlist_url = self.playlist_queue.get()
            if self.verbose:
                print ' %s' % name
            pls = urllib2.urlopen(playlist_url)
            config = ConfigParser.SafeConfigParser()
            config.readfp(pls)
            # Append the result to the stations list
            self.output.append((config.get('playlist', 'Title1'),
                                config.get('playlist', 'File1')))
            self.playlist_queue.task_done()


def get_stations_list(radio, stream_type, verbose = False):
    """ Get a list with all stations, as a json object """
    radio_name, radio_url = RADIOS[radio]
    if stream_type == 'aac':
        url = radio_url + 'public1'
    else:
        url = radio_url + 'public3'
    if verbose:
        print 'Loading %s %s stations at %s' % (radio_name, stream_type, url)
    # Return the json object
    return json.load(urllib2.urlopen(url))

def write_m3u(filename, items, verbose = False):
    """ Create a m3u playlist with all stations """
    if verbose:
        print 'Writing M3U playlist %s' % filename
    fp = open(filename, 'wb')
    fp.write('#EXTM3U\r\n')
    for (name, url) in items:
        fp.write('#EXTINF:-1,%s\r\n' % name)
        fp.write('%s\r\n' % url)
        fp.write('\r\n')
    fp.close()

def write_radiotray(filename, items, verbose = False):
    """ Create a RadioTray compatible playlist """
    if verbose:
        print 'Writing RadioTray playlist %s' % filename
    from xml.dom.minidom import Document
    doc = Document()
    bookmarks = doc.createElement('bookmarks')
    doc.appendChild(bookmarks)
    for (name, url) in items:
        bookmark = doc.createElement('bookmark')
        bookmark.setAttribute('name', name)
        bookmark.setAttribute('url', url)
        bookmarks.appendChild(bookmark)
    # Print our newly created XML
    fp = open(filename, 'wb')
    fp.write(doc.toprettyxml(indent = '  '))
    fp.close()


def main():
    """ The main method """

    # Options
    optparser = OptionParser(usage = '%prog [options]',
                             description = 'Create a playlist with all radio stations from SKY.fm or DI',
                             version = '%prog ' + __version__)
    # Set defaults
    optparser.set_defaults(radio = 'sky',
                           format = 'aac',
                           playlist = 'm3u',
                           verbose = False)
    # Add options
    optparser.add_option('-r', '--radio',
                         dest = 'radio',
                         help = 'the radio source',
                         choices = ['sky', 'di'])
    optparser.add_option('-f', '--format',
                         dest = 'format',
                         help = 'format of the stream',
                         choices = ['mp3', 'aac'])
    optparser.add_option('-p', '--playlist',
                         dest = 'playlist',
                         help = 'format of the playlist',
                         choices = ['m3u', 'radiotray'])
    optparser.add_option('-o', '--output',
                         dest = 'output',
                         help = 'the output file name',
                         metavar = 'FILE')
    optparser.add_option('-v', '--verbose',
                         action = 'store_true',
                         dest = 'verbose',
                         help = 'print status reports')
    # Parse the options
    (options, args) = optparser.parse_args()

    # Start with an empty stations list and playlist queue
    stations = []
    playlist_queue = Queue.Queue()

    # Spawn 5 threads
    for i in range(5):
        t = ThreadParsePlaylist(playlist_queue,
                                stations,
                                verbose = options.verbose)
        t.setDaemon(True)
        t.start()

    # Parse the stations list from the server
    for station in get_stations_list(options.radio,
                                     options.format,
                                     verbose = options.verbose):
        # Get the name and the playlist url
        name = station['name']
        playlist = station['playlist']
        # Put them to the queue
        playlist_queue.put((name, playlist))

    # Wait on the queue until everything has been processed
    playlist_queue.join()
    # Sort the result
    stations.sort()
    # Write the M3U output playlist
    if options.output:
        output = options.output
    else:
        output = '%s-%s.%s' % (options.radio,
                               options.format,
                               EXTENSIONS[options.playlist])
    # Select the playlist format
    if options.playlist == 'm3u':
        write_m3u(output, stations)
    elif options.playlist == 'radiotray':
        write_radiotray(output, stations)

if __name__ == '__main__':
    main()

# vim: set ft=python ai ts=4 sts=4 et sw=4 sta nowrap nu :
