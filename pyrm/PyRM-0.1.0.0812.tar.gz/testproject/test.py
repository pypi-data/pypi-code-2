# coding: utf-8

import os
import datetime

if __name__ == "__main__":
    os.chdir(os.path.expanduser("~/servershare/PyRM/"))
    os.environ['DJANGO_SETTINGS_MODULE'] = "testproject.settings"
    virtualenv_file = os.path.expanduser("~/pyrm_env/bin/activate_this.py")
    execfile(virtualenv_file, dict(__file__=virtualenv_file))

from django.conf import settings

settings.configure(DEBUG=True,
    DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  ":memory:",
    }
},)

from django.db import models


#class TestModel(models.Model):




if __name__ == "__main__":

    d = models.DateField()
    d.run_validators(datetime.datetime.now())

    print d

#    t = TestModel(d=datetime.datetime.now())
#    t.save()
#    print t
