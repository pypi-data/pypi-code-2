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
import utils


@plac.annotations(
    title=("Look for a movie or show with this title or URL. "
           "If it's not an URL and `episode` is empty "
           "a movie is assummed", 'positional'),
    episode=('Specifies a season/episode of a show. \n'
             'Examples: S01 (a whole season), s02e04, 1x4',
             'positional'),
    subs=("Download subtitles (if available)", 'flag', 's'),
    language=("Define the language of subtitles.Default: 'ES'", 'option',
            'l', str, ('ES', 'EN', 'PT'), '{ES, EN, PT}')
        )
def cli(title, subs, episode='', language='ES'):
    def get_and_print(content):
        """auxiliar function to practice DRY principle"""
        print content.get_links()
        if subs:
            urllib.urlretrieve(content.subs[language],
                               episode.filename(format='long'))


    c = cuevanaapi.CuevanaAPI()

    if title.startswith(cuevanaapi.URL_BASE) and not episode :
        try:
            print "Retrieving '%s'...\n" % title
            content = cuevanaapi.dispatch(title)
            get_and_print(content)
        except NotValidURL:
            sys.exit("Not valid URL of a cuevana's movie/episode")
        except HTTPError:
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
                    get_and_print(episode)
            
            except HTTPError:
                sys.exit("Cuevana server has problem. Try in a few minutes")

        elif len(numbers) == 2:
            #unique episode 
            print "Searching '%s' Episode 'S%02dE%02d'...\n" % (title,
                                                        numbers[0], numbers[1])
            try:
                show = c.get_show(title)
                episode = show.get_episode(numbers[0], numbers[1])
                get_and_print(episode)
            except HTTPError:
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
                          "Try with and episode/season" % title
                else:
                    get_and_print(results[0])

            #TODO order result by relevance as done with Shows ?
            #or (better) check len of results and turns interactive if are many
            else:
                print "Nothing found for '%s'." % title

        except HTTPError:
                sys.exit("Cuevana.tv has a problem. Try in a few minutes")

cli.__doc__ = ("CuevanaLinks %s - 2011 Martin Gaitán\n"
              "A program to retrieve movies and series links from cuevana.tv"
               % __version__ )

def main():
    plac.call(cli)

if __name__ == "__main__":
    main()
