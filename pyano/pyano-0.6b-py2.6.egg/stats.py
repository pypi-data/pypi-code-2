###############################################################################
# This file is part of Pyano.                                                 #
#                                                                             #
# Pyano is a web interface for the mixmaster remailer, written for mod_python #
# Copyright (C) 2010  Sean Whitbeck <sean@neush.net>                          #
#                                                                             #
# Pyano is free software: you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Pyano is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

import re
from config import conf, POST

class RemailerStats:
    def __init__(self,name,latency,uptime):
        self.name = name
        self.latency = latency
        self.uptime = uptime
        self.broken = []
        self.allow_from = False # by default no remailers accept from headers
        self.middleman = False
        self.post = False

stats = {}
bad_mail2news = {}

def parse_stats():
    try:
        _read_mlist()
        try:
            _read_allow_from()
        except IOError: # Error reading from.html
            pass
    except IOError: # Could not read mlis2.txt
        stats.clear()
    try:
        _read_bad_mail2news()
    except IOError: # Error reading results.txt
        bad_mail2news.clear()

        


def _read_mlist():
    completely_broken = set([])
    with open(conf.mlist2,'r') as f:
        n = 0
        in_stats_block = False
        in_broken_block = False
        for line in f:
            n += 1
            if n == 4:
                in_stats_block = True
            elif in_stats_block:
                elems = line.split()
                if len(elems) == 0: # blank line, we are out of the stats block
                    in_stats_block = False
                else:
                    name = elems[0]
                    latency = elems[2]
                    uptime = float(elems[4].strip('%'))                    
                    stats[name] = RemailerStats(name,latency,uptime)
            elif "Broken type-II remailer chains" in line:
                in_broken_block = True
            elif in_broken_block:
                elems = line.strip().strip('()').split()
                if len(elems) == 0: # blank line, we are out of the broken chains block
                    in_broken_block = False
                else:
                    rem_from = elems[0]
                    rem_to = elems[1]
                    if rem_from == '*': # This remailer doesn't accept messages
                        completely_broken.add(rem_to)
                    elif rem_to == '*': # This remailer doesn't send messages to anyone
                        completely_broken.add(rem_from)
                    else:
                        stats[rem_from].broken.append(rem_to)
            elif '=' in line: # we are now looking for the remailer capabilities block 
                name = line[11:].split('"',1)[0]
                rem_stats = stats[name]
                rem_stats.middleman = ("middle" in line)
                rem_stats.post = ("post" in line)
    # cleanup up completely useless remailers
    for remailer in completely_broken:
        del stats[remailer]


def _read_allow_from():
    with open(conf.allow_from,'r') as f: # find out those that do accept from headers
        in_from_block = False
        m = re.compile("<td>(\w+)</td>")
        for line in f:
            if line.find("User Supplied From") >= 0:
                in_from_block = True
            if in_from_block:
                ok = m.search(line)
                if ok:
                    name = ok.group(1)
                    if name in stats:
                        stats[name].allow_from = True


def format_stats(name):
    rem = stats[name]
    s = rem.name.ljust(12)+rem.latency.rjust(5)+(str(rem.uptime)+"%").rjust(7)
    if rem.middleman:
        s += " M"
    else:
        s += "  "
    if rem.allow_from:
        s += "F"
    else:
        s += " "
    if rem.post:
        s += "P"
    else:
        s += " "
    if rem.broken:
        s += " (breaks: "
        for remailer in rem.broken:
            s += remailer+","
        s = s.rstrip(',')
        s += ')'
    return s


def uptime_sort():
    remailers = stats.keys()
    remailers.sort(cmp=lambda x,y: cmp(stats[y].uptime,stats[x].uptime))
    return remailers


def _read_bad_mail2news():
    with open(conf.bad_mail2news,'r') as f:
        for line in f:
            elems = line.split('>')
            if len(elems) == 2:
                remailer = elems[0].strip()
                gateway = elems[1].strip()
                bad = False
                if 'BAD' in gateway:
                    gateway = gateway.split()[0]
                    bad = True
                if gateway == 'Post:':
                    gateway = POST
                if not gateway in bad_mail2news:
                    bad_mail2news[gateway] = set([])
                if bad:
                    bad_mail2news[gateway].add(remailer)

def format_bad_mail2news(gateway):
    out = gateway.ljust(25)
    bad = bad_mail2news[gateway]
    if bad:
        out += ' (BAD: '
        for remailer in bad:
            out += remailer+','
        out = out.rstrip(',')
        out += ')'
    return out

def mail2news_pref_sort():
    gateways = bad_mail2news.keys()
    gateways.sort(cmp=_mail2news_cmp)
    return gateways

def _mail2news_cmp(gate1, gate2):
    if gate1 in conf.mail2news:
        if gate2 in conf.mail2news:
            return cmp(conf.mail2news.index(gate1),
                       conf.mail2news.index(gate2))
        else:
            return -1
    elif gate2 in conf.mail2news:
        return 1
    else:
        return 0
