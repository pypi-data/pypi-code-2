#! /usr/bin/env python
'''
Translate between llsd encodings and python structures on the commandline.
'''

import sys
import pprint
import optparse
from llbase import llsd


Parsers = {}
Formatters = {}


def main(args = sys.argv[1:]):
    codec = Codec()
    parse, format = codec.process_args(args)

    sys.stdout.write(format(parse(sys.stdin.read())))


class Codec (object):
    def __init__(self):
        def chop_prefix(s, prefix):
            if s.startswith(prefix):
                return s[len(prefix):]
            else:
                return None

        def chop_any_prefix(s, prefixes):
            for prefix in prefixes:
                t = chop_prefix(s, prefix)
                if t is not None:
                    return (prefix, t)
            return None
        
        containermap = {'parse_': {}, 'format_': {}}
        for container in [llsd, self]:
            for pyname in dir(container):
                t = chop_any_prefix(pyname, containermap.keys())
                if t:
                    (prefix, username) = t
                    containermap[prefix][username] = getattr(container, pyname)

        self.parsers = containermap['parse_']
        self.formatters = containermap['format_']

    def process_args(self, args):
        p = optparse.OptionParser(usage = __doc__)
        p.add_option('-p', '--parser',
                     dest = 'parser',
                     type = 'choice',
                     default = 'guess',
                     choices = self.parsers.keys())
        p.add_option('-f', '--format',
                     dest = 'format',
                     type = 'choice',
                     default = 'pprint',
                     choices = self.formatters.keys())
            
        opts, args = p.parse_args(args)
        if args:
            p.error('Unexpected arguments.')

        return (self.parsers[opts.parser], self.formatters[opts.format])

    @staticmethod
    def parse_guess(input):
        return llsd.parse(input)

    @staticmethod
    def format_repr(parsed):
        return repr(parsed)

    @staticmethod
    def format_pprint(parsed):
        return pprint.pformat(parsed)
        



if __name__ == '__main__':
    main()
