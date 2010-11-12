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

import datetime
from config import conf


datetime_fmt = '%H%M%S%m%d%Y'

class SecurityError(Exception):
    pass

def get_history():
    history = {}
    try:
        with open(conf.hist_file,'r') as f:
            for line in f:
                times = line.strip('\n').split(':')
                ip = times.pop(0)
                history[ip] = [ datetime.datetime.strptime(t,datetime_fmt) for t in times ]
    except IOError: # hist file probably does not exist
        pass
    return history


def prune_history(hist):
    now = datetime.datetime.today()
    cutoff = now - datetime.timedelta(0,0,0,0,conf.hist_window)
    to_del = []
    for ip, times in hist.iteritems():
        new_times = []
        for t in times:
            if t >= cutoff:
                new_times.append(t)
        if new_times: 
            hist[ip] = new_times
        else: # no more recorded uses in the time window: remove all history for that ip
            to_del.append(ip)
    for ip in to_del:
        del hist[ip]
    return hist


def write_history(hist):
    try:
        with open(conf.hist_file,'w') as f:
            for ip, times in hist.iteritems():
                f.write(ip)
                for t in times:
                    f.write( ':' + t.strftime(datetime_fmt) )
                f.write("\n")
    except IOError: # histfile is probably not writable
        pass


def check_hist(ip):
    hist = prune_history( get_history() )
    if ip in hist:
        hist[ip].append( datetime.datetime.today() )
        write_history(hist)
        if len(hist[ip]) > 2*conf.hist_max_uses:
            ban(ip)
            raise SecurityError('Your ip has been banned from using this service. If you feel this is not warranted, please contact this service\'s operator')
        if len(hist[ip]) > conf.hist_max_uses:
            raise SecurityError('In order to prevent abuse of this service, you can only send a limited number of emails at a given time. Please try again later. If you persist in trying to use this interface too frequently, you will eventually get banned from this service.')
    else:
        hist[ip] = [ datetime.datetime.today() ]
        write_history(hist)


def check_banned(ip):
    banned = get_banned()
    if ip in banned:
        raise SecurityError('Your ip has been banned from using this service. If you feel this is not warranted, please contact this service\'s operator')


def ban(ip):
    banned = get_banned()
    banned.append(ip)
    write_banned(banned)


def get_banned():
    banned = []
    try:
        with open(conf.banned_file,'r') as f:
            banned = f.read().split('\n')
    except IOError: # file probably does not exist
        pass
    return banned

def write_banned(banned):
    with open(conf.banned_file,'w') as f:
        f.write('\n'.join(banned))


def check_ip(ip):
    check_banned(ip)
    check_hist(ip)
