# -*- coding: utf-8 -*-

usage = r"""
Move all tags satisfying given criteria to given list.

Example:

    %prog --list='Language learning' \
            --filter='list:"English Course" or tag:"French" or tag:German"

Destination list is created if not yet present.

Note: filter is using standard RememberTheMilk language, see
http://www.rememberthemilk.com/help/answers/search/advanced.rtm
"""

from connect import create_rtm_client

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(usage=usage)
    opt_parser.add_option("-l", "--list",
                          action="store", type="string", dest="list",
                          help="Target list to which all specified tasks will be moved.")
    opt_parser.add_option("-f", "--filter",
                          action="store", type="string", dest="filter",
                          help="Data filter (RTM query syntax)")
    opt_parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose",
                          help="Print diagnostic messages")
    opt_parser.add_option("-d", "--dry-run",
                          action="store_true", dest="dry_run",
                          help="Don't execute any updates, just check input and (if verbose) print planned actions")
                          
    opt_parser.set_defaults(verbose = False, dry_run = False, add =[], remove =[])
    (opts, args) = opt_parser.parse_args()

    if not opts.filter:
        opt_parser.error("--filter not specified")
    if not opts.list:
        opt_parser.error("--list not specified")
    return opts
    
def run():

    opts = parse_options()
    client = create_rtm_client()

    raise Exception("Sorry, this is not yet implemented")

    print opts.add
    print opts.remove
    print opts.filter

# ...

