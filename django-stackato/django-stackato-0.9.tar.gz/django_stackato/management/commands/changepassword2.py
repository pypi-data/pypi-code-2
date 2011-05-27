# Track:
#  https://code.djangoproject.com/browser/django/trunk/django/contrib/auth/management/commands/changepassword.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Non-interactive version of "changepassword" that accepts the password in command-line'
    requires_model_validation = False
    

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('need exactly two arguments for username and password')

        username, password = args

        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("user '%s' does not exist" % username)

        u.set_password(password)
        u.save()

        return "Password changed successfully for user '%s'" % u.username
        
