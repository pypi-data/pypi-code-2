# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ValidationFailure'
        db.create_table('output_validator_validationfailure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('path', self.gf('django.db.models.fields.TextField')()),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('request', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('response', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('errors', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('output_validator', ['ValidationFailure'])


    def backwards(self, orm):
        
        # Deleting model 'ValidationFailure'
        db.delete_table('output_validator_validationfailure')


    models = {
        'output_validator.validationfailure': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'ValidationFailure'},
            'errors': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'path': ('django.db.models.fields.TextField', [], {}),
            'request': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['output_validator']
