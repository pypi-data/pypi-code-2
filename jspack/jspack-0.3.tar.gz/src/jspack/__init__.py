#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
from os.path import isdir, isfile, join, splitext, split, isabs, dirname, basename
from optparse import OptionParser
from ConfigParser import ConfigParser
from sys import stdout, stderr, exit
import logging
from subprocess import PIPE, Popen

INOUTPREFIX = 'inout:'
comments = re.compile(r'<!--.*?-->', re.DOTALL)
scripttag = re.compile(r'(<script[^>]*src="([^"]*)"(?! class="jspack).*?(?:</script>|/>))')
usestrict = re.compile(r'("use strict";)')
scripttemplate = r'(<script[^>]*src="(%s[^"]*)"(?! class="jspack).*?(?:</script>|/>))'
# Filled using scripttemplate and option include in main()
customscripttag = None


## Header inserted at the start of each file in the output
HEADER = "/* %s */\n"


def compress(jcode, minimizer):
    if minimizer == 'slimit':
        return slimit(jcode)
    elif minimizer == 'jsmin':
        return jsmin(jcode)
    elif isinstance(minimizer, basestring) and minimizer.startswith(INOUTPREFIX):
        return inout(jcode, minimizer[len(INOUTPREFIX):])
    else:
        return jcode


def inout(jcode, command):
    logging.debug('running: "%s"' % command)
    proc = Popen(command, stdin=PIPE, stdout=PIPE, shell=True)
    out, err = proc.communicate(jcode)
    if err:
        logging.error('Error calling %s' % command)
        return jcode
    return out


def slimit(jcode):
    from slimit import minify
    return minify(jcode)


def jsmin(jcode):
    from jsmin import jsmin
    return jsmin(jcode)


def concatenate(files, minimizer='jsmin', replacestrict=True):
    """
    Concatenate files appending a simple header
    The headers are preserved even if compress is required
    """
    result = []
    for f in files:
        fname = basename(f)
        logging.info("Exporting: " + f)
        result.append(HEADER % fname)
        with open(f) as data:
            source = data.read()
            if replacestrict:
                source = usestrict.sub('', source)
            if minimizer:
                try:
                    logging.info("Minifying %s" % f)
                    source = compress(source, minimizer)
                except Exception:
                    logging.exception('Minifying Error in %s' % f)
            result.append(source)
            result.append("\n")
    logging.info("\nTotal files merged: %d " % len(files))
    merged = "".join(result)
    return merged


def process_cfg(cfgpath, options):
    """
    Process config file like:

    [DEFAULT]
    minimizer = jsmin

    [concatenated.js]
    root = /one/path
    compress = true
    files = file/relative/to/root.js
            /absolute/file.js

    [compressed.js]
    root = /another/path
    minimizer = none
    files = file/relative/to/root.js
            js/two.js


    And generates /one/path/concatenated.js and /another/path/compressed.js
    """
    config = ConfigParser()
    config.read(cfgpath)
    cfpath_dir = dirname(cfgpath)
    for section in config.sections():
        root = cfpath_dir
        if config.has_option(section, 'root'):
            root = config.get(section, 'root')
        cfiles = config.get(section, 'files').split()
        if options.replace:
            if config.has_option(section, 'html'):
                html = config.get(section, 'html')
                if not isabs(html):
                    html = join(root, html)
                # TODO: Improve. Now we are wrinting the file len(sections) times
                replace(html, section, cfiles)
        if options.pack:
            minimizer = False
            if config.has_option(section, 'minimizer'):
                minimizer = config.get(section, 'minimizer')
            files = []
            for f in cfiles:
                if isabs(f):
                    files.append(f)
                else:
                    files.append(join(root, f))
            merged = concatenate(files, minimizer, options.replacestrict)
            with open(section, "w") as output:
                output.write(merged)
            logging.info("Writing to %s (%d KB)" % (section, int(len(merged) / 1024)))


def replace(path, jsminimized, files):

    with open(path, 'r') as htmlfile:
        data = htmlfile.read()
    for f in files:
        # TODO: Fails with js/abc.js followed by js/abc.js.more.js
        tosearch = scripttemplate % f
        if not re.search(r'<!-- \S* includes: ' + tosearch, data):
            data = re.sub(tosearch, r'<!-- %s includes: \1 -->' % jsminimized, data)
    newtag = '<script type="text/javascript"  src="%s" class="jspack"/>' % jsminimized
    if not newtag in data:
        data = data.replace('</head>', '%s\n</head>' % newtag)
    with open(path, 'w') as htmlfile:
        htmlfile.write(data)


def process_html(path, options):
    logging.debug('Procesing... %s' % path)
    head, tail = split(path)
    base = splitext(tail)[0]
    section = base + '-minimized.js'
    with open(path, 'r') as htmlfile:
        data = htmlfile.read()
        data = comments.sub('', data)
        js = [src for tag, src in customscripttag.findall(data)]
    if js:
        config = ConfigParser()
        config.add_section(section)
        if head:
            config.set(section, 'root', head)
        config.set(section, 'html', path)
        config.set(section, 'minimizer', 'jsmin')
        config.set(section, 'files', ' \n  '.join(js))
        if options.write_config:
            cfgpath = join(head, base + '.jspack.cfg')
            if isfile(cfgpath) and not options.overwrite_config:
                logging.warn('File %s exists. Use -o to overwrite' % path)
            else:
                with open(cfgpath, "w") as cfgfile:
                    config.write(cfgfile)
        else:
            config.write(stdout)


def process_file(path, options):
    head, tail = split(path)
    base, ext = splitext(tail)
    if ext in ['.html', '.htm']:
        process_html(path, options)
    elif path.endswith('.jspack.cfg'):
        process_cfg(path, options)


def recurse(path, options):
    if isfile(path):
        process_file(path, options)
    elif isdir(path):
        for root, dirs, files in os.walk(path):
            for d in ['CVS', '.svn', '.hg']:
                if d in dirs:
                    dirs.remove(d)  # don't visit CVS directories
            for f in files:
                process_file(join(root, f), options)


def main():
    usage = """
%prog [options] file_or_directory

Typical Usage:

1. First create cfg files:
   $ %prog -w htmlfile_or_directory
2. Now we can edit the jspack.cfg files and customize
3. Then generate minimized:
   $ %prog cfgfile_or_directory
4. Last, replace script tags:
   $ %prog -rn cfgfile_or_directory

Note: 3 and 4 can be summarized which: $ %prog -r cfgfile_or_directory
    """
    parser = OptionParser(usage=usage)
    parser.add_option("--write-config", "-w",
                  dest="write_config",
                  help="For each FILE.html file write a FILE.jspack.cfg file which later can be used to produce FILE-minimized.js",
                  action="store_true",
                  default=False)
    parser.add_option("--ovewrite-config", "-o",
                  dest="overwrite_config",
                  help="Overwrite a jspack.cfg file if exists. Use which -w option",
                  action="store_true",
                  default=False)
    parser.add_option("--include-only", "-i",
                  dest="include",
                  help="When parsing html (to generate a .jspack.cfg file) , include only javascript files which match this regular expression. Default (?!http), Use "" for no restriction",
                  default="(?!http)")
    parser.add_option("--allow-strict-mode", "-s",
                  dest="replacestrict",
                  help="When concatenate js files, dont't drop 'use strict' lines. Default is remove strip mode",
                  action="store_false",
                  default=True)
    parser.add_option("--no-pack", "-n",
                  dest="pack",
                  help="no packing when using the jspack.cfg. Only usefull with -r option for only replace",
                  action="store_false",
                  default=True)
    parser.add_option("--replace-script-tags", "-r",
                  dest="replace",
                  help="Replace the script tags in html files",
                  action="store_true",
                  default=False)
    parser.add_option('-q', '--quiet',
                  dest='quiet',
                  help='Supress non error output',
                  default=False,
                  action='store_true')
    parser.add_option('-v', '--verbose',
                  dest='verbose',
                  help='Vebose output (debug mode)',
                  default=False,
                  action='store_true')
    (options, args) = parser.parse_args()

    if len(args) != 1:
        print "Wrong param number. Use --help"
        exit(1)

    logging.basicConfig(level=logging.WARNING, stream=stderr, format="%(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if options.quiet:
        logger.setLevel(logging.WARN)
    elif options.verbose:
        logger.setLevel(logging.DEBUG)

    global customscripttag
    customscripttag = re.compile(scripttemplate % options.include)

    path = args[0]
    recurse(path, options)

if __name__ == '__main__':
    main()
