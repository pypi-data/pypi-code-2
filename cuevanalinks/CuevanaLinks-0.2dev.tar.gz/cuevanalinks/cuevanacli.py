#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line interface to cuevanaapi
"""
import sys
import urllib

import plac

from . import __version__
import cuevanaapi
from downloaders import megaupload
import utils


@plac.annotations(
    title=("Look for a movie or show with this title or URL. "
           "If it's not an URL and `episode` is empty "
           "a movie is assummed", 'positional'),
    episode=('Specifies a season/episode of a show. \n'
             'Examples: S01 (a whole season), s02e04, 1x4',
             'positional'),
    download=("Download the contents instead show links",
                "flag", 'd'),
    subs=("Download subtitles (if available)", 'flag', 's'),
    language=("Define the language of subtitles. Default: 'es'", 'option',
            'l', str, ('es', 'en', 'pt'), '{es, en, pt}'),
    format=("The format of filenames when retrieving files. Default is 'long'", 
            'option', 'f', str, ('long', 'short'), '{long, short}')
        )
def cli(title, subs, download, episode='', language='es', format='long'):
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
            mu_url = content.sources[0]     #FIX ME . always the first one?
            filename = content.filename(format=format, extension='mp4')
            megaupload(mu_url, filename)
        
    language = language.upper()
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
                print e
                sys.exit("Cuevana server has problem. Try in a few minutes")

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
              "A program to retrieve movies and series (or its links) from cuevana.tv"
               % __version__ )

def main():
    plac.call(cli)

if __name__ == "__main__":
    main()
