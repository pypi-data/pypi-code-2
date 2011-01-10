
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

import django_couch
from couchdbcurl.client import ResourceConflict

class Command(BaseCommand):

    help = u'Creates admin user'
    
    def execute(self, db_key, username, *args, **kwargs):
        
        db = django_couch.db(db_key)
        u = User()
        password = User.objects.make_random_password()
        u.set_password(password)
        password_hash = u.password

        try:
            db['user_%s' % username] = {"admin": True, "is_staff": True, "last_login": None, "password": password_hash, "type": "user", "username": username}
            print "User %s created. Password is: %s" % (username, password)
        except ResourceConflict:
            print "Create user failed: conflict"
        
        
