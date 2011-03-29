#!/usr/bin/env python2.5
"""Module to retrieve the related videos from a file with a list of Youtube
links and to store it for next round of the crawl

Arguments:
    * url_file_in: file with a list of URLs to crawl (only Youtube is
      implemented)
    * max_per_page: nb of links to consider per page (only the first
      max_per_page related video links will be seen)
    * max_per_url: nb of links to select per page (max_per_url links will be
      randomly selected out of the max_per_page considered)
    * out_file_name: file name to store the list of related video urls
    * pickle_output: boolean to tell if the file is a pickle file or a text
      file
Usage:
    * from command line:
        ./dict_cache.py url_file.txt
    * as library:
        import lib_cache_url
        url_file_in = 'url_file.txt'
        lib_cache_url.get_next_round_urls(url_file_in, max_per_page=20,
                                          max_per_url=5, out_file_name=None,
                                          pickle_output=False)
"""

from __future__ import with_statement

import sys
import htmllib
import formatter
import urllib
import random
from operator import concat
import logging

from optparse import OptionParser

# global config
import pytomo.config_pytomo as config_pytomo

class LinksExtractor(htmllib.HTMLParser):
    "Simple HTML parser to obtain the urls from webpage"
    # derive new HTML parser
    def __init__(self, format_page):
        # class constructor
        htmllib.HTMLParser.__init__(self, format_page)
        # base class constructor
        self.links = []

    def start_a(self, attrs) :
        # override handler of <A ...>...</A> tags
        # process the attributes
        if len(attrs) > 0 :
            for attr in attrs :
                if attr[0] == "href" :
                    # ignore all non HREF attributes
                    self.links.append(attr[1])
                    # save the link info in the list

    def get_links(self) :
        """Return the list of extracted links"""
        return self.links


def get_all_links(url):
    "Parse and return a list of the links from the HTMLParser"
    # create default formatter
    format_page = formatter.NullFormatter()
    # create new parser object
    htmlparser = LinksExtractor(format_page)
    data = urllib.urlopen(url, proxies=config_pytomo.PROXIES)
    htmlparser.feed(data.read())
    # parse the file saving the info about links
    htmlparser.close()
    return htmlparser.get_links()

def get_youtube_links(url, max_per_page):
    "Return a set of only Youtube links from url"
    if not ('youtube' in url):
        config_pytomo.LOG.error("Only youtube is implemented, got url: %s"
                                % url)
        return []
    links = get_all_links(url)
    youtube_links = set()
    config_pytomo.LOG.info("Found %d links for url %s" % (len(links), url))
    for link in links:
        if link.find("/watch") >= 0:
            if link.startswith('/'):
                link = ''.join(("http://www.youtube.com", link))
            youtube_links.add(link)
            if len(youtube_links) >= max_per_page:
                break
    config_pytomo.LOG.info("Found %d related video links for url %s"
                            % (len(youtube_links), url))
    return youtube_links

def get_links(url, service, max_per_page):
    "Select the service that is to be used"
    if service == 'youtube':
        links = get_youtube_links(url, max_per_page)
    elif service == 'megaupload':
        config_pytomo.LOG.ERROR(
            'Megaupload service not implemented, got url : %s' % url)
        return []
    return links

def trunk_url(url):
    "Return the interesting part of a Youtube url"
    return url.split('&', 1)[0]

def get_related_urls(url, max_per_page, max_per_url):
    "Return a set of max_links randomly chosen related urls"
    youtube_links = get_links(url, 'youtube', max_per_page)
    selected_links = map(trunk_url,
                         random.sample(youtube_links,
                                       min(max_per_url, len(youtube_links))))
    config_pytomo.LOG.debug("Selected %d links for url %s"
                            % (len(selected_links), url))
    return selected_links

def get_next_round_urls(input_links, max_per_page=20, max_per_url=5):
    """Return a tuple of the set of input urls and a set of related url of
    videos
    Arguments:
        * input_links: list of the urls
        * max_per_url and max_per_page options
        * out_file_name: if provided, list is dump in it
        * pickle_output: indicate if dump format is pickle or text
    """
    # keep only non-duplicated links and no links from input file
    related_links = set(reduce(concat, (get_related_urls(url, max_per_page,
                                                         max_per_url)
                                        for url in input_links), [])
                       ).difference(input_links)
    config_pytomo.LOG.info("%d links collected by crawler"
                            % len(related_links))
    config_pytomo.LOG.debug(related_links)
    return related_links

def main(argv=None):
    "Program wrapper"
    if argv is None:
        argv = sys.argv[1:]
    usage = "%prog [-w out_file] [-p 10] [-u 2] [-V] url_file_in"
    parser = OptionParser(usage=usage)
    parser.add_option("-w", dest = "out_file_name", default="-",
            help = "output file or stdout if FILE is - (default case)")
    #parser.add_option("-P", "--pickle", dest = "pickle_output",
                      #action="store_true", default=False,
                      #help="store output file as pickle (default false)")
    parser.add_option("-V", "--verbose", dest = "verbose",
            action="store_true", default=False,
            help = "run as verbose mode")
    parser.add_option("-p", "--max_per_page", dest="max_per_page", default=20,
                      help=("nb max of related urls to consider per input url"
                            "(default 20)"), type="int")
    parser.add_option("-u", "--max_per_url", dest="max_per_url", default=5,
                      help=("nb max of related urls to select per input url"
                            "(default 5)"), type="int")
    (options, args) = parser.parse_args(argv)
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    try:
        # keep only non-empty and non-duplicated links
        with open(args[0], 'r') as input_file:
            input_links = set(filter(None, (line.strip()
                                            for line in input_file)))
    except IOError:
        parser.error("File, %s, does not exist." % args[0])
    #if options.pickle_output and options.out_file_name == "-":
        #parser.error("Must provide a filename in case of pickle output")
    if options.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    config_pytomo.LOG = logging.getLogger('lib_cache_url')
    # to not have console output
    config_pytomo.LOG.propagate = False
    config_pytomo.LOG.setLevel(log_level)
    if options.out_file_name == '-':
        handler = logging.StreamHandler(sys.stdout)
    else:
        try:
            with open(options.out_file_name, 'w') as _:
                pass
        except IOError:
            parser.error("Problem opening file: %s" % options.out_file_name)
        handler = logging.FileHandler(filename=options.out_file_name)
    log_formatter = logging.Formatter("%(asctime)s - %(filename)s - "
                                      "%(levelname)s - %(message)s")
    handler.setFormatter(log_formatter)
    config_pytomo.LOG.addHandler(handler)
    get_next_round_urls(input_links, max_per_page=options.max_per_page,
                        max_per_url=options.max_per_url)

if __name__ == '__main__':
    sys.exit(main())

