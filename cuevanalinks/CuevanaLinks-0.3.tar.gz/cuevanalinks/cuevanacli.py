#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line interface to cuevanaapi
"""

import os
import sys
import urllib
import subprocess
from multiprocessing import Process

import plac

from . import __version__
import cuevanaapi
from downloaders import megaupload
import utils

from ConfigParser import SafeConfigParser


@plac.annotations(
    title=("Look for a movie or show with this title or URL. "
           "If it's not an URL and `episode` is empty "
           "a movie is assummed", 'positional'),
    episode=('Specifies a season/episode of a show. \n'
             'Examples: S01 (a whole season), s02e04, 1x4',
             'positional'),
    download=("Download the contents instead show links",
                "flag", 'd'),
    play = ("Play while download. This automatically buffer enough data "
            "before call the player. It's possible define the player command "
            "in the config file", 'flag', 'p'),
    subs=("Download subtitles (if available)", 'flag', 's'),
    language=("Define the language of subtitles. Default: 'es'", 'option',
            'l', str, ('es', 'en', 'pt'), '{es, en, pt}'))
def cli(title, subs, download, play, episode='', language='es', ):

    config = get_config()
    format = config.get('main', 'file_format')
    
    if play:
        download = True

    def get_or_print(content):
        """auxiliar function to practice DRY principle"""

        if subs:
            try:
                urllib.urlretrieve(content.subs[language],
                               content.filename(format=format))
            except Exception, e:        #Fix me 
                print e     

        if not download:
            print content.get_links()
        else:
            print "Found %s" % content.pretty_title
            mu_url = content.sources[0]     #FIX ME . always the first one?
            filename= content.filename(format=format, extension='mp4')
            
            if play:
                command_list = config.get('main', 'player').split()

                if '{file}' in command_list:
                    command_list[command_list.index('{file}')] = filename
                else:
                    command_list.append(filename)

                process = Process(target=background_process, 
                                        args=(command_list,))
                
                megaupload(mu_url, filename, process.start)
                process.join()
            else:
               callback = process = None
               megaupload(mu_url, filename)
            

    language =  language.upper()
    filter = None if not download else 'megaupload'
    c = cuevanaapi.CuevanaAPI(filter)

    if title.startswith(cuevanaapi.URL_BASE) and not episode :
        try:
            print "Retrieving '%s'...\n" % title
            content = cuevanaapi.dispatch(title)
            get_or_print(content)
        except NotValidURL:
            sys.exit("Not valid URL of a cuevana's movie/episode")
        except Exception, e:        #Fix me
            print e
            sys.exit("Cuevana server has problem. Try in a few minutes")

    elif episode:
        #episode or season
        numbers = utils.get_numbers(episode)
        if len(numbers) == 1:
            #season
            print "Searching '%s' Season '%d'...\n" % (title, numbers[0])
            try:
                show = c.get_show(title)
                #TODO if empty?
                #TODO if Exception ?
                season = show.get_season(numbers[0])
                for episode in season:
                    get_or_print(episode)
            
            except Exception, e:            #Fix me
                raise e
                #sys.exit("Cuevana server has problem. Try in a few minutes")

        elif len(numbers) == 2:
            #unique episode 
            print "Searching '%s' Episode 'S%02dE%02d'...\n" % (title,
                                                        numbers[0], numbers[1])
            try:
                show = c.get_show(title)
                episode = show.get_episode(numbers[0], numbers[1])
                get_or_print(episode)
            except Exception, e:        #fix me
                print e 
                sys.exit("Cuevana.tv has a problem. Try in a few minutes")

        else:
            sys.exit('Not valid season/episode argument')

    else:
        #movie
        print "Searching '%s'...\n" % title
        try:
            results = c.search(title)
            if results:
                if isinstance(results[0], cuevanaapi.Show):
                    print "A show was found for '%s'. "\
                          "Try defining an episode/season" % title
                else:
                    get_or_print(results[0])

            #TODO order result by relevance as done with Shows ?
            #or (better) check len of results and turns interactive if are many
            else:
                print "Nothing found for '%s'." % title

        except Exception, e:        #FIX ME this is crap
            print e
            sys.exit("Cuevana.tv has a problem. Try in a few minutes")

cli.__doc__ = ("CuevanaLinks %s - 2011 Martin Gaitán\n"
              "A program to retrieve movies and series "
              "(or links to them) from cuevana.tv"
               % __version__ )

def get_config():
    """
    """
    OS_UNIX = False
    OS_WINDOWS = False
    OS_OSX = False
    if sys.platform.startswith("win"):
        OS_WINDOWS = True
    elif "darwin" in sys.platform:
        OS_OSX = True
    else:
        OS_UNIX = True
    #path constants
    if OS_WINDOWS:
        home = os.path.join(os.path.expanduser("~"), "")
        DEFAULT_PATH = home.decode(locale.getdefaultlocale()[1])
    else:
        DEFAULT_PATH = os.path.join(os.path.expanduser("~"), "")
    
    CONFIG_FILE = os.path.join(DEFAULT_PATH, '.cuevanalinks.cfg')
    
    DEFAULTS = { 'main': {
                    "player": "mplayer -fs {file}",
                    "file_format": "long", 
                  # "download_dir_show": os.path.join( DEFAULT_PATH, "Videos",
                  #                                     "{show}", "{season}"),
                  # "download_dir_movie": os.path.join( DEFAULT_PATH, "Videos",
                  #                                     "{title}" ),
                        },
                }
    config = SafeConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print "There is no config file. Creating default %s" % CONFIG_FILE
        for section, options in DEFAULTS.items():
            for section, options in DEFAULTS.items():
                if not config.has_section(section):
                    config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, value)

        with open(CONFIG_FILE, 'w') as cfg:
            config.write(cfg)
    else:
        with open(CONFIG_FILE, 'r') as cfg:
            config.readfp(cfg)
        
    return config

def background_process(command_list):
    return subprocess.call(command_list,  stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
    
    
    


def main():
    plac.call(cli)

if __name__ == "__main__":
    main()
