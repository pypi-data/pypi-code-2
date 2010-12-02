import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import mongoengine
from django.conf import settings
from grate.mongo import User, Group


mongoengine.connect(settings.MONGO_DBNAME)

names = ['alice', 'bob', 'charlie', 'dave', 'eve', 'fran', 'gordon', 'henry',
    'isaac', 'justin', 'kim', 'lisa', 'mallory', 'nick', 'oscar', 'pat',
    'lee']

for name in names:
    try:
        User(username=name).save()
    except:
        pass

lee = User.objects(username='lee').first()

g_test = Group(name='test', owner=lee)
g_test.save()

for name in names[:10]:
    user = User.objects(username=name).first()
    g_test.add_access(user, 'member')
