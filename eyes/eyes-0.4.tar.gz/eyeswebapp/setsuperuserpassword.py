#!/usr/bin/env python
# encoding: utf-8
"""
setsuperuserpassword.py

Created by Joseph Heck on 2009-10-22.

Sets the django admin password to "admin"
"""
# pragma: no cover
from django.core.management import setup_environ
import settings
setup_environ(settings)

def main():
    from django.contrib.auth.models import User
    all_users = User.objects.all()
    first_user = all_users[0]
    first_user.set_password('admin');
    first_user.save()
    print "Password for first super user account reset to 'admin'."
    
if __name__ == '__main__':
	main()

