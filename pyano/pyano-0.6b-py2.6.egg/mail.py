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

from validate import *
from config import conf
from interface import MixInterface
from mix import send_mail


class MailInterface(MixInterface):
    
    form_html = '''
    <form action="PYANO_URI" method="post" >
    <table id="mixtable">
      <tr id="to">
        <td><strong>*To:</strong></td>
        <td><input class="line" name="to" value="" /></td>
      </tr>
      <tr id="from">
        <td><strong>From:</strong></td>
        <td><input class="line" name="from" value="" /></td>
      </tr>
      <tr id="subject">
        <td><strong>Subject:</strong></td>
        <td><input class="line" name="subject" value="" /></td>
      </tr>PYANO_CHAIN
      <tr id="copies">
         <td><strong>Copies:</strong></td>
         <td>
           PYANO_COPIES
         </td>
      </tr>
      <tr id="message">
        <td><strong>*Message:</strong></td>
        <td><textarea name="message" rows="30" cols="70" ></textarea></td>
      </tr>
      <tr id="buttons">
        <td></td>
        <td><input type="submit" value="Send" /><input type="reset" value="Reset" /></td>
      </tr>
    </table>
    </form>
'''

    def validate(self):
        to = str(self.fs['to'])
        val_email(to)
        orig = str(self.fs['from'])
        if orig:
            val_email(orig)
        subj = str(self.fs['subject'])
        chain = parse_chain(self.fs)
        n_copies = int(self.fs['copies'])
        val_n_copies(n_copies)
        msg = str(self.fs['message'])
        if not msg:
            raise InputError('Refusing to send empty message.')
        return to, orig, subj, chain, n_copies, msg


    def html(self):
        return conf.mail_html

    def form(self):
        return conf.mail_form_html.replace('<!--FORM-->',MailInterface.form_html)
                
    def process(self):
        to, orig, subj, chain, n_copies, msg = self.validate() # check user input
        send_mail(to,orig,subj,chain,n_copies,msg) # try sending to mixmaster
        msg = 'Successfully sent message to '+to+' using '
        if chain:
            msg += 'remailer chain '+','.join(chain)+'.'
        else:
            msg += 'a random remailer chain.'
        return msg

    

def handler(req):
    return MailInterface()(req)

