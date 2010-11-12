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
import random

from stats import stats, bad_mail2news
from config import conf, NONE, RANDOM, POST


class InputError(Exception):
    pass

def val_email_local(local):
    ac = "[a-zA-Z0-9_!#\$%&'*+\-=?\^`{|}~]"
    m = re.compile( '^('+ac+'+\.)*'+ac+'+$')
    if not m.match(local):
        raise InputError()


def val_dot_seq(server):
    ac = '[a-zA-Z0-9+\-_]'
    m = re.compile( '^('+ac+'+\.)+'+ac+'+$')
    if not m.match(server):
        raise InputError()


def val_email(addr):
    m = re.compile( '^("?[\w ]*"? *<)?([^>]+)>?$' )
    ok =  m.match(addr)
    try:
        if not ok:
            raise InputError()
        email = ok.group(2)
        parts = email.split('@')
        if len(parts) != 2:
            raise InputError()
        val_email_local(parts[0])
        val_dot_seq(parts[1])
    except InputError:
        if addr:
            raise InputError(addr+' is not a valid email address.')
        raise InputError('Please enter an email address.')


def val_newsgroups(newsgroups):
    groups = newsgroups.split(',')
    for group in groups:
        val_dot_seq(group)


def val_references(refs):
    m = re.compile( '^<(.*)>$' )
    try:
        for ref in refs.split(' '):
            ok = m.match(ref)
            if not ok:
                raise InputError()
            val_email( ok.group(1) )
    except:
        raise InputError(ref+' is not a valid reference.')


def val_mail2news(mail2news):
    for addr in mail2news.split(','):
        try:
            val_email(addr)
        except InputError:
            raise InputError(mail2news+' is not a valid mail2news gateway')


def val_hashcash(hc):
    m = re.compile('[a-zA-Z0-9_:+\-=; ]+')
    if not m.match(hc):
        raise InputError(hc+' is not a valid hashcash.')

def val_n_copies(n_copies):
    if n_copies <= 0 or n_copies > conf.max_copies:
        raise InputError('Invalid number of copies.')

# Explanation for the chain parsing:
#
# By default, mixmaster will allow the user to specify any chain he or
# she desires. For example, it will accept messages with duplicate
# remailers (bad for privacy), or a middleman remailer as the final
# remailer (which will silently fail). However, when sending
# multi-packet messages, it *requires* a random remailer in the chain.
#
# On the other hand, mixmaster does a very thorough job of picking
# intelligent sets of random remailers.
#
# Here we make the following design choices:
#  - Do not allow the user to use a known bad chain
#  - Do not allow the user to use a middleman remailer as last hop
#  - Do not allow the user to use a remailer that does not support the 
#    post directive as last hop when posting to a newsgroup without a 
#    mail2news gateway.
#  - Translate a choice of RANDOM to '*' (the mixmaster random chain)
#  - Check for duplicate remailers.
#
def parse_chain(fs,m2n=None):
    chain = []
    for i in range(0, conf.chain_max_length):
        chain_str = 'chain'+str(i)
        if not chain_str in fs:
            break
        remailer = str(fs[chain_str])
        if remailer == NONE: # empty remailer, we stop the chain
            break
        elif remailer == RANDOM:
            chain.append('*')
        elif remailer in chain: # duplicate remailer!
            raise InputError('Cannot use the same remailer twice in the same chain.')
        elif remailer in stats:
            chain.append( remailer )
        else: # invalid remailer entry
            raise InputError(remailer+' is not a valid remailer.')

    if chain:
        # Do some checks on last remailer
        last = chain[len(chain)-1]
        if stats[last].middleman: # make sure that final remailer is not a middleman
            raise InputError('Cannot select a "middleman" remailer as your final remailer.')
        if m2n: # this is a news article
            if m2n == POST and not stats[last].post: # make sure that final remailer can post to newsgroups
                raise InputError(last+'does not have the "post" option configured.')
            elif m2n in bad_mail2news: # make sure that we are not using an incompatible exit node and mail2news gateway
                if last in bad_mail2news[m2n]:
                    raise InputError(last+' is not compatible with the mail2news gateway '+m2n+'.')
        # check for bad chains
        for i in range(0,len(chain)-1):
            cur = chain[i]
            next = chain[i+1]
            if next in stats[cur].broken:
                raise InputError('Cannot use known broken chain: ('+cur+' '+next+').')
    return chain
