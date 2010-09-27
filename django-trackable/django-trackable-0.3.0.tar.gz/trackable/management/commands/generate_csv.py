from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db.models.loading import get_model
from django.db.models import Sum, Avg

from trackable.messaging import process_messages
from trackable.sites import site, NotRegistered

from optparse import make_option

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import datetime
import warnings
import codecs
import csv


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        # self.writer.writerow([s.encode("utf-8") for s in row])
        newrow = []
        for s in row:
            if type(s) == unicode:
                s = s.encode("utf-8")
            newrow.append( s )
        self.writer.writerow( newrow )

        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class Command(BaseCommand):
    help = 'Used to generate CSV summary data for Vendor tracking data.'
    args = 'app.model [app.trackable_model ...]'
    option_list = BaseCommand.option_list + (
        make_option('--aggregate-fields', action='store', dest='aggregate_fields',
                    help='Specify the field on which to aggregate data'),
        )

    def handle(self, model_spec, *trackable_model_specs, **options):
        print "Aggregating data for %s" % (model_spec)
        for option in options.get('aggregate_fields').split(','):
            print "  %s" % (option)

        try:
            app_label,model = model_spec.split('.')
            model_cls = get_model(app_label,model)
            if model_cls is None:
                raise CommandError("Unknown model: %s" % (model_spec))
        except ValueError:
            raise CommandError("Use full appname.ModelName specification for argument %s" % model_spec)

        trackable_models = []
        if trackable_model_specs:
            for model_spec in trackable_model_specs:
                app_label,model = model_spec.split('.')
                model_cls = get_model(app_label,model)
                if model_cls is None:
                    warnings.warn( "Could not resolve trackable model specification: %s" % model_spec )
                trackable_models.append( model_cls )
        try:
            if not trackable_models:
                trackable_models = site._registry[model_cls]
        except KeyError:
            raise CommandError("%s has no registered trackable objects.")

        for trackable_model in trackable_models:
            if trackable_model not in site._registry[model_cls]:
                raise CommandError( \
                    "%s is not a registered trackable object with %s" % \
                        (trackable_model,model_cls))

        fields = [Sum(field_name) for field_name in options.get('aggregate_fields').split(',')]
        fields.extend( [Avg(field_name) for field_name in options.get('aggregate_fields').split(',')] )
        instances = []

        for instance in model_cls.objects.values('id','name'):
            for trackable_model in trackable_models:
                trackable_model_objects = \
                    trackable_model.objects \
                    .filter( \
                        content_type=ContentType.objects.get_for_model(model_cls), \
                        object_id=instance['id'] \
                        )
                if not trackable_model_objects.count():
                    continue
                attrs = trackable_model_objects \
                    .aggregate( \
                        *[field for field in fields] \
                        )
                adjusted_attrs = {}
                for key,val in attrs.iteritems():
                    adjusted_attrs['%s__%s' % (trackable_model.__name__.lower(),key)] = val
                instance.update( adjusted_attrs )

            final_attrs = {}
            for key,val in instance.iteritems():
                if type(val) == unicode:
                    try:
                        val = str(val)
                    except:
                        continue
                final_attrs[key] = val
            instances.append( final_attrs )

        f = open('./output.csv','w')
        headers = ['id','name',]
        for trackable_model in trackable_models:
            for field in options.get('aggregate_fields').split(','):
                headers.append('%s__%s__%s' % (trackable_model.__name__.lower(),field,'sum'))
                headers.append('%s__%s__%s' % (trackable_model.__name__.lower(),field,'avg'))
        output = csv.DictWriter(f,headers,dialect='excel-tab',quoting=csv.QUOTE_ALL)
        # output = UnicodeWriter(f,instances[0].keys(),quoting=csv.QUOTE_ALL)
        output.writerow( dict(zip(headers,headers)) )
        for instance in instances:
            output.writerow( instance )
        f.close()
