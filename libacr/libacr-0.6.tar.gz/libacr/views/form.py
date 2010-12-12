# -*- coding: utf-8 -*-
import ConfigParser
from tg import tmpl_context
import StringIO
from libacr.lib import url as acr_url
from libacr.lib import language
from genshi.template import MarkupTemplate

from libacr.model.core import DBSession
from libacr.model.content import Page
import tw.forms as twf

class FormRenderer(object):
    def __init__(self):
        self.name = 'form'
        self.exposed = True
        self.form_fields = [twf.TextField('email_address', label_text="Destination Email:",
                                                           validator=twf.validators.Email(not_empty=True, strip=True)),
                            twf.TextField('subject', label_text="Subject:",
                                                           validator=twf.validators.String(not_empty=True, strip=True)),
                            twf.TextArea('fields', label_text="Fields:", validator=twf.validators.String(not_empty=True),
                                                   rows=20, attrs={'style':'width:600px;height:400px;'})]
                                                                   
    def to_dict(self, data):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(data))

        d = {'email_address' : config.get('form', 'email_address'),
                   'subject' : config.get('form', 'subject')}

        fields = ''
        for field in config.items('form'):
            if field[0] not in d.keys():
                fields += '%s=%s\n' % (field[0], field[1])

        d['fields'] = fields
        return d
        
    def from_dict(self, dic):
        config = ConfigParser.ConfigParser()
        config.add_section('form')
        config.set('form', 'email_address', dic['email_address'])
        config.set('form', 'subject', dic['subject'])

        fields = ConfigParser.ConfigParser()
        fields.readfp(StringIO.StringIO('[fields]\n' + dic['fields']))
        for field in fields.items('fields'):
            config.set('form', field[0], field[1])

        s = StringIO.StringIO()
        config.write(s)
        return s.getvalue()

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(data))

        email_address = config.get('form', 'email_address')
        subject = config.get('form', 'subject')
        items = config.items('form')
        list_items = []
        form = '<div class="form">'
        form += '<form action=%s >' % (acr_url('/sendForm_to_email'))
        form += '<table>'

        for item in items:
         if item[0] != 'email_address' and item[0] != 'subject':
            form += '<tr class="%s_field">' % (item[0])
            form += '<td class="form_label">'
            item1 = item[1]
            obligatory = item[0].startswith('*')

            if item1[0] == '[':
               if obligatory:
                  copy = item[0].lstrip('*')
                  form += '%s' % (copy)
               else:
                  form += '%s </td>' % (item[0])
               form += '<td class="form_field"><select name="%s">' % (item[0])

               copy1 = item[1].lstrip('[')
               copy2 = copy1.rstrip(']')
               list_items = copy2.split(',')

               for value in list_items:
                   form += '<option value="%s">%s</option>' % (value, value)
               form += '</select></td>'
            elif item[1].lower() == 'textarea':
               if obligatory:
                  copy = item[0].lstrip('*')
                  form += '%s ' % (copy)
               else:
                  form += '%s </td>' % (item[0])
               form += '<td class="form_field"> <textarea name="%s">' % (item[0])
               form += '</textarea> </td>'
               form += '</tr>'
            else:
               if obligatory:
                  copy = item[0].lstrip('*')
                  form += '%s' % (copy)
               else:
                  form += '%s </td> ' % (item[0])
               form += '<td class="form_field"><input type="%s" name="%s"/> </td>' % (item[1], item[0])

        form += '</table>'

        form += '<div> <input type="hidden" name="email_address" value="%s" />' % (email_address)
        form += '<input type="hidden" name="subject" value="%s" />' % (subject)
        form += '<input type="submit" value="submit" /></div>'

        form += '</form>'
        form += '</div>'
        return form










