# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from mekk.nozbe.nozbe import NozbeApi
import csv
from twisted.internet import defer

@defer.inlineCallbacks
def nozbe_to_csv(nozbe_client, csv_filename, include_completed = False):
    """
    Connects to given Nozbe account, grabs data and saves them to CSV file.

    @param nozbe_client: nozbe connector
    @param csv_filename: name of the output file
    @param include_completed: load finished actions too
    """
    assert(isinstance(nozbe_client, NozbeApi))

    out = csv.writer(open(csv_filename, 'w'))
    out.writerow([u'Action', u'Project', u'Context', 
                  u'Finished?', u'Next?', u'Delegated?', 
                  u'Due', u'Recurring'])

    print "Loading projects..."
    projects = yield nozbe_client.get_projects()
    if projects is None:
        projects = []
    print "   DONE."

    proj_hash_to_name = dict([ (p['hash'], p['name']) for p in projects ])

    print "Loading contexts"
    contexts = yield nozbe_client.get_contexts()
    if contexts is None:
        contexts = []
    print "   DONE."

    ctx_hash_to_name = dict([ (c['hash'], c['name']) for c in contexts ])

    print "Loading actions..."
    all_actions = yield nozbe_client.get_tasks()
    if all_actions is None:
        all_actions = []
    print "   DONE."

    if include_completed:
        print "Loading finished actions..."
        finished_actions = yield nozbe_client.get_completed_tasks()
        if finished_actions:
            all_actions.extend(finished_actions)
        print "   DONE."

    for action in all_actions:
        re_user = action['re_user']
        if re_user and re_user != "0":
            shared = "YES"
        else:
            shared = "NO"

        out.writerow([action['name'].encode("utf-8"), 
                      proj_hash_to_name[action['project_hash']].encode("utf-8"), 
                      ctx_hash_to_name.get(action.get('context_hash', ''), '').encode("utf-8"),
                      action['date'], 
                      action['next'] and "YES" or "NO", 
                      shared,
                      action['datetime'], 
                      nozbe_client.recur_label(action['recur']),
                      ])
