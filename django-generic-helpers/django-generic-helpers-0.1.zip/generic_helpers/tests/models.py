from django.db import models
from django.core.management import call_command
from generic_helpers.models import GenericRelationModel

FOO_NUMBER = 3
BAR_NUMBER = 3

class Foo(models.Model):
    title = models.CharField('Title', max_length=255)

    class Meta:
        app_label = 'generic_helpers'

class Bar(GenericRelationModel):
    title = models.CharField('Title', max_length=255)

    class Meta:
        app_label = 'generic_helpers'

def load_test_data():
    for i in xrange(1, FOO_NUMBER + 1):
        foo = Foo.objects.create(title='Foo #%s' % i)

        for j in xrange(1, BAR_NUMBER + 1):
            bar = Bar.objects.create(title='Bar #%s' % i, content_object=foo)
        
call_command('syncdb', interactive=False, verbosity=0)
