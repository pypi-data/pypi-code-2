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


import subprocess
from config import conf, POST

class MixError(Exception):
    pass

def send_mail(to,orig,subj,chain,n_copies,msg):
    args = [conf.mixmaster,'--mail','--to='+to,'--subject='+subj,'--copies='+str(n_copies)]
    
    if orig:
        args.append('--header=From: '+orig)
    if chain:
        args.append('--chain='+','.join(chain))
    send_mix(args,msg)


def send_news(newsgroups, orig, subj, refs, mail2news, hashcash, no_archive, chain, n_copies, msg):
    args = [conf.mixmaster,'--subject='+subj,'--copies='+str(n_copies)]
    if orig:
        args.append('--header=From: '+orig)
    if no_archive:
        args.append('--header=X-No-Archive: yes')
    if mail2news != POST: # user supplied mail2news gateways
        args.extend(['--mail','--to='+mail2news])
        args.append('--header=Newsgroups: '+newsgroups)
    else: # no supplied mail2news gateways, use mixmaster's internal mail2news parameters
        args.extend(['--post','--post-to='+newsgroups])
    if refs:
        args.append('--header=References: '+refs)
    if hashcash:
        args.append('--header=X-HashCash: '+hashcash)
    if chain:
        args.append('--chain='+','.join(chain))
    send_mix(args,msg)
    

def send_mix(args,msg):
    try:
        mix = subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = mix.communicate(msg)
        if err.find('Error') >= 0:
            raise MixError('Mixmaster process returned the following error: '+str(err)+'. Sending failed.')
    except OSError: # usally means that mixmaster could not be executed
        raise MixError('Could not find mixmaster binary.')
