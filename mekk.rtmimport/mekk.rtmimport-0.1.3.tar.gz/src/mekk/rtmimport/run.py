# -*- coding: utf-8 -*-

usage = """
Simple RememberTheMilk importer.

Importing Nozbe export file (obtained with nozbetool export --json=<file>):

    %prog --nozbe-json=nozbe.json  [--verbose] [--dry-run]
"""

import webbrowser
from base64 import decodestring as __
import xml.etree.ElementTree as ElementTree
from rtmapi import Rtm
import keyring
import simplejson
from rtm_updater import RtmUpdater

API="Y2IwYzQ1ZGUwNDI5NTFiNDJjYjUzYzhmNjI0NjliMjk="
SEC="Y2QyODU4Yzk0ZTQ2ZjdhNg=="

def parse_options():
    from optparse import OptionParser
    opt_parser = OptionParser(usage=usage)
    opt_parser.add_option("-n", "--nozbe-json",
                          action="store", type="string", dest="nozbe_json",
                          help="The name of .json file exported using nozbetool export --json ")
    opt_parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose",
                          help="Print diagnostic messages")
    opt_parser.add_option("-d", "--dry-run",
                          action="store_true", dest="dry_run",
                          help="Don't execute anything, just check input and (if verbose) print planned actions")
                          
    opt_parser.set_defaults(verbose = False, dry_run = False)
    (opts, args) = opt_parser.parse_args()

    if not opts.nozbe_json:  # Alternative formats can be considered in future
        opt_parser.error("Operation not selected (--nozbe-json expected)")

    return opts

def grab_access_token():
    token = keyring.get_password("rtmimport", "default-user")
    api = Rtm(__(API), __(SEC), "write", token)
    
    if not api.token_valid():
        url, frob = api.authenticate_desktop()
        print "Opening browser window to authenticate the script"
        webbrowser.open(url)
        raw_input("Press Enter once you authenticated script to access your RememberTheMilk account.")
        api.retrieve_token(frob)
        keyring.set_password("rtmimport", "default-user", api.token)
        print "Access token received and saved for future use"

    return token
    
def run():

    opts = parse_options()
    token = grab_access_token()
    if not token:
        raise Exception("Failed to grab working access token. Check API key")
    api = Rtm(__(API), __(SEC), "write", token)
    updater = RtmUpdater(api)

    if opts.nozbe_json:
        data = simplejson.load(open(opts.nozbe_json),
                               encoding = "utf-8")

        from nozbe_import import import_nozbe_actions

        import_nozbe_actions(updater, actions = data['actions'], notes = data['notes'],
                             verbose = opts.verbose, dry_run = opts.dry_run)
