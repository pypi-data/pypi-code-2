# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Session'
        db.create_table('demo_session', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('database', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sessions', to=orm['demo.SessionDatabase'])),
        ))
        db.send_create_signal('demo', ['Session'])


    def backwards(self, orm):
        
        # Deleting model 'Session'
        db.delete_table('demo_session')


    models = {
        'demo.session': {
            'Meta': {'object_name': 'Session'},
            'database': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sessions'", 'to': "orm['demo.SessionDatabase']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'})
        },
        'demo.sessiondatabase': {
            'Meta': {'ordering': "['-death']", 'object_name': 'SessionDatabase'},
            'death': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['demo']
