"""
utilities for URLs
"""

import urlparse

def shorten(url, length):
    """shorten a URL preserving readability"""

    if len(url) < length:
        # don't need to do anything
        return url

    parsed = urlparse.urlsplit(url)
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-l', '--length', dest='length',
                      default=20, type='int',
                      help='maximum URL length')
    options, args = parser.parse_args()
    for arg in args:
        print shorten(arg, options.length)
