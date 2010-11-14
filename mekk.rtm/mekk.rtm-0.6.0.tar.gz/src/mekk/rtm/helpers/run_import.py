# -*- coding: utf-8 -*-

usage = """
Simple RememberTheMilk importer.

Importing RTM export file (obtained via rtmexport --json=<file>):

    %prog --json=rtm.json  [--verbose] [--dry-run]

Importing Nozbe export file (obtained via nozbetool export --json=<file>):

    %prog --nozbe-json=nozbe.json  [--verbose] [--dry-run]
"""

from connect import create_rtm_client
import simplejson

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(usage=usage)
    opt_parser.add_option("-j", "--json",
                          action="store", type="string", dest="json",
                          help="The name of .json file exported using rtmexport --json ")
    opt_parser.add_option("-n", "--nozbe-json",
                          action="store", type="string", dest="nozbe_json",
                          help="The name of Nozbe .json file exported using nozbetool export --json ")
    opt_parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose",
                          help="Print diagnostic messages")
    opt_parser.add_option("-d", "--dry-run",
                          action="store_true", dest="dry_run",
                          help="Don't execute anything, just check input and (if verbose) print planned actions")
                          
    opt_parser.set_defaults(verbose = False, dry_run = False)
    (opts, args) = opt_parser.parse_args()

    if not (opts.json or opts.nozbe_json):
        opt_parser.error("Operation not selected (--json or --nozbe-json expected)")

    return opts

    
def run():

    opts = parse_options()
    client = create_rtm_client()

    if opts.json:
        data = simplejson.load(open(opts.json),
                               encoding = "utf-8")

        from mekk.rtm.importers.rtmjson import import_rtm

        import_rtm(
            client, tasks = data['tasks'], lists = data['lists'],
            verbose = opts.verbose, dry_run = opts.dry_run)

    if opts.nozbe_json:
        data = simplejson.load(open(opts.nozbe_json),
                               encoding = "utf-8")

        from mekk.rtm.importers.nozbe import import_nozbe_actions

        import_nozbe_actions(
            client, actions = data['actions'], notes = data['notes'],
            verbose = opts.verbose, dry_run = opts.dry_run)
