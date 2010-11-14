# -*- coding: utf-8 -*-

import re
from collections import defaultdict

# Mapping nozbe codes to rtm codes
RECUR_2_MILK = {
    '0' : None,
    '1' : u"Every day",
    '2' : u"Every weekday",
    '3' : u"Every week",
    '4' : u"Every 2 weeks",
    '5' : u"Every month",
    '6' : u"Every 6 months",
    '7' : u"Every year",
    }

# Name used for "preserve notes" task
NOTE_TASK_NAME = u"Save this note"

re_badchars = re.compile(u"[^-\w]+", re.UNICODE)
def context_to_tag(ctx_name):
    name = re_badchars.sub("-",ctx_name)
    return u"@" + name

#print context_to_tag("Ala ma kota")
#print context_to_tag(u"Zażółć gęślą jaźń")
#print context_to_tag(u"Komp/Platon")


def import_nozbe_actions(rtm_client, actions, notes, verbose, dry_run):

    for action in actions:
        name = action['name']
        project_name = action['project_name']

        completed = (str(action.get('completed', 0)) == "1")
        if completed:
            #print (u"Skipping completed action from project %s: %s" % (project_name, name)).encode('utf-8')
            continue

        if dry_run or (project_name == "Inbox"):
            list_id = None
        else:
            list_id = rtm_client.find_or_create_list(project_name).id

        completed = (str(action.get('completed', 0)) == "1")
                
        tags = []
        if action['context_name']:
            tags.append(context_to_tag(action['context_name']))
        if str(action['next']) == "1":
            tags.append("Next")

        due_date = None  # ...
        if action['datetime']:
            due_date = action['datetime']

        repeat = None
        if not completed: # avoid resurrecting old tasks
            repeat = RECUR_2_MILK[ action['recur']  ]

        estimate = None  # 3 days 2 hours 10 minutes
        at = str(action['time'])
        if at != "0":
            estimate = at + " minutes"

        if verbose:
            intro = (completed and "Saving completed task" or "Creating new task")
            print (u"%(intro)s on list %(project_name)s\n   Task name: %(name)s \n   Repeat: %(repeat)s, due: %(due_date)s, estimate: %(estimate)s, tags: %(tags)s" % locals()).encode('utf-8')

        if not dry_run:
            rtm_client.create_task(
                task_name = name,
                list_id = list_id,
                tags = tags,
                due_date = due_date,
                estimate = estimate,
                repeat = repeat,
                completed = completed)
           # priority, url, notes - unused
    
    # First group notes by project
    project_notes = defaultdict(lambda: [])
    for note in notes:
        project_notes[note['project_name']].append(
            (note['name'], note['body'])
            )

    # ... and save them
    for project_name, here_notes in project_notes.iteritems():
        if dry_run or (project_name == "Inbox"):
            list_id = None
        else:
            list_id = rtm_client.find_or_create_list(project_name).id
        task_name = NOTE_TASK_NAME
        if verbose:
            print "Creating preserve note task on list %(project_name)s. Task name: %(task_name)s\n" % locals()
            print "Notes bound:\n"
            for (title, body) in here_notes:
                print title, "\n"
                print "   ", body.replace("\n", "\n    "), "\n"
        if not dry_run:
            rtm_client.create_task(
                task_name = task_name,
                list_id = list_id,
                tags = ["Note"],
                due_date = "today",
                notes = here_notes)
