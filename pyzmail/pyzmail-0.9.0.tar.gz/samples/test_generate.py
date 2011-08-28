#!/bin/env python

import pyzmail
from pyzmail.generate import *

#
# some testing code and samples
#
smtp_host='max'
smtp_port=25

if False:
    smtp_host='smtp.gmail.com'
    smtp_port=587
    smtp_login='your.addresse@gmail.com'
    smtp_passwd='your.password'

sender=(u'Ala\xefn Spineux', 'alain.spineux@gmail.com')
sender=(u'Alain Spineux', u'alain.spineux@gmail.com')

root_addr='root@max.asxnet.loc'
recipients=[ ('Alain Spineux', root_addr),
             (u'Alain Spineux', root_addr),
             ('Dr. Alain Sp<i>neux', root_addr),
             (u'Dr. Alain Sp<i>neux', root_addr),
             (u'Dr. Ala\xefn Spineux', root_addr),
             (u'Dr. Ala\xefn Spineux', root_addr),
             ('us_ascii_name_with_a_space_some_where_in_the_middle to_allow_python_Header._split()_to_split_according_RFC2822', root_addr),
             (u'This-is-a-very-long-unicode-name-with-one-non-ascii-char-\xf4-to-force-Header()-to-use-RFC2047-encoding-and-split-in-multi-line', root_addr),
             ('this_line_is_too_long_and_dont_have_any_white_space_to_allow_Header._split()_to_split_according_RFC2822', root_addr),
             ('Alain Spineux', root_addr),             
              ]

smile_png=base64.b64decode(
"""iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOBAMAAADtZjDiAAAAMFBMVEUQEAhaUjlaWlp7e3uMezGU
hDGcnJy1lCnGvVretTnn5+/3pSn33mP355T39+//75SdwkyMAAAACXBIWXMAAA7EAAAOxAGVKw4b
AAAAB3RJTUUH2wcJDxEjgefAiQAAAAd0RVh0QXV0aG9yAKmuzEgAAAAMdEVYdERlc2NyaXB0aW9u
ABMJISMAAAAKdEVYdENvcHlyaWdodACsD8w6AAAADnRFWHRDcmVhdGlvbiB0aW1lADX3DwkAAAAJ
dEVYdFNvZnR3YXJlAF1w/zoAAAALdEVYdERpc2NsYWltZXIAt8C0jwAAAAh0RVh0V2FybmluZwDA
G+aHAAAAB3RFWHRTb3VyY2UA9f+D6wAAAAh0RVh0Q29tbWVudAD2zJa/AAAABnRFWHRUaXRsZQCo
7tInAAAAaElEQVR4nGNYsXv3zt27TzHcPup6XDBmDsOeBvYzLTynGfacuHfm/x8gfS7tbtobEM3w
n2E9kP5n9N/oPZA+//7PP5D8GSCYA6RPzjlzEkSfmTlz+xkgffbkzDlAuvsMWAHDmt0g0AUAmyNE
wLAIvcgAAAAASUVORK5CYII=
""")
angry_gif=base64.b64decode(
"""R0lGODlhDgAOALMAAAwMCYAAAACAAKaCIwAAgIAAgACAgPbTfoR/YP8AAAD/AAAA//rMUf8A/wD/
//Tw5CH5BAAAAAAALAAAAAAOAA4AgwwMCYAAAACAAKaCIwAAgIAAgACAgPbTfoR/YP8AAAD/AAAA
//rMUf8A/wD///Tw5AQ28B1Gqz3S6jop2sxnAYNGaghAHirQUZh6sEDGPQgy5/b9UI+eZkAkghhG
ZPLIbMKcDMwLhIkAADs=
""")
pingu_png=base64.b64decode(
"""iVBORw0KGgoAAAANSUhEUgAAABoAAAATBAMAAAB8awA1AAAAMFBMVEUQGCE5OUJKa3tSUlJSrdZj
xu9rWjl7e4SljDGlnHutnFK9vbXGxsbWrTHW1tbv7+88a/HUAAAACXBIWXMAAA7EAAAOxAGVKw4b
AAAAB3RJTUUH2wgJDw8mp5ycCAAAAAd0RVh0QXV0aG9yAKmuzEgAAAAMdEVYdERlc2NyaXB0aW9u
ABMJISMAAAAKdEVYdENvcHlyaWdodACsD8w6AAAADnRFWHRDcmVhdGlvbiB0aW1lADX3DwkAAAAJ
dEVYdFNvZnR3YXJlAF1w/zoAAAALdEVYdERpc2NsYWltZXIAt8C0jwAAAAh0RVh0V2FybmluZwDA
G+aHAAAAB3RFWHRTb3VyY2UA9f+D6wAAAAh0RVh0Q29tbWVudAD2zJa/AAAABnRFWHRUaXRsZQCo
7tInAAAA0klEQVR4nE2OsYrCUBBFJ42woOhuq43f4IfYmD5fsO2yWNhbCFZ21ovgFyQYG1FISCxt
Xi8k3KnFx8xOTON0Z86d4ZKKiNowM5QEUD6FU9uCSWwpYThrSQuj2fjLso2DqB9OBqqvJFiVllHa
usJedty1NFe2brRbs7ny5aIP8dSXukmyUABQ0CR9AU9d1IOO1EZgjg7n+XEBpOQP0E/rUz2Rlw09
Amte7bdVSs/s7py5i1vFRsnFuW+gdysSu4vzv9vm57faJuY0ywFhAFmupO/zDzDcxlhVE/gbAAAA
AElFTkSuQmCC
""")

text_utf8="""This is the the text part.
With a related picture: cid:smile.png
and related document: cid:related.txt

Bonne journ\xc3\xa9ee.
"""
utext=u"""
This is the the text part.
With a related picture: cid:smile.png
and related document: cid:related.txt
Bonne journ\xe9e.
"""
data_text=u'Text en Fran\xe7ais'
related_text=u'Document relatif en Fran\xe7ais'

html="""<html><body>
This is the html part with a related picture: <img src="cid:smile.png" />
and related document: <a href="cid:related.txt">here</a><br>
Bonne journ&eacute;e.
</body></html>
"""
embeddeds=[ (smile_png, 'image', 'png', 'smile.png', None),  
           (related_text.encode('iso-8859-1'), 'text', 'plain', 'related.txt', 'iso-8859-1'),  
          ]

pingu_att=email.mime.image.MIMEImage(pingu_png, 'png')
pingu_att.add_header('Content-Disposition', 'attachment', filename=('iso-8859-1', 'fr', u'ping\xfc.png'.encode('iso-8859-1')))

pingu_att2=email.mime.image.MIMEImage(pingu_png, 'png')
pingu_att2.add_header('Content-Disposition', 'attachment', filename='pingu.png')

attachments=[ (angry_gif, 'image', 'gif', ('iso-8859-1', 'fr', u'\xe4ngry.gif'.encode('iso-8859-1')), None),
              (angry_gif, 'image', 'gif', 'angry.gif', None),
             
              (data_text.encode('iso-8859-1'), 'text', 'plain', 'document.txt', 'iso-8859-1'),  
              pingu_att,
              pingu_att2]

mail=build_mail((utext.encode('iso-8859-1'), 'iso-8859-1'), (html, 'us-ascii'), attachments, embeddeds)
#    mail=build_mail((utext.encode('iso-8859-1'), 'iso-8859-1'))
payload, mail_from, rcpt_to, msg_id=complete_mail(mail, sender, recipients, u'My Subject', default_charset='iso-8859-1', cc=[('Gama', root_addr), ], bcc=[('Colombus', root_addr), ], message_id_string='pyzmail')
print payload
ret=send_mail(payload, mail_from, rcpt_to, smtp_host, smtp_port=smtp_port)

if not ret:
    print 'Success'
else:
    if isinstance(ret, dict):
        print 'failed recipients:', ', '.join(ret.keys())
    else:
        print 'Error:', errmsg
