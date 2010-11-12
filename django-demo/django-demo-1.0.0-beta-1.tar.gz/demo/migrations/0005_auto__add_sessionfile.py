# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SessionFile'
        db.create_table('demo_sessionfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('database', self.gf('django.db.models.fields.related.ForeignKey')(related_name='files', to=orm['demo.SessionDatabase'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('demo', ['SessionFile'])


    def backwards(self, orm):
        
        # Deleting model 'SessionFile'
        db.delete_table('demo_sessionfile')


    models = {
        'demo.session': {
            'Meta': {'object_name': 'Session'},
            'database': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sessions'", 'to': "orm['demo.SessionDatabase']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'})
        },
        'demo.sessiondatabase': {
            'Meta': {'ordering': "['-death']", 'object_name': 'SessionDatabase'},
            'death': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'demo.sessionfile': {
            'Meta': {'object_name': 'SessionFile'},
            'database': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['demo.SessionDatabase']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['demo']
