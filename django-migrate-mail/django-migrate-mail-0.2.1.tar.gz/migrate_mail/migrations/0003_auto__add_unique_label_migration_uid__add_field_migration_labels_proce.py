# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Label', fields ['migration', 'uid']
        db.create_unique('migrate_mail_label', ['migration_id', 'uid'])

        # Adding field 'Migration.labels_processed'
        db.add_column('migrate_mail_migration', 'labels_processed', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Migration.current_since'
        db.add_column('migrate_mail_migration', 'current_since', self.gf('django.db.models.fields.DateField')(default=datetime.date(1990, 1, 1)), keep_default=False)

        # Adding field 'Migration.current_label'
        db.add_column('migrate_mail_migration', 'current_label', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Removing unique constraint on 'Label', fields ['migration', 'uid']
        db.delete_unique('migrate_mail_label', ['migration_id', 'uid'])

        # Deleting field 'Migration.labels_processed'
        db.delete_column('migrate_mail_migration', 'labels_processed')

        # Deleting field 'Migration.current_since'
        db.delete_column('migrate_mail_migration', 'current_since')

        # Deleting field 'Migration.current_label'
        db.delete_column('migrate_mail_migration', 'current_label')


    models = {
        'migrate_mail.label': {
            'Meta': {'unique_together': "(('migration', 'uid'),)", 'object_name': 'Label'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.TextField', [], {}),
            'migration': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['migrate_mail.Migration']"}),
            'uid': ('django.db.models.fields.IntegerField', [], {})
        },
        'migrate_mail.migration': {
            'Meta': {'unique_together': "(('from_email', 'to_username'),)", 'object_name': 'Migration'},
            'admin_password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'admin_username': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'current_label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'current_since': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(1990, 1, 1)'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'from_password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels_processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'since': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(1990, 1, 1)'}),
            'to_username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['migrate_mail']
