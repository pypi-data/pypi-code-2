from StringIO import StringIO
import urllib
from zipfile import ZipFile
from common.progress import Progress

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError

from ipgeo.models import Location, Range

class Command(BaseCommand):
    help = 'Update ipgeo application database'

    @transaction.commit_on_success
    def handle(self, *args, **options):
        print 'Downloading the archive'
        url = 'http://ipgeobase.ru/files/db/Main/geo_files.zip'
        data = urllib.urlopen(url).read()
        zfile = ZipFile(StringIO(data))

        print 'Deleting old objects'
        Location.objects.all().delete()
        Range.objects.all().delete()

        print 'Importing locations'
        for line in zfile.open('cities.txt'):
            keys = ['pk', 'name', 'region', 'area', 'lat', 'lon']
            args = dict(zip(keys, line.decode('cp1251').strip().split('\t')))
            loc = Location.objects.create(**args)

        print 'Importing IP ranges'
        # We know approximate number of range records
        prog = Progress(total=120000)
        for line in zfile.open('cidr_optim.txt'):
            prog.tick()
            keys = ['start', 'end', 'description', 'country', 'location_id']
            args = dict(zip(keys, line.strip().split('\t')))
            if args['location_id'] == '-':
                args['location_id'] = None
            obj = Range.objects.create(**args)
