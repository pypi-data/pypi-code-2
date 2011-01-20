# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = u'Import news from forum into couchdb'
    
    
    def execute(self, **options):
        pass
    
        
