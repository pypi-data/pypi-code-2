#!/usr/bin/env python
# coding: utf-8
'''
    DzenStatus

    A script for making nice statusbars with dzen2
'''
from __future__ import print_function
import sys
import os
import time
from select import poll, POLLIN
from os import path
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.add_section('general')
config.set('general', 'plugin_dir', '~/.dzenstatus/plugins')
config.set('general', 'order', '')
config.set('general', 'dzen_path', 'dzen2')
config.set('general', 'dzen_opts', '-dock')
config.set('general', 'min_timeout', '1')

CONFIG_FILENAME = path.expanduser('~/.dzenstatus/config.ini') 

n = config.read(CONFIG_FILENAME)
if not n:
    print("WARNING: No user config found in %r, this will be pretty useless." % CONFIG_FILENAME, file=sys.stderr)

# A mapping of enabled plugin results, so as to be able to print a new line
# without updating all values.
results = {}

ALWAYS_UPDATE = lambda n, lu : True
NEVER_UPDATE = lambda n, lu : False

class UPDATE_ONCE(object):
    def __init__(self):
        self.updated = False
    def __call__(self, now, last_update):
        if not self.updated:
            self.updated = True
            return True
        return False


def timeout_update(n):
    '''
        Create an update predicate for a simple timeout value.  Not terribly
        performant, but adequate.
    '''
    def updatep(now, last_update):
        diff = now - last_update
        if diff > n: 
            return True

        for i in range(last_update, now):
            if i % n == 0:
                return True
        else:
            return False
    return updatep

# Some globals.  components holds the full list of configured instances of
# plugins, order holds the list of displayed plugin instances, which may
# repeat.
components = []
order = []

def backtick(command):
    '''
        Simple function that acts like a reasonably safe "backtick" operator.
    '''
    from subprocess import Popen, PIPE
    proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(None)
    if proc.returncode:
        return "FAIL: %s" % err
    return out.strip()

last_update = 0
def update(now):
    '''
        Repopulates the results dictionary with up-to-date outputs.

        Does not change the displayed value if the result of the update for a
        plugin is false.  If a plugin throws an exception, it is caught and the
        traceback is printed to stderr.  A simple ERROR: [name] is placed into
        the output to notify you that something went wrong.  
    ''' 
    global last_update

    for name, updatep, func in components:
        if updatep(now, last_update):
            try:
                r = func()
                if r:
                    results[name] = r
            except Exception:
                import traceback
                print(traceback.format_exc(), file=sys.stderr)
                results[name] = "^fg(red)ERROR: " + name + "^fg()"
    
    last_update = now

def print_line(f):
    ''' responsible for pushing the results dict to the output stream.  flushes
    the output stream on completion. '''
    for part in order:
        if part in results and results[part]:
            f.write(results[part])
    f.write("\n")
    f.flush()

def load_plugins():
    '''
        Uses pkg_resources to load all defined entry_points for "dzenstatus.plugins".

        Then looks in the configuration for what plugins to instantiate and
        builds the components and order lists.

        (Searches the plugin_dir defined in the config file for distributions
        containing the "dzenstatus.plugins" entry_point)
    '''
    from pkg_resources import iter_entry_points, working_set
    from pkg_resources import Environment

    distributions, errors = working_set.find_plugins(
            Environment(config.get('general', 'plugin_dir'))
    )

    for d in distributions:
        working_set.add(d)

    if errors:
        print("Had errors loading plugins: ", errors, file=sys.stderr)

    plugin_types = {}
    for ep in working_set.iter_entry_points('dzenstatus.plugins.v1'):
        plugin = ep.load()
        plugin_types[ep.name] = plugin

    sections = config.sections()
    sections.remove('general')
    for section in sections:
        conf = dict(config.items(section))
        conf['name'] = section
        try:
            plugin = plugin_types[conf['plugin']]
            components.append( plugin(conf) )
        except KeyError:
            import traceback
            traceback.print_exc()
            raise Exception("Plugin missing from config for section %r" % section)

    for section in config.get('general', 'order').split(', '):
        order.append(section)

def main(output=sys.stdout):
    global ready_fds        # Better way to do this? I don't like globals.
    load_plugins()

    # Set up polling for read_fd plugin, only plugin that couldn't be
    # implemented as an external plugin.
    inready = poll()
    for fd in polled_fds:
        inready.register(fd, POLLIN)

    min_interval = config.getint('general', 'min_timeout')

    for part in order:
        if part not in [ x[0]   for x in components ]:
            raise Exception("%s is not configured but included in order!" % part)

    while True:
        update(int(time.time()))
        print_line(output)

        # Used by the read_fd plugin to know when to read.
        ready_fds = inready.poll(min_interval*1000)

def main_pipe():
    return main()

def main_run_dzen():
    from subprocess import Popen, PIPE
    dzen_cmd = [ config.get('general', 'dzen_path') ] + config.get('general', 'dzen_opts').split()
    dzen = Popen(dzen_cmd, shell=False, stdin=PIPE)
    return main(dzen.stdin)

def plugin_static(config):
    '''
        The static text plugin, as simple as it gets, never recomputed.

        Name: static
        Parameters:
            contents: the text to be displayed
    '''
    return (config['name'], UPDATE_ONCE(), lambda: config['contents'])

ready_fds = []
polled_fds = []
def plugin_read_fd(config):
    '''
        The read_fd plugin reads *lines* from a file (or named fifo) and
        displays the last line read.
        
        Updates occur immediately when new lines are available due to the use
        of poll()

        Name: read_fd
        Parameters:
            file: the path to the file / fifo to read.
    '''
    class LBNBFDReader(object):
        def __init__(self, filename, line_limit):
            self.line_limit = line_limit
            
            # Prevent from blocking if a FIFO.
            self.fd = os.open(path.expanduser(filename), os.O_RDWR) 
            self.line_buf = ""
            self.complete_line = ""

            polled_fds.append(self.fd)  

        def __call__(self):
            try:
                t = os.read(self.fd, 4096)
                if t:
                    self.line_buf += t
                    self.complete_line = self.line_buf.splitlines()[-1]
                    if len(self.line_buf.splitlines()) > 1 and self.line_buf.endswith('\n'):
                        self.line_buf = '\n'.join(self.line_buf.splitlines()[-2:])  + '\n'
            except OSError as e:
                # Is EAGAIN ever going to happen without O_NONBLOCK/O_NDELAY?
                if e.errno != 11: # EAGAIN
                    raise

            # If longer than line_limit, truncate to limit and add elipsis.
            if self.complete_line and self.line_limit != 0 and len(self.complete_line) > self.line_limit:
                self.complete_line = self.complete_line[:self.line_limit] + '...'

            return self.complete_line.strip()

    reader = LBNBFDReader(config['file'], int(config.get('line_limit', 0)))
    def updatep(now, last_update):
        return (reader.fd, 1) in ready_fds

    return (config['name'], updatep, reader)

def plugin_gmail_feed(config):
    '''
        The gmail_feed plugin reads the number of mails from a Gmail account in
        a particular label or the inbox (an empty label).

        Name: gmail_feed
        Parameters:
            label: The label (folder) to check.  Leave empty for INBOX.
            timeout: The timeout between updates to this plugin.
            icon: The dzen supported icon to show for this mailbox.
            username: The gmail username.
            pwd_file: The file containing the password for the account (no newline at EOF).
            calmcolor: The color to use when there is no new mail.
            alertcolor: The color to use when there *is* new mail.
    '''
    def do_check_gmail_feed():
        #========================================================================
        #      Copyright 2007 Raja <rajajs@gmail.com>
        #
        #      This program is free software; you can redistribute it and/or modify
        #      it under the terms of the GNU General Public License as published by
        #      the Free Software Foundation; either version 2 of the License, or
        #      (at your option) any later version.
        #
        #      This program is distributed in the hope that it will be useful,
        #      but WITHOUT ANY WARRANTY; without even the implied warranty of
        #      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        #      GNU General Public License for more details.
        #
        #      You should have received a copy of the GNU General Public License
        #      along with this program; if not, write to the Free Software
        #      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
        #==========================================================================
        
        # ======================================================================
        # Modified from code originally written by Baishampayan Ghose
        # Copyright (C) 2006 Baishampayan Ghose <b.ghose@ubuntu.com>
        # ======================================================================
        
        
        try:
            import urllib.request, urllib.parse, urllib.error             
        except ImportError:
            import urllib

        import feedparser         
        
        
        ##################   Edit here      #######################
        
        #pwd = xxxx                            # pwd stored in script
        _pwdfile = config['pwd_file']          # pwd stored in a file
        _username = config['username']
        _calmcolor = config['calmcolor']
        _alertcolor = config['alertcolor']
        _maxmails = 1  # maximum new mails to show
        _maxwords = 3  # maximum words to show in each mail header
        _icon = config['icon']
        _url = 'https://mail.google.com/gmail/feed/atom/' + config['label']
        
        ###########################################################
        
        class GmailRSSOpener(urllib.FancyURLopener):
            '''Logs on with stored password and username
               Password is stored in a hidden file in the home folder'''
            
            def prompt_user_passwd(self, host, realm):
                #uncomment line below if password directly entered in script.
                pwd = open(_pwdfile).read()
                return (_username, pwd)
        
        def auth():
            '''The method to do HTTPBasicAuthentication'''
            opener = GmailRSSOpener()
            f = opener.open(_url)
            feed = f.read()
            return feed
        
        def showmail(feed):
            '''Parse the Atom feed and print a summary'''
            atom = feedparser.parse(feed)
            newmails = len(atom.entries)
            if newmails == 0:
                title = "^i(%s) ^fg(%s)0^fg()" % (_icon, _calmcolor)
            else:
                title = "^i(%s)^fg(%s)%s^fg()" % (_icon, _alertcolor,newmails)
            
            return title

        feed = auth()
        return showmail(feed)
    return (config['name'], timeout_update(int(config['timeout'])), do_check_gmail_feed)

def plugin_wifi(config):
    '''
        The wifi plugin shows the connected/associated ESSID and the signal strength.

        Name: wifi
        Parameters:
            timeout: Number of seconds between updates.
            iface:  The network interface to monitor.
            good_color: The color to use when signal is good.
            bad_color: The color to use when signal is bad.
    '''
    def do_wifi():
        quality = int(open("/sys/class/net/%s/wireless/link"%config['iface']).read())
        essid = os.popen("/sbin/iwconfig %s | head -1 | cut -d: -f2"%config['iface']).read().strip()

        if quality < 50.0:
            number_color = config['bad_color']
        else:
            number_color = config['good_color']

        return "%s (^fg(%s)%2d^fg()%%)" % (essid, number_color, quality)
    return (config['name'], timeout_update(int(config['timeout'])), do_wifi)

def plugin_battery(config):
    '''
        The battery plugin shows an icon indicating AC/Battery state and
        battery charge percentage.

        Name: acpi_battery
        Parameters:
            timeout: Number of seconds between updates.
            ac_icon: Icon path for when connected to AC power.
            battery_icon: Icon path for when on battery power.
            ac_color: Color of icon for when on AC power.
            bat_color: Color of icon for when on battery power.
            high_color: Color for when battery has a good charge.
            low_color: Color for when batteyr has a low charge.
            ac_name: The sysfs directory name for the AC adaptor.
            battery_name: The sysfs directory name for the Battery.
    '''
    def do_battery():
        battery_dir = '/sys/class/power_supply/%s/' % config['battery_name']
        ac_dir = '/sys/class/power_supply/%s/' % config['ac_name']

        mAh_left = float(open(path.join(battery_dir, 'charge_now')).read().strip())
        mAh_max  = float(open(path.join(battery_dir, 'charge_full_design')).read().strip())

        ac_state = int(open(path.join(ac_dir, 'online')).read().strip())

        if ac_state:
            stat_text = "^fg(%s)^i(%s)^fg() " % (config['ac_color'], config['ac_icon']) 
        else:
            stat_text = "^fg(%s)^i(%s)^fg() " % (config['bat_color'], config['battery_icon'])

        percent = (mAh_left/mAh_max)*100.0

        if percent < 50.0:
            number_color = config['low_color']
        else:
            number_color = config['high_color']

        return "%s^fg(%s)%2.2f^fg()%%" % (stat_text, number_color, percent)
    return (config['name'], timeout_update(int(config['timeout'])), do_battery)

def plugin_clock(config):
    '''
        Shows the date/time.

        Name: clock
        Parameters:
            timeout: Number of seconds between updates.
            format: The format (as for the command "date" but with % signs
                    doubled due to python's config file parser.
            color: The color for the text.
    '''
    from datetime import datetime
    def do_clock():
        return ''.join(["^fg(%s)" % config['color'], datetime.now().strftime(config['format']), "^fg()"])
    return (config['name'], timeout_update(int(config['timeout'])), do_clock)

def plugin_spaces(config):
    '''
        Due to a limitation of the config file parser, inserting whitespace as
        a static rule doesn't work.  This plugin allows you to specify a number
        of spaces to emit as a static element.

        Name: spaces
        Parameters:
            spaces: number of space characters to emit.
    '''
    def do_spaces():
        return " "*int(config['spaces'])
    return (config['name'], UPDATE_ONCE(), do_spaces)

def plugin_mpd(config):
    '''
        show state of configured MPD

        Name: mpd
        Parameters:
            mpd_host: hostname or ip address of MPD
            mpd_port: port of MPD
            play_icon: icon path for playing state
            play_color: color for playing state
            pause_icon: 
            pause_color:
            stop_icon:
            stop_color:
            vol_icon: volume indicator icon
            vol_color:
            song_color: color to display song info
            playlist_color: color to display playlist info
    '''
    try:
        import mpd
        client = mpd.MPDClient()
        client.connect(config['mpd_host'], config['mpd_port'])
        def mpd_state():
            status = client.status()
            song = client.currentsong()
            data = {'vol_color':config['vol_color'],'vol_icon':config['vol_icon'],
                    'playlist_color': config['playlist_color'], 'song_color': config['song_color']}
            data['state_color'] = config["%s_color"%status['state']]
            data['state_icon'] = config["%s_icon"%status['state']]
            if song:
                data['song'] = "%(artist)s - %(title)s" % song
            else:
                data['song'] = ''
            if 'pos' in song:
                data['playlist'] = '[%s/%s]' % (int(song['pos'])+1, status['playlistlength'])
            else:
                data['playlist'] = '[-/%s]' % status['playlistlength']
            data['volume'] = status['volume']
            return "^fg(%(song_color)s)%(song)s ^fg(%(playlist_color)s)%(playlist)s ^fg(%(state_color)s)^i(%(state_icon)s) ^fg(%(vol_color)s)^i(%(vol_icon)s) %(volume)s" % data
        return config['name'], timeout_update(3), mpd_state

    except ImportError:
        def f():
            return "^fg(red)Install python-mpd"
        return config['name'], UPDATE_ONCE(), f


if __name__=='__main__':
    sys.exit(main())
