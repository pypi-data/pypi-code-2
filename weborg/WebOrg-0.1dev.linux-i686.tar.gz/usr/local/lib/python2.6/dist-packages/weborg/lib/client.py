import subprocess
import os
import sys
import logging
import json
import re

import settings

log = logging.getLogger('client')
log.setLevel(level=logging.DEBUG)
handler = logging.FileHandler(settings.LOG_FILE)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
log.addHandler(handler)

def execute(cmd):
    env = os.environ
    env["LANG"] = 'en_US.utf8'
    full_cmd = settings.EMACS + " -q -batch -l ~/.emacs.d/70-org-mode.el -l " + settings.ORG_EL + " -eval '%s'" % cmd.encode('utf-8')
    p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
    stdout, stderr = p.communicate()
    log.debug('RPC: %s' % full_cmd)
    log.debug('Result: %s' % stdout)
    return stdout

def entry_index():
    cmd = '(entry-index)'
    return execute(cmd)

def entry_create(eid, jsonstr):
    cmd = '(entry-create "%s" "%s")' % (eid, re.escape(jsonstr))
    return execute(cmd)

def entry_new(eid):
    cmd = '(entry-new "%s")' % eid
    return execute(cmd)

def entry_update(eid, jsonstr):
    cmd = '(entry-update "%s" "%s")' % (eid, re.escape(jsonstr))
    return execute(cmd)

def entry_delete(eid):
    cmd = '(entry-delete "%s")' % eid
    return execute(cmd)

def entry_show(eid):
    cmd = '(entry-show "%s")' % eid
    return execute(cmd)

def entry_edit(eid):
    cmd = '(entry-edit "%s")' % eid
    return execute(cmd)
