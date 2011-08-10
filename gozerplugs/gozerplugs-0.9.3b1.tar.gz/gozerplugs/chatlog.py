# gozerplugs/chatlog.py
#

""" log irc channels to [hour:min] <nick> txt format 
The db backend expects the following table structure
$dbtable(time, network, target, nick, type, message)
"""

__copyright__ = 'this file is in the public domain'

from gozerbot.commands import cmnds
from gozerbot.callbacks import callbacks, jcallbacks
from gozerbot.database.alchemy import dbstart, create_session, trans, transfunc, create_all
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.generic import hourmin, rlog, lockdec
from gozerbot.irc.monitor import outmonitor
from gozerbot.xmpp.monitor import xmppmonitor
from gozerbot.plughelp import plughelp
from gozerbot.examples import examples
from gozerbot.irc.ircevent import Ircevent
from gozerbot.fleet import fleet
from gozerbot.tests import tests

import time, os, thread
from os import path
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime, Integer, Sequence

IrclogsBase = declarative_base()

class ChatLog(IrclogsBase):
    __tablename__ = 'chatlog'
    __table_args__ = {'useexisting': True}
    id = Column('id', Integer, Sequence('chatlog_id_seq', optional=True), primary_key=True)
    time = Column('time', DateTime, nullable=False, default=datetime.now)
    network = Column('network', String(256), nullable=False, default='')
    target = Column('target', String(256), nullable=False, default='')
    nick = Column('nick', String(256), nullable=False, default='')
    type = Column('type', String(256), nullable=False, default='')
    message = Column('message', Text, nullable=False, default='')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


plughelp.add('chatlog', 'log irc channels')

outlock = thread.allocate_lock()
outlocked = lockdec(outlock)

cfg = PersistConfig()
cfg.define('channels', [])
# format for logs. simple or supy are currently supported.
cfg.define('format', 'simple')
# basepath: the root of all logs.  None is $gozerbot-root/logs
cfg.define('basepath', '')
# msgs that should be logged start with this
cfg.define('nologprefix', '[nolog]')
# and are replaced with
cfg.define('nologmsg', '-= THIS MESSAGE NOT LOGGED =-')
# where do we write the logs too?
cfg.define('backend', 'file')
# db settings for db backend
cfg.define('dbtype', '')
cfg.define('dbname', '')
cfg.define('dbhost', '')
cfg.define('dbuser', '')
cfg.define('dbpasswd', '')
cfg.define('dburi', '')
logfiles = {}
backends = {}
stopped = False
db = None

 # Formats are defined here. simple also provides default values if values
 # are not supplied by the format, as well as format 'simple'. 
 # Parameters that should be supplied:
 #   * timestamp_format: format of timestamp in log files
 #     * all strftime vars supported.
 #   * filename: file name for log
 #     * var channel : full channel ie. #dunkbot
 #     * var channel_name : channel without '#' ie. dunkbot
 #   * event_filename: 
 #        if event_filename exists, then it will be used for
 #        logging events (seperate from chat)
 #     * var channel : full channel ie. #dunkbot
 #     * var channel_name : channel without '#' ie. dunkbot
 #   * separator: the separator between the timestamp and message
formats = {
    'simple': {
        'timestamp_format': '%Y-%m-%d %H:%M:%S',
        'basepath': None,
        'filename': 'logs/%%(network)s/simple/%%(target)s.%Y%m%d.slog',
        'event_prefix': '',
        'event_filename': 'logs/%%(network)s/simple/%%(channel_name)s.%Y%m%d.slog',
        'separator': ' | ',
    },
    'supy': {
        'timestamp_format': '%Y-%m-%dT%H:%M:%S',
        'filename': 'logs/%%(network)s/supy/%%(target)s/%%(target)s.%Y-%m-%d.log',
        'event_prefix': '*** ',
        'event_filename': None,
        'separator': '  ',
    }
}

# Get a format opt in the currently cfg'd format
def format_opt(name):
    simple_format = formats['simple']
    format = formats.get(cfg.get('format'), 'simple')
    opt = format.get(name, simple_format.get(name, None))
    return opt

def init():
    global stopped
    stopped = False
    callbacks.add('ALL', chatlogcb, prechatlogcb)
    jcallbacks.add('ALL', jabberchatlogcb, jabberprechatlogcb)
    outmonitor.add('chatlog', chatlogcb, prechatlogcb)
    xmppmonitor.add('chatlog-jabber', jabberchatlogcb, jabberprechatlogcb)
    return 1

def shutdown():
    global stopped
    stopped = True
    for file in logfiles.values():
        file.close()
    return 1

def timestr(dt):
    return dt.strftime(format_opt('timestamp_format'))

def write(m): 
    """m is a dict with the following properties:
      datetime
      type : (comment, nick, topic etc..)
      target : (#channel, bot etc..)
      txt : actual message
      network
    """
    backend_name = cfg.get('backend', 'file')
    backend = backends.get(backend_name, file_write)
    if m['txt'].startswith(cfg.get('nologprefix')):
        m['txt'] = cfg.get('nologmsg')
    backend(m)

def file_write(m):
    if stopped:
        return
    args = {
        'target': m.get('target'), 
        'network': m.get('network'), 
    }
    if args['target'].startswith('#'):
        args['channel_name'] = args['target'][1:]
    else: args['channel_name'] = args['target']
    f = time.strftime(format_opt('filename')) % args
    # if this is an event, and there is an event_filename, use that
    # instead of filename
    if m['type'] != 'comment':
        event_filename = format_opt('event_filename')
        if event_filename:
            f = time.strftime(event_filename) % args
        m['txt'] = '%s%s'%(m['event_prefix'], m['txt'])
    else:
        m['txt'] = '<%s> %s'%(m['nick'], m['txt'])

    # if there is a basepath specified, append it,
    # else it should go to a dir relative to the 
    # gozerbot dir.
    basepath = cfg.get('basepath')
    if basepath:
        f = path.join(basepath, f)

    # create dir if it doesn't exist
    dir = path.dirname(f)
    if not path.exists(dir):
        os.makedirs(dir)

    timestamp = timestr(m['datetime'])

    line = '%(timestamp)s%(separator)s%(txt)s\n'%({
        'timestamp': timestamp, 
        'separator': format_opt('separator'),
        'txt': m['txt'],
    })

    try:
        if logfiles.has_key(f):
            logfiles[f].write(line)
            logfiles[f].flush()
        else:
            rlog(5, 'chatlog', 'opening %s for logging'%(f))
            logfiles[f] = open(f, 'a')
            logfiles[f].write(line)
            logfiles[f].flush()
    except Exception, ex:
        rlog(10, 'chatlog', str(ex))

backends['file'] = file_write

def init_db():
    try:
        Session, engine = dbstart(mainconfig=cfg, base=IrclogsBase) 
    except:
        Session, engine = dbstart(base=IrclogsBase) 
    create_all('chatlog', base=IrclogsBase)
    return (Session, engine)

if cfg['backend'] == 'db':
    Session, engine = init_db()

def db_write(m):
    try:
        db = Session()
        db.begin()
        row = {
                'time' : m.get('datetime'),
                'network' : m.get('network'),
                'target' : m.get('target'),
                'nick' : m.get('nick'),
                'type' : m.get('type'),
                'message' : m.get('txt')
        }
        db.add(ChatLog(**row))
        db.commit()
    except Exception, e:
        rlog(10, 'chatlog', 'failed to log to db: %s'%(str(e)))
    
backends['db'] = db_write

def log(bot, ievent):
    m = {
        'datetime': datetime.now(),
        'separator': format_opt('separator'),
        'event_prefix': format_opt('event_prefix'),
        'network': bot.networkname,
        'nick': ievent.nick,
        'target': ievent.channel,
    }

    if ievent.cmnd == 'PRIVMSG':
        if ievent.txt.startswith('\001ACTION'):
            m.update({
                'type': 'action',
                'txt': '* %s %s'%(m['nick'], ievent.txt[7:-1].strip()),
            })
        else:
            m.update({
                'type': 'comment',
                'txt': '%s'%(ievent.origtxt),
            })
    elif ievent.cmnd == 'NOTICE':
        m.update({
            'type': 'notice',
            'target': ievent.arguments[0],
            'txt': "-%s- %s"%(ievent.nick, ievent.txt)
        })
    elif ievent.cmnd == 'TOPIC':
        m.update({
            'type': 'topic',
            'txt': '%s changes topic to "%s"'%(ievent.nick, ievent.txt),
        })
    elif ievent.cmnd == 'MODE':
        margs = ' '.join(ievent.arguments[1:])
        m.update({
            'type': 'mode',
            'txt': '%s sets mode: %s'%(ievent.nick, margs),
        })
    elif ievent.cmnd == 'JOIN':
        m.update({
            'type': 'join',
            'txt': '%s (%s) has joined'%(ievent.nick, ievent.userhost),
        })
    elif ievent.cmnd == 'KICK':
        m.update({
            'type': 'kick',
            'txt': '%s was kicked by %s (%s)'%(
                ievent.arguments[1], 
                ievent.nick, 
                ievent.txt
            ),
        })
    elif ievent.cmnd == 'PART':
        m.update({
            'type': 'part',
            'txt': '%s (%s) has left'%(ievent.nick, ievent.userhost),
        })
    elif ievent.cmnd in ('QUIT', 'NICK'):
        cmd = ievent.cmnd
        nick = cmd == 'NICK' and ievent.txt or ievent.nick
        if not bot.userchannels.has_key(nick.lower()):
            return
        for c in bot.userchannels[nick.lower()]:
            if [bot.name, c] in cfg.get('channels'):
                if c in bot.state['joinedchannels']:
                    if cmd == 'NICK':
                        m['txt'] = '%s (%s) is now known as %s'%(
                            ievent.nick, ievent.userhost, ievent.txt
                        )
                    else:
                        m['txt'] = '%s (%s) has quit: %s'%(
                            ievent.nick, ievent.userhost, ievent.txt
                        )
                    m.update({
                        'type': ievent.cmnd.lower(),
                        'target': c,
                    })
                    write(m)
        return
    if m.get('txt'):
        write(m)

def jabberlog(bot, ievent):
    if ievent.botoutput:
        chan = ievent.to
    else:
        chan = ievent.channel
    m = {
        'datetime': datetime.now(),
        'separator': format_opt('separator'),
        'event_prefix': format_opt('event_prefix'),
        'network': bot.networkname,
        'nick': ievent.nick,
        'target': chan,
    }
    if ievent.cmnd == 'Message':
            m.update({
                'type': 'comment',
                'txt': ievent.txt.strip(),
            })
    elif ievent.cmnd == 'Presence':
            if ievent.type == 'unavailable':
                m.update({
                    'type': 'part',
                    'txt': "%s left"%ievent.nick
                })
            else:
                m.update({
                    'type': 'join',
                    'txt': "%s joined"%ievent.nick
                })
    if m['txt']:
        write(m)

def prechatlogcb(bot, ievent):
    """Check if event should be logged.  QUIT and NICK are not channel
    specific, so we will check each channel in log()."""
    if not ievent.msg and [bot.name, ievent.channel] in \
            cfg.get('channels'):
        return 1
    if ievent.cmnd in ('QUIT', 'NICK'):
        return 1
    if ievent.cmnd == 'NOTICE':
        if [bot.name, ievent.arguments[0]] in cfg.get('channels'):
            return 1

def chatlogcb(bot, ievent):
    log(bot, ievent)

def jabberprechatlogcb(bot, ievent):
    if not ievent.groupchat:
        return 0
    if [bot.name, ievent.channel] in cfg.get('channels'):
        return 1

def jabberchatlogcb(bot, ievent):
    jabberlog(bot, ievent)

def handle_chatlogon(bot, ievent):
    chan = ievent.channel
    if [bot.name, chan] not in cfg.get('channels'):
        cfg['channels'].append([bot.name, chan])
        cfg.save()
        ievent.reply('chatlog enabled on (%s,%s)' % (bot.name, chan))
    else:
        ievent.reply('chatlog already enabled on (%s,%s)' % (bot.name, chan))

cmnds.add('chatlog-on', handle_chatlogon, 'OPER')
examples.add('chatlog-on', 'enable chatlog on <channel> or the channel \
the commands is given in', '1) chatlog-on 2) chatlog-on #dunkbots')
tests.add('chatlog-on', 'enabled')

def handle_chatlogoff(bot, ievent):
    try:
        cfg['channels'].remove([bot.name, ievent.channel])
        cfg.save()
    except ValueError:
        ievent.reply('chatlog is not enabled in (%s,%s)' % (bot.name, \
ievent.channel))
        return
    ievent.reply('chatlog disabled on (%s,%s)' % (bot.name, ievent.channel))

cmnds.add('chatlog-off', handle_chatlogoff, 'OPER')
examples.add('chatlog-off', 'disable chatlog on <channel> or the channel \
the commands is given in', '1) chatlog-off 2) chatlog-off #dunkbots')
tests.add('chatlog-off', 'disabled|not enabled')

plughelp.add('chatlog', """
chatlog can log chats to mutliple backends.  Currently, only the file and db 
backends are supported.  

If you are using the file backend, there are two 
related configuration points; format and basepath.  Format dictates how the
logs are output.  There are currently two supported formats; simple and supy.
supy emulates the output logs of the excellent supybot ircbot.  Simple, as 
the name applies is some what simpler, although it logs comments and all
other lines types into seperate files.  Please create a ticket if you would
like another format supported.   

If you are using the db backend, then you must specify the database 
parameters.  This follows the same convention as gozerbot itself.  The db-
prefixed parameters are the ones you are after.  The chatlog plugin does
not create an table for chatlogs, this is up to the owner.  The owner will
need to create a table named chatlog with (time, network, target, nick, 
type, message) fields.  If there is an id field, it should be auto 
incrementing.  It is suggested to put and index on (network, target). 
target is usually a channel name.  

nologprefix is used to allow private messages that won't be logged by the bot.
The will be replaced by nologmsg.  

If you are looking for a great way to display your logs on the web, consider 
the irclogs trac plugin.  
</shameless-plug>
""")
