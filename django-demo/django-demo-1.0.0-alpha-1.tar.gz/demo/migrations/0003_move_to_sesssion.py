# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for obj in orm.SessionDatabase.objects.all():
            orm.Session.objects.create(id=obj.session, database=obj)


    def backwards(self, orm):
        "Write your backwards methods here."


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
