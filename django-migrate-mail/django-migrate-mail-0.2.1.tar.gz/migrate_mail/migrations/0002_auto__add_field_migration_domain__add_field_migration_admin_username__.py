# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Migration.domain'
        db.add_column('migrate_mail_migration', 'domain', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'Migration.admin_username'
        db.add_column('migrate_mail_migration', 'admin_username', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'Migration.admin_password'
        db.add_column('migrate_mail_migration', 'admin_password', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'Migration.from_password'
        db.add_column('migrate_mail_migration', 'from_password', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Changing field 'Migration.to_username'
        db.alter_column('migrate_mail_migration', 'to_username', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Adding unique constraint on 'Migration', fields ['to_username', 'from_email']
        db.create_unique('migrate_mail_migration', ['to_username', 'from_email'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Migration', fields ['to_username', 'from_email']
        db.delete_unique('migrate_mail_migration', ['to_username', 'from_email'])

        # Deleting field 'Migration.domain'
        db.delete_column('migrate_mail_migration', 'domain')

        # Deleting field 'Migration.admin_username'
        db.delete_column('migrate_mail_migration', 'admin_username')

        # Deleting field 'Migration.admin_password'
        db.delete_column('migrate_mail_migration', 'admin_password')

        # Deleting field 'Migration.from_password'
        db.delete_column('migrate_mail_migration', 'from_password')

        # Changing field 'Migration.to_username'
        db.alter_column('migrate_mail_migration', 'to_username', self.gf('django.db.models.fields.CharField')(max_length=255))


    models = {
        'migrate_mail.label': {
            'Meta': {'object_name': 'Label'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.TextField', [], {}),
            'migration': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['migrate_mail.Migration']"}),
            'uid': ('django.db.models.fields.IntegerField', [], {})
        },
        'migrate_mail.migration': {
            'Meta': {'unique_together': "(('from_email', 'to_username'),)", 'object_name': 'Migration'},
            'admin_password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'admin_username': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'from_password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'since': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(1990, 1, 1)'}),
            'to_username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['migrate_mail']
