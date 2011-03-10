#!/usr/bin/env python
# -*- coding: utf-8 -*- #
'''Watchvideo'''
###
#
# WatchVideo is the legal property of Leonardo Gastón De Luca
# leo[at]kde.org.ar Copyright (c) 2009 Leonardo Gastón De Luca
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###

from optparse import OptionParser
import os
import sys

from watchvideo.main import download, play, get_new_file, MATCHER
import watchvideo.constants as c
from watchvideo.utils import is_command


def validate_output(path, vid_name, one_video=True):
    fullpath = vid_name

    if os.path.exists(path):
        #path can exist and be a file or a directory
        if os.path.isdir(path):
            fullpath = os.path.join(path, vid_name)
        elif one_video:  # file already exists and it's only one file
            fullpath = get_new_file(path, vid_name)
        else:  # if there are many videos, get the path, forget the name
            fullpath = os.path.split(path)[0]

    else:  # if it's the path to a non-existant file

        if os.path.exists(os.path.split(path)[0]):
            #if the path to the file exists and the file doesn't
            #it means it's a valid path
            if one_video:
                #if only one video, copy all the path
                fullpath = path
            else:
                #if more than one video, get the path, forget the name
                fullpath = os.path.split(path)[0]

    return fullpath


def handle_single_video(medium, mformat, options, one_video):
    """Play or watch a single video."""
    if options.down:
        #Validate output option
        videopath = medium.title + mformat.file_extension
        if options.output:
            videopath = validate_output(options.output, medium.title,
                                        one_video)
        download(mformat.url, videopath)
    else:
        play(mformat.url, medium.title, options.player)


def describe_format(mformat):
    """Return *mformat* as human-readable string."""
    text = ""
    if mformat.width is not None and mformat.height is not None:
        text = "%dx%d" % (mformat.width, mformat.height)
    if mformat.mime_type:
        if text:
            text += " "
        text += mformat.mime_type
    return text


def choose_format(medium, options, one_video):
    """Play or download some formats of a medium."""
    if options.quality == "all":
        formats = list(medium)
        for i in xrange(0, len(formats)):
            print i, medium.website, medium.title, describe_format(formats[i])
        choice = None
        while True:
            line = raw_input("format number>")
            try:
                choice = int(line)
            except ValueError:
                assert True
            else:
                break
        try:
            mformat = formats[choice]
        except IndexError:
            return
        handle_single_video(medium, mformat, options, one_video)
    elif options.quality == "lowest":
        handle_single_video(medium, min(medium), options, one_video)
    elif options.quality == "highest":
        handle_single_video(medium, max(medium), options, one_video)
    else:
        raise AssertionError("unknown value of options.quality")


def handle_videos(media, options):
    """Ask the user which of videos to play or download"""
    if len(media) == 1:
        choose_format(media[0], options, True)
    else:
        choices = [False] * len(media)
        for i in xrange(0, len(media)):
            print i, media[i].website, media[i].title
        while True:
            line = raw_input("video number>")
            if not line:
                break
            for token in line.split():
                if token == "all":
                    choices = [True] * len(media)
                elif token == "none":
                    choices = [False] * len(media)
                else:
                    try:
                        choices[int(token)] = True
                    except (ValueError, IndexError):
                        assert True
        for i in xrange(0, len(media)):
            if choices[i]:
                choose_format(media[i], options, choices.count(True) < 2)


def run():
    '''Main function'''
    try:
        parser = OptionParser(usage="usage: %prog [options] URL", \
        version=c.VERSION)
        parser.add_option("-d", "--download",
                        action="store_true",
                        dest="down",
                        default=False,
                        help="download the video")
        parser.add_option("-L", "--list-plugins",
                          action="store_true",
                          dest="list_plugins",
                          default=False,
                          help="list plugins used and exit")
        parser.add_option("-p", "--player",
                          dest="player",
                          default=False,
                          help="use your favourite player")
        parser.add_option("-o", "--output",
                          dest="output",
                          default=False,
                          help="save video to a certain location")
        parser.add_option("-q", "--quality",
                          dest="quality",
                          default="all",
                          help="list all, lowest or highest " \
                              "quality video formats")
        (options, args) = parser.parse_args()
        #Validate player option
        if not options.player:
            options.player = None
        elif is_command(options.player):
            options.player = options.player
        else:
            options.player = None
            print (" *ERROR* " + '"' + str(options.player) + '"' +
                   " is NOT a valid player! Using default player...\n")
        # Validate quality option.
        chosen_quality = None
        for quality in ("all", "lowest", "highest"):
            if quality.startswith(options.quality):
                if chosen_quality is None:
                    chosen_quality = quality
                else:
                    parser.error("ambiguous quality setting")
        if chosen_quality is not None:
            options.quality = chosen_quality
        else:
            parser.error("unknown quality chosen")
        if options.list_plugins:
            print "Installed plugins:"
            print ", ".join(plugin
                            for plugin in MATCHER.plugins.iterkeys())
            print ""
            print "Disabled plugins:"
            for plugin, reasons in MATCHER.disabled.iteritems():
                print plugin
                print "\n".join("\t" + reason for reason in reasons)
        else:
            valid_videos = []
            for url in args:
                plugin = MATCHER.match(url)
                if plugin is not None:
                    for medium in plugin:
                        valid_videos.append(medium)

            if not valid_videos:
                print "No valid links found."
            else:
                handle_videos(valid_videos, options)

    except KeyboardInterrupt:
        print '\r'
        sys.exit()

if __name__ == "__main__":
    run()
