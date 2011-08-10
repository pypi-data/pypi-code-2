# plugs/upgrade.py
#
#

__copyright__ = 'this file is in the public domain'

from gozerbot.aliases import aliasset
from gozerbot.fleet import fleet
from gozerbot.plugins import plugins
from gozerbot.commands import cmnds
from gozerbot.examples import examples
from gozerbot.generic import reboot_stateful, gozerpopen, lockdec, \
handle_exception
from gozerbot.eventhandler import mainhandler
from gozerbot.plughelp import plughelp
from gozerbot.config import config
from gozerbot.utils.lockmanager import lockmanager
from gozerbot.partyline import partyline
import os, os.path, time

plughelp.add('upgrade', "do a mercurial hg pull -u and see if \
we need to reboot .. if only plugins are updated we don't need to reboot \
because we can reload them")

def gethgrev(path=None):
    rev = None
    try:
        if not path:
            proces = gozerpopen(['hg', 'tip'])
        else:
            proces = gozerpopen(['hg', 'tip', '-R%s' % path])
        rev = int(proces.fromchild.readlines()[0].split(':')[1].strip())
        proces.close()
    except (OSError, IndexError):
        return rev
    except Exception, ex:
        handle_exception()
    return rev

def handle_hgupgrade(bot, ievent, silent=None, path=None):
    """ upgrade .. do a mercurial pull -u .. see if we need to reboot \
        otherwise reload plugins """
    if not path:
         path = '.'
    startrev = gethgrev(path)
    if not startrev:
        ievent.reply("can't fetch current revision")
        return
    ievent.reply('upgrading from revision %s' % str(startrev))
    args = ['hg', 'pull', '-u', '-R%s' % path]
    userargs = []
    try:
        proces = gozerpopen(args, userargs)
    except Exception, ex:
        ievent.reply('error running popen: %s' % str(ex))
        return
    nochange = 0
    lines = proces.fromchild.readlines()
    proces.close()
    res = []
    for i in lines:
        if 'abort: error:' in i:
            ievent.reply('failed to update ==>  %s' % i)
            return
        if 'no changes' in i:
            nochange = 1
        res.append(i.strip())
    if nochange:
        ievent.reply('no changes')
        return
    else:
        not silent and ievent.reply(' .. '.join(res))
    rev = gethgrev(path)
    ievent.reply("new revision is %s" % rev)
    args = ['hg', 'diff', '-r%s' % startrev, '-R%s' % path]
    try:
        proces = gozerpopen(args)
    except Exception, ex:
        ievent.reply('error running popen: %s' % str(ex))
        return
    data = proces.fromchild.readlines()
    returncode = proces.close()
    if returncode != 0:
        ievent.reply("can't run hg diff")
        return
    files = []
    plugs = []
    needreboot = 0
    for i in data:
        if i.startswith('+++') or i.startswith('---'):
            if len(i.split()) < 2:
                continue
            filename = '%s' % os.sep
	    filename = filename.join(i.split()[1].split(os.sep)[1:])
            if filename == 'dev/null':
                continue
            if filename not in files:
                files.append(filename)
            if not filename.endswith('.py'):
                continue
            if filename.startswith('gozerbot') and not 'plugs' in filename: 
                needreboot = 1
            elif filename.find('plugs') != -1 or path == 'gozerplugs':
                if filename not in plugs:
                    plugs.append(filename)
    not silent and ievent.reply('files: ' + ' '.join(files))
    summary = []
    args = ['hg', 'log', '-r%s:%s' % (rev, startrev+1), '-R%s' % path]
    try:
        proces = gozerpopen(args)
    except Exception, ex:
        ievent.reply('error running popen: %s' % str(ex))
        return
    data = proces.fromchild.readlines()
    returncode = proces.close()
    if returncode == 0:
        for i in data:
            if i.startswith('summary:'):
                summary.append(i.split('summary:')[1].strip())
        not silent and ievent.reply("summaries: %s" % ' .. '.join(summary))
    if needreboot:
        ievent.reply('rebooting')
        time.sleep(4)
        try:
            plugins.exit()
            fleet.save()
        finally:
            time.sleep(1)
            mainhandler.put(0, reboot_stateful, bot, ievent, fleet, partyline)
            return
    config.load()
    if not plugs:
        ievent.reply('nothing to reload')
        return
    ievent.reply("reloading %s" %  " .. ".join(plugs))
    failed = plugins.listreload(plugs)
    if failed:
        ievent.reply("failed to reload %s" % ' .. '.join(failed))
        return
    else:
        ievent.reply('done')

cmnds.add('upgrade-hg', handle_hgupgrade, ['OPER', 'UPGRADE'])
examples.add('upgrade-hg', 'do a mercurial upgrade', 'upgrade-hg')

def handle_upgradesilent(bot, ievent):
    """ do a 'silent' upgrade """
    if ievent.rest == 'gozerplugs':
        path = 'gozerplugs'
    else:
        path = None
    lockmanager.acquire('up')
    try:
        handle_hgupgrade(bot, ievent, True, path)
    except Exception, ex: 
        handle_exception()
    lockmanager.release('up')
    return
    
cmnds.add('upgrade', handle_upgradesilent, ['OPER', 'UPGRADE'])
examples.add('upgrade', 'do a mercurial upgrade', \
'upgrade')
aliasset('upgrade-plugs', 'upgrade gozerplugs')

def handle_upgradeloud(bot, ievent):
    """ do a verbose upgrade """
    if ievent.rest == 'gozerplugs':
        path = 'gozerplugs'
    else:
        path = None
    lockmanager.acquire('up')
    try:
        handle_hgupgrade(bot, ievent, False, path)
    except Exception, ex: 
        handle_exception()
    lockmanager.release('up')
    return

cmnds.add('upgrade-loud', handle_upgradeloud, ['OPER', 'UPGRADE'])
examples.add('upgrade-loud', 'do a mercurial upgrade', 'upgrade-loud')
