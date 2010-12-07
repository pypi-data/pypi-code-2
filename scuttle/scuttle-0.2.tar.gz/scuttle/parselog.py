#!/usr/bin/env python

import contextlib
import gzip
import os
import time
from optparse import OptionParser

from scuttle import Analytics
from scuttle.loggers import RotatingFileLogger
from scuttle.loggers.file import StandardJSONFormatter
from scuttle.parsers import PARSERS

class ParseLog(object):
    def __init__(self, event, filename, outpath, parser, forever=False):
        self.event = event
        self.filename = filename
        self.formatter = StandardJSONFormatter()
        self.logger = RotatingFileLogger(outpath, self.formatter)
        self.analytics = Analytics(self.logger)
        self.parser = parser
        self.forever = forever

    def run(self):
        stat = os.stat(self.filename)
        
        fp = None
        
        while True:
            if not fp:
                if not os.path.exists(self.filename):
                    time.sleep(5)
                    continue
                
                try:
                    if self.filename.endswith('.gz'):
                        fp = gzip.GzipFile(self.filename, "r")
                    else:
                        fp = open(self.filename, "r")
                    stat = os.stat(self.filename)
                except OSError:
                    time.sleep(2)
                    if fp:
                        fp.close()
                        fp = None
                    continue
            
            line = fp.readline()
            if not line:
                if not self.forever:
                    return
                time.sleep(1)

                try:
                    stat2 = os.stat(self.filename)
                    if (stat.st_dev != stat2.st_dev) or (stat.st_ino != stat2.st_ino):
                        fp.close()
                        fp = None
                        continue
                except OSError:
                    fp.close()
                    fp = None
                    continue

                continue

            ts, row = self.parser(line)
            self.analytics.record(self.event, row, ts)

def build_parser():
    parser = OptionParser(usage="Usage: %prog [options] logfile outpath")
    parser.add_option("-n", "--name", dest="name")
    parser.add_option("-p", "--parser", dest="parser", help="Parser (accesslog, ...)")
    parser.add_option("-f", "--forever", dest="forever", default=False, action="store_true")
    return parser

if __name__ == "__main__":
    parser = build_parser()
    options, args = parser.parse_args()
    if len(args) < 2:
        parser.error("must specify a log file and output path")
    if not options.parser:
        parser.error("must specify a parser")
    if not options.name:
        parser.error("must specify a name")

    parser = PARSERS[options.parser]
    parselog = ParseLog(options.name, args[0], args[1], parser, options.forever)
    parselog.run()
