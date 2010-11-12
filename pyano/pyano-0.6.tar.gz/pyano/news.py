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
from config import conf, POST
from interface import MixInterface
from stats import bad_mail2news, format_bad_mail2news, mail2news_pref_sort
from mix import send_news


class NewsInterface(MixInterface):

    form_html = '''
    <form action="PYANO_URI" method="post" >
    <table id="mixtable">
      <tr id="newsgroup">
        <td><strong>*Newsgroup(s):</strong></td>
        <td><input class="line" name="newsgroups" value="" /></td>
      </tr>
      <tr id="from">
        <td><strong>From:</strong></td>
        <td><input class="line" name="from" value="" /></td>
      </tr>
      <tr id="subject">
        <td><strong>*Subject:</strong></td>
        <td><input class="line" name="subject" value="" /></td>
      </tr>
      <tr>
        <td><strong>References:</strong></td>
        <td><input class="line" name="references" value="" /></td>
      </tr>
      <tr id="mail2news">
        <td><strong>Mail2News:</strong></td>PYANO_MAIL2NEWS
      </tr>
      <tr id="hashcash">
        <td><strong>Hashcash:</strong></td>
        <td><input class="line" name="hashcash" value="" /></td>
      </tr>
      <tr id="noarchive">
        <td><strong>X-No-Archive:</strong></td>
        <td><input type="checkbox" name="archive" checked="checked" />
        (checked means Google will not archive this post)
        </td>
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
        groups = str(self.fs['newsgroups']).replace(' ','') # filter out whitespaces
        val_newsgroups(groups)
        orig = str(self.fs['from'])
        if orig:
            val_email(orig)
        refs = str(self.fs['references'])
        if refs:
            val_references(refs)
        mail2news_custom = self.fs['mail2news_custom']
        if mail2news_custom:
            val_mail2news(mail2news_custom)
            mail2news = mail2news_custom
        else:
            mail2news = str(self.fs['mail2news'])
            if mail2news != POST:
                val_mail2news(mail2news)
        hashcash = str(self.fs['hashcash']).strip()
        if hashcash:
            val_hashcash(hashcash)
        try:
            checked = str(self.fs['archive'])
            no_archive = True
        except KeyError:
            no_archive = False
        subj = str(self.fs['subject'])
        if not subj:
            raise InputError('Subject required.')
        chain = parse_chain(self.fs,m2n=mail2news)
        n_copies = int(self.fs['copies'])
        val_n_copies(n_copies)
        msg = str(self.fs['message'])
        if not msg:
            raise InputError('Refusing to send empty message.')
        return groups, orig, subj, refs, mail2news, hashcash, no_archive, chain, n_copies, msg


    def html(self):
        return conf.news_html

    def form(self):
        mail2news =  '\n'
        mail2news += '        <td>\n'
        mail2news += '          <select name="mail2news" >\n'
        if bad_mail2news:
            gateways = mail2news_pref_sort()
            for gateway in gateways:
                mail2news += '            <option value="'+gateway+'">'+format_bad_mail2news(gateway).replace(' ',"&nbsp;")+'</option>\n'
        else:
            for gateway in conf.mail2news:
                mail2news += '            <option value="'+gateway+'">'+gateway+'</option>\n'
        mail2news += '          </select><br/>\n'
        mail2news += '          Or custom: <input name="mail2news_custom" value="" />\n'
        mail2news += '        </td>\n'
        out = NewsInterface.form_html.replace('PYANO_MAIL2NEWS',mail2news)
        return conf.news_form_html.replace('<!--FORM-->',out)

    
    def process(self):
        newsgroups, orig, subj, refs, mail2news, hashcash, no_archive, chain, n_copies, msg = self.validate()
        send_news(newsgroups, orig, subj, refs, mail2news, hashcash, no_archive, chain, n_copies, msg)
        msg = 'Successfully sent message to '+newsgroups+' using '
        if chain:
            msg += 'remailer chain '+','.join(chain)
        else:
            msg += 'a random remailer chain'
        if mail2news != POST:
            msg += ' with mail2news gateway '+mail2news+'.'
        else:
            msg += '.'
        return msg

    
def handler(req):
    return NewsInterface()(req)
