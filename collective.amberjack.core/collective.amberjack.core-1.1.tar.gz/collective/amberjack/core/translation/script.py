#!python
"""Usage: i18ndude command [options] [path | file1 file2 ...]]

i18ndude performs various tasks related to ZPT's, Python Scripts and i18n.

Unless the -h, or --help option is given one of the commands below must be
present:

   rebuild-pot --pot <filename> --create <domain> [--merge <filename>
   [--merge2 <filename>]] [--exclude="<ignore1> <ignore2> ..."] path [path2 ...]
          Given a pot-file via the --pot option you can specify one or more
          directories which including all sub-folders will be searched for
          PageTemplates (*.*pt) and Python scripts (*.*py).

          Make sure you have a backup copy of the original pot-file in case
          you need to fill back in ids by hand.

          If you give me an additional pot-file with the --merge <filename>
          option, I try to merge these msgids into the target-pot file
          afterwards. If a msgid already exists in the ones I found in the
          ZPTs, I'll warn you and ignore that msgid. I take the mime-header
          from this additional pot-file. If you provide a second pot-file via
          --merge2 <filename> I'll merge this into the first merge's result

          You can also provide a list of filenames which should not be included
          by using the --exclude argument, which takes a whitespace delimited
          list of files.
"""

import sys, os
import getopt
from i18ndude import catalog
from i18ndude.extract import find_files
from collective.amberjack.core import utils

MSG_STR_KEYS = ['title','description', 'text']

def cfg_catalog(dir, domain='none', exclude=()):
    catalogs = {}
    for filename in find_files(dir, '*.cfg', exclude=tuple(exclude)):
        content = open(filename, 'r')
        _raw = utils._load_config(content)
        content.close()
        domain = os.path.splitext(os.path.basename(filename))[0]
        if domain not in catalogs:
            catalogs[domain] = []
        for _msgid, row in _raw.items():
            for key in row:
                if key in MSG_STR_KEYS:
                    msgid = '%s_%s' % (_msgid, key)
                    catalogs[domain].append((msgid, row[key], filename))
    return catalogs

class CFGReader(object):
    """Reads in a list of cfg files."""

    def __init__(self, path, domain, exclude=()):
        self.domain = domain
        self.catalogs = {} # keyed by domain name
        self.path = path
        self.exclude = exclude

    def read(self):
        """Reads in from all given xml's and builds up MessageCatalogs
        accordingly.

        The MessageCatalogs can after this call be accessed through attribute
        ``catalogs``, which indexes the MessageCatalogs by their domain.

        read returns the list of tuples (filename, errormsg), where filename
        is the name of the file that could not be read and errormsg a human
        readable error message.
        """

        cfgs = cfg_catalog(self.path, self.domain, exclude=self.exclude)

        for domain in cfgs:
            for msgid in cfgs[domain]:
                self._add_msg(msgid[0],
                              msgid[1],
                              [],
                              [msgid[2]],
                              [],
                              domain)
        return []

    def _add_msg(self, msgid, msgstr, comments, references, automatic_comments, domain):
        if not domain:
            print >> sys.stderr, 'No domain name for msgid "%s" in %s\n' % \
                  (msgid, references)
            return

        if not self.catalogs.has_key(domain):
            self.catalogs[domain] = catalog.MessageCatalog(domain=domain)

        self.catalogs[domain].add(msgid, msgstr=msgstr, comments=comments, references=references, automatic_comments=automatic_comments)

def usage(code, msg=''):
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

def short_usage(code, msg=''):
    if msg:
        print >> sys.stderr, msg
    print >> sys.stderr, u"Type i18ndude<Enter> to see the help."
    sys.exit(code)

def rebuild_pot():
    try:
        opts, files = getopt.getopt(sys.argv[2:], 'mp:c:',
                                   ('pot=', 'create=', 'merge=', 'merge2=', 'exclude='))
    except:
        usage(1)

    pot_fn = None
    merge_fn = None
    merge2_fn = None
    create_domain = None
    exclude = ()
    for opt, arg in opts:
        if opt in ('-p', '--pot'):
            pot_fn = arg
        if opt in ('-c', '--create'):
            create_domain = arg
        if opt in ('-m', '--merge'):
            merge_fn = arg
        if opt in ('--merge2'):
            merge2_fn = arg
        if opt in ('--exclude'):
            exclude = tuple(arg.split())

    if not pot_fn:
        short_usage(1, u"No pot file specified as target with --pot.")

    if merge2_fn == merge_fn:
        merge2_fn = False

    path = files
    merge_ctl = None

    try:
        if create_domain is not None:
            orig_ctl = catalog.MessageCatalog(domain=create_domain)
        else:
            orig_ctl = catalog.MessageCatalog(filename=pot_fn)
        if merge_fn:
            merge_ctl = catalog.MessageCatalog(filename=merge_fn)
        if merge2_fn:
            merge2_ctl = catalog.MessageCatalog(filename=merge2_fn)

        cfgreader = CFGReader(path, create_domain, exclude=exclude)
    except IOError, e:
        short_usage(0, 'I/O Error: %s' % e)

    cfgresult = cfgreader.read()
    cfgresult #pyflakes

    domain = orig_ctl.domain
    cfgctl = {}

    if domain in cfgreader.catalogs:
        cfgctl = cfgreader.catalogs[domain]
        # XXX Preserve comments?

    if not cfgctl:
        short_usage(0, 'No entries for domain "%s".' % domain)
    ctl = cfgctl

    added_by_merge = []
    if merge_ctl is not None:
        # use headers from merge-catalog
        ctl.commentary_header = merge_ctl.commentary_header
        ctl.mime_header = merge_ctl.mime_header
        # merge
        added_by_merge = ctl.add_missing(merge_ctl, mergewarn=True)
    else:
        # use headers from orig-catalog
        ctl.commentary_header = orig_ctl.commentary_header
        ctl.mime_header = orig_ctl.mime_header

    added_by_merge #pyflakes

    added_by_merge2 = []
    if merge2_fn:
        added_by_merge2 = ctl.add_missing(merge2_ctl, mergewarn=True)

    added_by_merge2 #pyflakes

    ctl.mime_header['POT-Creation-Date'] = catalog.now()
    file = open(pot_fn, 'w')
    writer = catalog.POWriter(file, ctl)
    writer.write(msgstrToComment=True)

def main():
    if len(sys.argv) == 1:
        usage(0)

    commands = {'rebuild-pot': rebuild_pot, }
    command = sys.argv[1]

    try:
        fun = commands[command]
    except KeyError:
        if command in ('-h', '--help'):
            fun = lambda: usage(0)
        else:
            print >> sys.stderr, 'Unknown command %s' % command
            sys.exit(1)

    fun()

if __name__ == '__main__':
    main()
