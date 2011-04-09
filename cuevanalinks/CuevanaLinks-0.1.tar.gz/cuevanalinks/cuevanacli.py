#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line interface to cuevanaapi
"""
import sys
import urllib

import plac

import cuevanaapi
import utils

@plac.annotations(
    title=('Look for a movie or show with this title. If `episode` is empty \
           a movie title is assummed', 'positional'),
    episode=('Specifies a season/episode of a show. \n'
             'Examples: S01 (a whole season), s02e04, 1x4',
             'positional'),
    subs=("Download subtitles (if available)", 'flag', 's'),
    language=("Define the language of subtitles.Default: 'ES'", 'option',
            'l', str, ('ES', 'EN', 'PT'), '{ES, EN, PT}')
        )
def cli(title, subs, episode='', language='ES'):
    """
    A program to retrieve movies and series links from cuevana.tv
    """
    c = cuevanaapi.CuevanaAPI()
    if episode:
        numbers = utils.get_numbers(episode)
        if len(numbers) == 1:
            print "Searching '%s' Season '%d'...\n" % (title, numbers[0])
            show = c.get_show(title)
            #TODO if empty?
            #TODO if Exception ?

            season = show.get_season(numbers[0])
            for episode in season:
                print episode.get_links()
                if subs:
                    urllib.urlretrieve(episode.subs[language],
                                      episode.filename(format='long'))

        elif len(numbers) == 2:
            print "Searching '%s' Episode 'S%02dE%02d'...\n" % (title,
                                                        numbers[0], numbers[1])
            show = c.get_show(title)
            episode = show.get_episode(numbers[0], numbers[1])
            print episode.get_links()
            if subs:
                urllib.urlretrieve(episode.subs[language],
                                  episode.filename(format='long'))
        else:
            sys.exit('Not valid season/episode argument')

    else:
        print "Searching '%s'...\n" % title
        results = c.search(title)

        if results:
            print results[0].get_links()
            
            if subs:
                urllib.urlretrieve(results[0].subs[language],
                                  results[0].filename(format='long'))
        #TODO order result by relevance as done with Shows ?
        #or (better) check len of results and turns interactive if are many
        else:
            print "Nothing found for '%s'" % title

def main():
    plac.call(cli)

if __name__ == "__main__":
    main()
