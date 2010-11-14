# -*- coding: utf-8 -*-

usage = r"""
Add and/or remove given tags to given set of tasks.

Example:

    %prog --add=work --add=computer \
           --remove=office \
           --filter='list:"Prepared Reports" and status:"incomplete"'

(add tags work and computer and remove tag office to all tasks from
list named Prepared Reports which are incomplete)

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
    opt_parser.add_option("-g", "--debug",
                          action="store_true", dest="debug",
                          help="Print debugging information")
                          
    opt_parser.set_defaults(verbose = False, dry_run = False, debug=False,
                            add =[], remove =[])
    (opts, args) = opt_parser.parse_args()

    if not opts.filter:
        opt_parser.error("--filter not specified")
    if not (opts.add or opts.remove):
        opt_parser.error("either --add, or --remove must be specified (or both)")

    if opts.debug:
        import logging
        logging.basicConfig(level = logging.DEBUG)

    return opts
    
def run():

    opts = parse_options()
    client = create_rtm_client()

    modify_tags(client, filter = opts.filter, 
                add_tags = opts.add, remove_tags = opts.remove, 
                verbose = opts.verbose, dry_run = opts.dry_run)

def modify_tags(client, filter, add_tags =[], remove_tags=[],
                verbose = False, dry_run = False):
    for task in client.find_tasks(filter = filter):
        old_set = set(task.tags)
        new_set = old_set.copy()
        new_set.difference_update(remove_tags)
        new_set.update(add_tags)
        if new_set != old_set:
            new_items = sorted(list(new_set))
            if verbose:
                print "Changing tags for %s from %s to %s" % (
                    task.name, ",".join(task.tags), ",".join(new_items))
            if not dry_run:
                client.update_task(
                    task_key = task.key, set_tags = new_items)

