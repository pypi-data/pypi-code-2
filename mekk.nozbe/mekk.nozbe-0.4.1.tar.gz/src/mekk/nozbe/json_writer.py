# -*- coding: utf-8 -*-
# (c) 2008, Marcin Kasperski

from mekk.nozbe.nozbe import NozbeApi
from twisted.internet import defer
import simplejson
import codecs

@defer.inlineCallbacks
def nozbe_to_json(nozbe_client, json_filename, include_completed = False):
    """
    Connects to given Nozbe account, grabs data and saves them to JSON file.

    @param nozbe_client: nozbe connector
    @param json_filename: name of the output file
    @param include_completed: load finished actions too
    """
    assert(isinstance(nozbe_client, NozbeApi))

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
        for fa in finished_actions:
            fa['completed'] = 1
        if finished_actions:
            all_actions.extend(finished_actions)
        print "   DONE."

    for action in all_actions:
        re_user = action['re_user']
        if re_user and re_user != "0":
            shared = "YES"
        else:
            shared = "NO"

        action['project_name'] = proj_hash_to_name[action['project_hash']]
        action['context_name'] = ctx_hash_to_name.get(action.get('context_hash', ''))
        action['recur_desc'] = nozbe_client.recur_label(action['recur'])

    print "Loading notes..."
    notes = yield nozbe_client.get_notes()
    if notes is None:
        notes = []
    print "   DONE."

    output = codecs.open(json_filename, "w", encoding = "utf-8")
    simplejson.dump(
        dict(projects = projects, contexts = contexts, actions = all_actions, notes = notes),
        output,
        sort_keys = True,
        indent = 4,
        )
    output.close()
