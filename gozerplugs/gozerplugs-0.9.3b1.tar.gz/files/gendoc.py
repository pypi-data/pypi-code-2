#! /usr/bin/env python
#
# Quick'n'dirty doc generator
#
# TODO:
#  * look for author in the hg heads
#  * map user<>full name in this file
#  * use gozerbot to actually process the output of the commands, if able
#

from gozerbot.generic import handle_exception, enable_logging, toascii, \
splittxt, strippedtxt
from gozerbot.threads.thr import start_new_thread
from gozerbot.plugins import plugins
from gozerbot.irc.ircevent import Ircevent
from gozerbot.examples import examples
from gozerbot.irc.bot import Bot
from gozerbot.users import users
from gozerbot.plughelp import plughelp
from gozerbot.commands import cmnds
from gozerbot.aliases import aliasreverse
from gozerbot.config import config, Config
from gozerbot.fleet import fleet
from gozerbot.redispatcher import rebefore, reafter
from gozerbot.database.alchemy import startmaindb
from gozerbot.eggs import loadeggs
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import time
donot = ['quit', 'reboot', 'jump']
config.load()
oldlevel = config['loglevel']
config['loglevel'] = 1000
enable_logging()
loadeggs('gozernest')
startmaindb()
cfg = Config()
bot = Bot(cfg)
bot.channels.setdefault('#test', {})
bot.channels.setdefault('#dunkbots', {})
bot.userhosts['dunker'] = 'bart@gozerbot.org'
bot.userhosts['test'] = 'test@test'
bot.server = 'localhost'
bot.port = 6667
bot.debug = True
fleet.addbot(bot)
plugins.regplugins()
time.sleep(5)

try:
    users.add('test', ['test@test', ], ['OPER', 'USER', 'QUOTE', 'MAIL'])
except Exception, ex:
    pass

try:
    users.setemail('test', 'bthate@gmail.com')
except Exception, ex:
    pass

def gendoc(f, output):
    base = os.path.basename(f).replace('.py', '')
    try:
        plugins.reload('gozerbot.plugs', base)
    except:
        try:
            plugins.reload('gozerplugs', base)
        except:
            pass
    if not plugins.plugs.has_key(base):
        print "no %s plugin found" % base
        return
    output.write('=' * (len(base)+2) + '\n')
    output.write(' %s ' % base.upper() + '\n')
    output.write('=' * (len(base)+2) + '\n')
    output.write("| \n" + '\n')
    output.write("about" + '\n')
    output.write("-----" + '\n')
    output.write("| \n" + '\n')
    try:
        author = plugins.plugs[base].__author__
        output.write(":author:  %s" % author.strip() + '\n')
    except AttributeError:
        output.write(":author:  Bart Thate <bthate@gmail.com>" + '\n')
    output.write(":contact: IRCNET/#dunkbots" + '\n')
    if 'gozerbot' in f:
        output.write(':distribution: core' + '\n')
    else:
        output.write(":distribution: http://gozerbot.org/gozerplugs" + '\n')
    try:
        license = plugins.plugs[base].__license__
        output.write(":license:  %s" % license.strip() + '\n\n')
    except AttributeError:
        output.write(":license: Public Domain" + '\n\n')
    output.write("| \n" + '\n')
    data = {'author': 'unknown', 'description': '', 'commands': [], 'examples': {}, 'descriptions': {}, 'callbacks': {}, 'aliases': {}, 'permissions': {}, 'options': {}}
    data['description'] = plughelp[base]
    cmndlist = []
    for j, z in cmnds.iteritems():
        if j in donot:
            continue
        if z.plugname == base:
            cmndlist.append(j)
    relist = []
    for reitem in rebefore.relist:
        if reitem.plugname == base:
            relist.append(reitem)
    for reitem in reafter.relist:
        if reitem.plugname == base:
            relist.append(reitem)
    cmndlist.sort()
    try:
        first = plugins.plugs[base].__gendocfirst__
        for i in first[::-1]: 
            try:
                cmndlist.remove(i)
            except ValueError:
                continue
            cmndlist.insert(0,i)
    except AttributeError:
        pass
    try:
        first = plugins.plugs[base].__gendoclast__
        for i in first[::-1]: 
            try:
                cmndlist.remove(i)
            except ValueError:
                continue
            cmndlist.append(i)
    except AttributeError:
        pass
    try:
        skip = plugins.plugs[base].__gendocskip__
        for i in skip[::-1]: 
            try:
                cmndlist.remove(i)
            except ValueError:
                continue
    except AttributeError:
        pass
    for command in cmndlist:
        data['commands'].append(command)
        alias = aliasreverse(command)
        data['options'][command] = cmnds.options(command)
        if alias:
            data['aliases'][command] = alias
        try:
            ex = examples[command]
        except Exception, exx:
            continue
        try:
            data['permissions'][command] = cmnds.perms(command)
        except: 
            pass
        data['examples'][command] = []
        exampleslist = re.split('\d\)', ex.example)
        for e in exampleslist:
            data['examples'][command].append(e.strip())
            data['descriptions'][command] = ex.descr
    output.write("description" + '\n')
    output.write( "-----------" + '\n')
    output.write( "| \n\n")
    output.write(data['description'] + '\n\n')
    try:
        doc = plugins.plugs[base].__doc__
        output.write("| \n" + '\n')
        doclist = doc.split('\n\n')
        for line in doclist:
            output.write(" %s" % line + '\n')
    except AttributeError:
        pass
    output.write("\n| \n" + '\n')
    output.write('commands' + '\n')
    output.write("--------" + '\n')
    output.write("| \n" + '\n')
    output.write("\n    :commands in this plugin: %s\n\n" % ' .. '.join(cmnds.getcommands(base)))
    output.write("| \n" + '\n')
    teller = 1
    for command in data['commands']:
        try:
            funcname = cmnds.getcommand(command).func.func_name
        except AttributeError:
            funcname = 'none'
        if data['aliases'].has_key(command):
            output.write('%s) *%s (%s) .. [%s]*' % (teller, command, data['aliases'][command], funcname) + '\n')
        else:
            output.write('%s) *%s .. [%s]*' % (teller, command, funcname) + '\n')
        if data['descriptions'].has_key(command):
            output.write('\n    :description: %s' % data['descriptions'][command] + '\n')
        if data['permissions'].has_key(command):
            output.write('\n    :permissions: %s' % ' .. '.join(data['permissions'][command]) + '\n')
        if data['options'].has_key(command):
             output.write("\n    :options: %s\n" % data['options'][command])
        if data['examples'].has_key(command):
            output.write('\n    :examples:' + '\n')
            for i in data['examples'][command]:
                if not i:
                     continue
                output.write('\n    ::\n\n        <user> !%s' % i.strip() + '\n')
                out = None
                try:
                    config['loglevel'] = 1000
                    out = bot.test(i.strip())
                    if not out:
                        output.write("        <output> none" + '\n')
                        continue
                    result = ' .. '.join(out)
                    result = result.replace('\002', '')
                    teller2 = 1
                    for j in splittxt(result, 50):
                        if teller2 > 10:
                            output.write('         - output trunked -' + '\n')
                            break
                        output.write('        <output> %s' % j + '\n')
                        teller2 += 1
                    output.write('\n\n')
                except Exception, ex:
                    handle_exception(short=True)
        teller += 1
    if not data['commands']:
        output.write("no commands in this plugin" + '\n')
    if relist:
        output.write("\nregular expressions" + '\n')
        output.write("-------------------" + '\n')
        output.write("| \n" + '\n')
        teller = 1
        for reitem in relist:
            output.write("%s) %s [%s]" % (teller, reitem.regex, reitem.func.func_name) + '\n')
            try:
                output.write("     " + reitem.func.__doc__ + '\n')
            except AttributeError:
                pass
            teller += 1
    output.write('\nfunctions\n')
    output.write('---------\n')
    output.write("\n    :functions implemented in this plugin: %s\n\n\n" % ' .. '.join(cmnds.getfuncnames(base)))

    output.flush()
    output.close()
    print "DONE %s" % f 

#config['loglevel'] = oldlevel

if __name__ == '__main__':
    threads = []
    try:
        f = open('doc' + os.sep + sys.argv[1].upper(), 'w')
        gendoc(sys.argv[1], f)
    except IndexError:
        for file in os.listdir(os.getcwd() + os.sep +'gozerbot' + os.sep + 'plugs'):
            if not file.endswith('.py') or '__init__' in file:
                continue
            f = open('doc' + os.sep + 'baseplugs' + os.sep + file[:-3].upper(), 'w')
            threads.append(start_new_thread(gendoc, (file, f)))
        for file in os.listdir(os.getcwd() + os.sep +'gozerplugs'):
            if not file.endswith('.py') or '__init__' in file:
                continue
            f = open('doc' + os.sep + 'gozerplugs' + os.sep + file[:-3].upper(), 'w')
            threads.append(start_new_thread(gendoc, (file, f)))
    for thread in threads:
        thread.join()
