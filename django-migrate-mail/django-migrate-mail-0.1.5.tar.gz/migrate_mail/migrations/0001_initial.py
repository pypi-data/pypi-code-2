# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Migration'
        db.create_table('migrate_mail_migration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('to_username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('since', self.gf('django.db.models.fields.DateField')(default=datetime.date(1990, 1, 1))),
        ))
        db.send_create_signal('migrate_mail', ['Migration'])

        # Adding model 'Label'
        db.create_table('migrate_mail_label', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('migration', self.gf('django.db.models.fields.related.ForeignKey')(related_name='labels', to=orm['migrate_mail.Migration'])),
            ('uid', self.gf('django.db.models.fields.IntegerField')()),
            ('labels', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('migrate_mail', ['Label'])


    def backwards(self, orm):
        
        # Deleting model 'Migration'
        db.delete_table('migrate_mail_migration')

        # Deleting model 'Label'
        db.delete_table('migrate_mail_label')


    models = {
        'migrate_mail.label': {
            'Meta': {'object_name': 'Label'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.TextField', [], {}),
            'migration': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'labels'", 'to': "orm['migrate_mail.Migration']"}),
            'uid': ('django.db.models.fields.IntegerField', [], {})
        },
        'migrate_mail.migration': {
            'Meta': {'object_name': 'Migration'},
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'since': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(1990, 1, 1)'}),
            'to_username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['migrate_mail']
