# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

usage = """
Nozbe command-line utilities.

Exporting Nozbe projects and tasks as CSV file:

    %prog export --csv=file.csv --user=YourNick

or as JSON file:

    %prog export --json=file.json --user=YourNick

To include completed actions too:

    %prog export --csv=file.csv --user=YourNick --completed

or

    %prog export --json=file.json --user=YourNick --completed

"""

OPERATIONS = [ 'export' ]

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(
                              usage=usage)
    #opt_parser.add_option("-k", "--key",
    #                      action="store", type="string", dest="key",
    #                      help ="Your Nozbe API key (see bottom of http://www.nozbe.com/account/extras)")
    opt_parser.add_option("-x", "--csv",
                          action="store", type="string", dest="csv",
                          help="The name of the output CSV file")
    opt_parser.add_option("-j", "--json",
                          action="store", type="string", dest="json",
                          help="The name of the output JSON file")
    opt_parser.add_option("-u", "--user",
                          action="store", type="string", dest="user",
                          help="Your Nozbe username (or email)")
    opt_parser.add_option("-c", "--completed",
                          action="store_true", dest = "completed",
                          help = "Include completed tasks (not downloaded by default)")
    opt_parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose",
                          help="Print diagnostic messages")
    opt_parser.add_option("-d", "--devel",
                          action="store", type="string", dest="devel",
                          help="Use development installation. Give --devel=user,pwd (http auth for devel site)")
    opt_parser.set_defaults(verbose = False, completed = False)
    (opts, args) = opt_parser.parse_args()

    if not len(args) == 1:
        opt_parser.error("Operation not selected (" + ", ".join(OPERATIONS) + ")")
    operation = args[0]

    if not opts.user:
        opt_parser.error("This operation requires --user=<your-nozbe-username>")

    if opts.devel:
        import re
        m = re.match("^([^,]+),([^,]+)$", opts.devel)
        if not m:
            opt_parser.error("Bad syntax for devel option (expected user,pwd)")
        opts.devel = dict(user = m.group(1), password = m.group(2))

    if operation == "export":
        if not (opts.csv or opts.json):
            opt_parser.error("This operation requires --csv=<created-csv-file>" or "--json=<created-json-file>")

    return operation, opts

operation, options = parse_options()

from mekk.nozbe import NozbeKeyringConnection, CachingNozbeApi
from mekk.nozbe.csv_writer import nozbe_to_csv
from mekk.nozbe.json_writer import nozbe_to_json
from twisted.internet import reactor, defer
import logging
logging.basicConfig(level = (options.verbose and logging.DEBUG or logging.WARN))

@defer.inlineCallbacks
def main():
    try:
        connection = NozbeKeyringConnection(username = options.user, devel = options.devel)
        yield connection.obtain_api_key()
        api = CachingNozbeApi(connection)
        if operation == "export":
            if options.csv:
                yield nozbe_to_csv(api, options.csv, options.completed)
                print "CSV file saved to %s" % options.csv
            if options.json:
                yield nozbe_to_json(api, options.json, options.completed)
                print "JSON file saved to %s" % options.json
    except Exception, e:
        if options.verbose:
            raise
        else:
            print "Failure:", e
    finally:
        reactor.stop()

def run():
    reactor.callLater(0, main)
    reactor.run()

if __name__ == "__main__":
    run()
