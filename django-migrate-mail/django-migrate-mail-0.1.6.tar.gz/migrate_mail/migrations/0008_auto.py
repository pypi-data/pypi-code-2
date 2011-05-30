# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Label', fields ['uid']
        db.create_index('migrate_mail_label', ['uid'])


    def backwards(self, orm):
        
        # Removing index on 'Label', fields ['uid']
        db.delete_index('migrate_mail_label', ['uid'])


    models = {
        'migrate_mail.label': {
            'Meta': {'object_name': 'Label'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'migration': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['migrate_mail.Migration']"}),
            'uid': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'migrate_mail.migration': {
            'Meta': {'unique_together': "(('from_email', 'to_username'),)", 'object_name': 'Migration'},
            'admin_password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'admin_username': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'auth_token': ('django.db.models.fields.TextField', [], {}),
            'current_label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'current_since': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(1990, 1, 1)'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'from_password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_uid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'messages_cnt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'since': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(1990, 1, 1)'}),
            'to_username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['migrate_mail']
