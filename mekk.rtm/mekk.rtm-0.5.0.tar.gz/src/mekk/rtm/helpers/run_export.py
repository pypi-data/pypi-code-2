# -*- coding: utf-8 -*-

usage = """
Simple RememberTheMilk data exporter.

Exporting data (lists and tasks) to JSON file:

    %prog --json=myrtm.json

   (in this case data are saved in the same format in which
    RememberTheMilk API provides them, just wrapped in separate
    fields for lists and tasks)

Exporting data (tasks) to CSV file:

    %prog --csv=myrtm.csv

Exported data can be narrowed using "--filter" clause, for example

    %prog --json=myrtm.json --filter="tag:Work and status:incomplete"

If filter is not set, "status:incomplete" is assumed.

"""

from connect import create_rtm_client

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(usage=usage)
    opt_parser.add_option("-j", "--json",
                          action="store", type="string", dest="json",
                          help="The name of .json file being exported")
    opt_parser.add_option("-c", "--csv",
                          action="store", type="string", dest="csv",
                          help="The name of .csv file being exported")
    opt_parser.add_option("-f", "--filter",
                          action="store", type="string", dest="filter",
                          help="Data filter (RTM query syntax)")
    opt_parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose",
                          help="Print diagnostic messages")
                          
    opt_parser.set_defaults(verbose = False)
    opt_parser.set_defaults(filter = "status:incomplete")
    (opts, args) = opt_parser.parse_args()

    if not (opts.json or opts.csv):
        opt_parser.error("Operation not selected (--json=filename or --csv=filename expected)")
    return opts

def run():

    opts = parse_options()
    client = create_rtm_client()

    if opts.csv:
        from mekk.rtm.exporters.csv import csv_export
        csv_export(client, opts.csv, opts.filter)
    if opts.json:
        from mekk.rtm.exporters.json import json_export
        json_export(client, opts.json, opts.filter)

