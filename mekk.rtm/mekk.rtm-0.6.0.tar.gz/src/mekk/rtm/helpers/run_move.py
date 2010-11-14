# -*- coding: utf-8 -*-

usage = r"""
Move all tags satisfying given criteria to given list.

Example:

    %prog --list='Language learning' \
            --filter='list:"English Course" or tag:"French" or tag:German"

Destination list is created if not yet present.

Run:

    %prog --help

for all options.

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
    opt_parser.add_option("-g", "--debug",
                          action="store_true", dest="debug",
                          help="Print debugging information")
                          
    opt_parser.set_defaults(verbose = False, dry_run = False, debug=False,
                            add =[], remove =[])
    (opts, args) = opt_parser.parse_args()

    if not opts.filter:
        opt_parser.error("--filter not specified")
    if not opts.list:
        opt_parser.error("--list not specified")

    if opts.debug:
        import logging
        logging.basicConfig(level = logging.DEBUG)

    return opts
    
def run():

    opts = parse_options()
    client = create_rtm_client()

    move_tasks(client, filter = opts.filter,
               new_list_name = opts.list,
               verbose = opts.verbose, dry_run = opts.dry_run)

def move_tasks(client, filter, new_list_name,
               verbose = False, dry_run = False):

    new_list = client.find_or_create_list(new_list_name)

    for task in client.find_tasks(filter = filter):
        if task.key.list_id != new_list.id:
            if verbose:
                print "Moving task %s to list %s" % (task.name, new_list.name)
            if not dry_run:
                client.move_task(task.key, new_list.id)

