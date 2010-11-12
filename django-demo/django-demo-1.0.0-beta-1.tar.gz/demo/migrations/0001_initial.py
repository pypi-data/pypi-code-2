# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SessionDatabase'
        db.create_table('demo_sessiondatabase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('death', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('demo', ['SessionDatabase'])


    def backwards(self, orm):
        
        # Deleting model 'SessionDatabase'
        db.delete_table('demo_sessiondatabase')


    models = {
        'demo.sessiondatabase': {
            'Meta': {'ordering': "['-death']", 'object_name': 'SessionDatabase'},
            'death': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['demo']
