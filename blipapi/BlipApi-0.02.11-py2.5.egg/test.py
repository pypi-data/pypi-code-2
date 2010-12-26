#!/usr/bin/env python2.4 -tt
# -*- coding: utf-8 -*-

import blipapi
from pprint import pprint
import time
import sys

b = blipapi.BlipApi (dont_connect=False)
# b = blipapi.BlipApi ('myszapi', 'jsDhzc1', dont_connect=False)
# b = blipapi.BlipApi ('mysz', 'Tttj,oGC.', dont_connect=False)
b.authorize ('myszapi', 'jsDhzc1')
b.parser = eval
# b.rpm = 2
# b.debug = 10

imgs = (
    '/Users/mysz/test_img/avatar.jpg',
    '/Users/mysz/test_img/test_jpg/01.jpg',
)

# pprint (b.avatar_read (user='myszapi'))
# pprint (b.avatar_delete ())
# pprint (b.avatar_update (imgs[0]))

# pprint (b.background_update (imgs[1]))
# pprint (b.background_read (user='myszapi'))
# pprint (b.background_delete ())
#
# pprint (b.bliposphere_read (limit=2, include=['user']))
# pprint (b.bliposphere_read (since_id=49069134, include=['user']))

# pprint (b.dashboard_read ())
# pprint (b.dashboard_read (user='mysz', limit=3))
# pprint (b.dashboard_read (user='mysz', limit=3, include=['user']))

# pprint (b.dirmsg_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi'))
# pprint (b.dirmsg_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi', imgs[1]))
# pprint (b.dirmsg_read (id=49006191))
# pprint (b.dirmsg_read (user='mysz', limit=3, include=['user'], ))
# pprint (b.dirmsg_delete (id=49006191))

# pprint (b.movie_read (8337417)) # nie dziala - blip

# pprint (b.notice_read ())
# pprint (b.notice_read (limit=2))
# pprint (b.notice_read (limit=2, include=['user']))

# pprint (b.picture_read (id=49010414))
# pprint (b.picture_read (id=49010414, include=['update']))

# pprint (b.privmsg_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi'))
# pprint (b.privmsg_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi', imgs[1]))
# pprint (b.privmsg_read ())
# pprint (b.privmsg_read (id=49015681, include=['pictures']))
# pprint (b.privmsg_delete (id=49015681))

# pprint (b.recording_read ()) # nieprzetestowane

# pprint (b.shortlink_create (link='http://urzenia.net/asdf/qwe'))
# pprint (b.shortlink_read (limit=2))
# pprint (b.shortlink_read (code = '69eua'))

# pprint (b.status_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ())))
# pprint (b.status_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), imgs[1]))
# pprint (b.status_read (id=49065213))
# pprint (b.status_read (user='mysz', limit=2))
# pprint (b.status_read (user='myszapi', limit=2, include=['pictures', 'user']))
# pprint (b.status_delete (49065213))

# pprint (b.subscription_read ())
# pprint (b.subscription_read (user='myszapi', direction='to', include=['tracked_user', 'tracking_user']))
# pprint (b.subscription_delete ('mysz'))
# pprint (b.subscription_update ('mysz', www=1, im=0))

# pprint (b.tag_read ('myszfoto', limit=3))
# pprint (b.tag_read ('myszfoto', limit=2, include=['user', 'user[avatar]']))

# pprint (b.update_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ())))
# pprint (b.update_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi'))
# pprint (b.update_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi', imgs[1]))
# pprint (b.update_create (u'test ążśźęćńłó ĄŻŚŹĘĆŃŁÓ test ' + str (time.time ()), 'myszapi', imgs[1], private=True))
# pprint (b.update_read (id=49067520))
# pprint (b.update_read (user='myszapi', limit=2))
# pprint (b.update_read (user='myszapi', limit=2, include=['pictures', 'user']))
# pprint (b.update_delete (id=49067708))

# pprint (b.user_read ('mysz', include=['avatar']))
# pprint (b.user_read (include=['avatar', 'current_status']))

# pprint (b ('user_read', 'mysz', include=['avatar']))

# pprint (b.avatar_read ('myszapi'))
# pprint (b.background_read ('myszapi'))

# # import socket
# # socket.setdefaulttimeout (2)
# while True:
#     print time.time () % 60
#     try:
#         i = b.status_read (user='mysz', limit=1)
#         print i['body'][0]['body']
#     except Exception, e:
#         print 'ERROR:', type (e), dir (e), e.args, e
# #     pprint (i)
#     time.sleep (0.5)

