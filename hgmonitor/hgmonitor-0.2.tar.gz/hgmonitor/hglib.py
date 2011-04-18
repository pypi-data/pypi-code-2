# -*- coding: utf-8 -*-
# Pigs need libraries too

import autfunc
import re
import os

class ChangeSet:
    def __init__(self):
        self.parents = []
        self.label = ""
        self.rev = ""
        self.node = ""
        self.summary = ""

template = """NEW_CHANGESET
changeset:{rev}
node:{node}
users:{author}
date:{date|date}
summary:{desc|firstline}"""
        
# Check for outgoing things
def parse_log_output(output,strip_merge=True):
    lines = map(lambda x: x.strip(), output.split("\n"))
    changesets = []
    for l in lines:
        if l[:10] == "changeset:":
            changesets.append(ChangeSet())
        if l[:10] == "changeset:":
            changesets[-1].label = l[13:]
            changesets[-1].rev = l[13:].split(':')[0]
            changesets[-1].node = l[13:].split(':')[1]
        if l[:7] == "parent:":
            changesets[-1].parents.append(l[13:])
        if l[:8] == "summary:":
            changesets[-1].summary = l[13:]

    if strip_merge:
        return [c for c in changesets if len(c.parents) <= 1]
    else:
        return changesets

def is_repo(repo):
    if os.path.exists(repo):
        hog_box = os.path.join( repo, ".hg" )
        if os.path.exists( hog_box ):
            return True
    return False

def find_outgoing( repo, strip_merge = False ):
    assert is_repo(repo), "The path %s does not contain a hg clone." % repo

    output={}
    autfunc.run2("hg", "-R \"%s\" outgoing" % (repo,), output=output)
    return parse_log_output(output["StdOut"], strip_merge)

def shelved_changes( repo ):
    assert is_repo(repo), "The path %s does not contain a hg clone." % repo

    shelf_file = os.path.join( repo, ".hg", "shelve" )
    if os.path.exists(shelf_file):
        mod_files = []
        f = open(shelf_file,"r").read()
        r = re.compile("diff --git a/(.*) b/(.*)")
        for m in r.finditer(f):
            if m.group(1) == m.group(2):
                mod_files.append(m.group(1))
            else:
                mod_files.append( "A file is modified that I couldn't parse" )
        return mod_files
    else:
        return []

def stat_parse(status_output):
    lines = status_output.split('\n')
    lines = [(l[0], l[2:].strip('\r\n')) for l in lines if l.strip('\r\n ') != ""]
    return [l for l in lines if l[0] != "?"]

def local_uncommitted(repo):
    assert is_repo(repo), "The path %s does not contain a hg clone." % repo

    output={}
    autfunc.run2("hg", "-R \"%s\" status" % (repo,), output=output)

    lines = output["StdOut"].split('\n')[:-1]
    lines = [(l[0], l[2:].strip('\r\n')) for l in lines]
    return [l for l in lines if l[0] != "?"]

def attic_files(repo):
    assert is_repo(repo), "The path %s does not contain a hg clone." % repo

    mq_dir = os.path.join( repo, ".hg", "attic" )
    if os.path.exists(mq_dir):
        l = [f for f in os.listdir(mq_dir) if not os.path.isdir(f)]
        return filter(lambda x: x!=".current" and x!=".applied" and x!=".hgignore", l)
    else:
        return []

def mq_files(repo):
    assert is_repo(repo), "The path %s does not contain a hg clone." % repo

    mq_dir = os.path.join( repo, ".hg", "patches" )
    if os.path.exists(mq_dir):
        l = [f for f in os.listdir(mq_dir) if not os.path.isdir(f)]
        return filter(lambda x: x!="status" and x!="series" and x!=".hgignore", l)
    else:
        return []

def default_push(repo):
    lines = open( os.path.join( repo, ".hg", "hgrc" ), "r" ).readlines()
    lines = [l.strip('\r\n') for l in lines if l.strip('\r\n') != ""]
    if lines[0] == '[paths]':
        match = re.match("default *= *(.*)",lines[1])
        if match:
            return match.group(1)
    return None

# this is not technically correct
# you can specify different pull & push locations and so the functions should return the correct ones ... we'll get to that when we need it.
default_pull = default_push

def recent_logs(repo,max_entries=45):
    assert is_repo(repo), "The path %s does not contain a hg clone." % repo

    output={}
    autfunc.run2("hg", "-R \"%s\" log -l %i" % (repo,max_entries), output=output)
    return parse_log_output(output["StdOut"])
