# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'SessionDatabase.session'
        db.delete_column('demo_sessiondatabase', 'session')


    def backwards(self, orm):
        
        # We cannot add back in field 'SessionDatabase.session'
        raise RuntimeError(
            "Cannot reverse this migration. 'SessionDatabase.session' and its values cannot be restored.")


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
        }
    }

    complete_apps = ['demo']
