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
from interface import Interface
import smtplib


class BlockInterface(Interface):
    
    form_html = '''
    <p>Entering an email address in the box below will ensure that no further emails will be sent to it from this remailer.</p>
    <div>
      <form action="PYANO_URI" method="post" >
        <p>
          <input name="email" value="" />
          <input type="submit" value="Block" />
        </p>
      </form>
    </div>
'''


    def validate(self):
        email = str(self.fs['email'])
        val_email(email)
        return email

    def main(self,req):
        if len(self.fs) == 0: # before submission
            if conf.remailer_addr:
                content = self.form_html.replace('PYANO_URI',str(req.uri))
            else:
                content = '<p>remailer_addr not configured</p>'
            html = self.set_html_content(conf.block_html, content)
            req.write(html)
        else: # process submission
            msg = self.process()
            req.write(self.html_success(msg,print_back=False))

    def html(self):
        return conf.block_html
                
    def process(self):
        email = self.validate() # check user input
        self.send_block_email(email) # try sending blocking email
        msg = 'Successfully sent request to block all emails to '+email+'.'
        msg += ' You will receive a confirmation email shortly.'
        return msg

    def send_block_email(self,email):
        server = smtplib.SMTP(conf.remailer_mx)
        msg = ('From: %s\r\nTo: %s\r\n\r\n'
               % (email, conf.remailer_addr))
        msg += ('DESTINATION-BLOCK %s\r\n' % email )
        server.sendmail(email, conf.remailer_addr, msg)
        server.quit()


def handler(req):
    return BlockInterface()(req)

