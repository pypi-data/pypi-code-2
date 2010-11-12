# -*- coding: utf-8 -*-

usage = r"""
Add and/or remove given tags to given set of tasks.

Example:

    %prog --add=work --add=computer \
          --remove=office \
          --filter='list:"Prepared Reports" and status:"incomplete"'

(add tags work and computer and remove tag office to all tasks from
list named Prepared Reports which are incomplete)

Note: filter is using standard RememberTheMilk language, see
http://www.rememberthemilk.com/help/answers/search/advanced.rtm
"""

from connect import create_rtm_client

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(usage=usage)
    opt_parser.add_option("-a", "--add",
                          action="append", type="string", dest="add",
                          help="Tag to add (use --add many times to add many tags)")
    opt_parser.add_option("-r", "--remove",
                          action="append", type="string", dest="remove",
                          help="Tag to remove (use --remove many times to del many tags)")
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
    if not (opts.add or opts.remove):
        opt_parser.error("either --add, or --remove must be specified (or both)")
    return opts
    
def run():

    opts = parse_options()
    client = create_rtm_client()

    raise Exception("Sorry, this is not yet implemented")

    print opts.add
    print opts.remove
    print opts.filter

# ...

