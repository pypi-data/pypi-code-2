# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PanoramaTranslation'
        db.create_table('panorama_panorama_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('language_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=15, blank=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['panorama.Panorama'])),
        ))
        db.send_create_signal('panorama', ['PanoramaTranslation'])

        # Adding unique constraint on 'PanoramaTranslation', fields ['language_code', 'master']
        db.create_unique('panorama_panorama_translation', ['language_code', 'master_id'])

        # Adding model 'Panorama'
        db.create_table('panorama_panorama', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('panorama', ['Panorama'])

        # Adding model 'PanoramaInfo'
        db.create_table('panorama_panoramainfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('panorama', self.gf('django.db.models.fields.related.ForeignKey')(related_name='panorama', to=orm['panorama.Panorama'])),
            ('x0', self.gf('django.db.models.fields.IntegerField')()),
            ('x1', self.gf('django.db.models.fields.IntegerField')()),
            ('y0', self.gf('django.db.models.fields.IntegerField')()),
            ('y1', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('panorama', ['PanoramaInfo'])

        # Adding model 'PanoramaExternalLinkTranslation'
        db.create_table('panorama_panoramaexternallink_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('language_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=15, blank=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['panorama.PanoramaExternalLink'])),
        ))
        db.send_create_signal('panorama', ['PanoramaExternalLinkTranslation'])

        # Adding unique constraint on 'PanoramaExternalLinkTranslation', fields ['language_code', 'master']
        db.create_unique('panorama_panoramaexternallink_translation', ['language_code', 'master_id'])

        # Adding model 'PanoramaExternalLink'
        db.create_table('panorama_panoramaexternallink', (
            ('panoramainfo_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['panorama.PanoramaInfo'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('panorama', ['PanoramaExternalLink'])

        # Adding model 'PanoramaNoteTranslation'
        db.create_table('panorama_panoramanote_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('tinymce.models.HTMLField')(blank=True)),
            ('language_code', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=15, blank=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', to=orm['panorama.PanoramaNote'])),
        ))
        db.send_create_signal('panorama', ['PanoramaNoteTranslation'])

        # Adding unique constraint on 'PanoramaNoteTranslation', fields ['language_code', 'master']
        db.create_unique('panorama_panoramanote_translation', ['language_code', 'master_id'])

        # Adding model 'PanoramaNote'
        db.create_table('panorama_panoramanote', (
            ('panoramainfo_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['panorama.PanoramaInfo'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('panorama', ['PanoramaNote'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PanoramaNoteTranslation', fields ['language_code', 'master']
        db.delete_unique('panorama_panoramanote_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'PanoramaExternalLinkTranslation', fields ['language_code', 'master']
        db.delete_unique('panorama_panoramaexternallink_translation', ['language_code', 'master_id'])

        # Removing unique constraint on 'PanoramaTranslation', fields ['language_code', 'master']
        db.delete_unique('panorama_panorama_translation', ['language_code', 'master_id'])

        # Deleting model 'PanoramaTranslation'
        db.delete_table('panorama_panorama_translation')

        # Deleting model 'Panorama'
        db.delete_table('panorama_panorama')

        # Deleting model 'PanoramaInfo'
        db.delete_table('panorama_panoramainfo')

        # Deleting model 'PanoramaExternalLinkTranslation'
        db.delete_table('panorama_panoramaexternallink_translation')

        # Deleting model 'PanoramaExternalLink'
        db.delete_table('panorama_panoramaexternallink')

        # Deleting model 'PanoramaNoteTranslation'
        db.delete_table('panorama_panoramanote_translation')

        # Deleting model 'PanoramaNote'
        db.delete_table('panorama_panoramanote')


    models = {
        'panorama.panorama': {
            'Meta': {'object_name': 'Panorama'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'panorama.panoramaexternallink': {
            'Meta': {'object_name': 'PanoramaExternalLink', '_ormbases': ['panorama.PanoramaInfo']},
            'panoramainfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['panorama.PanoramaInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'panorama.panoramaexternallinktranslation': {
            'Meta': {'ordering': "('language_code',)", 'unique_together': "(('language_code', 'master'),)", 'object_name': 'PanoramaExternalLinkTranslation', 'db_table': "'panorama_panoramaexternallink_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'blank': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['panorama.PanoramaExternalLink']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'panorama.panoramainfo': {
            'Meta': {'object_name': 'PanoramaInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'panorama': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'panorama'", 'to': "orm['panorama.Panorama']"}),
            'x0': ('django.db.models.fields.IntegerField', [], {}),
            'x1': ('django.db.models.fields.IntegerField', [], {}),
            'y0': ('django.db.models.fields.IntegerField', [], {}),
            'y1': ('django.db.models.fields.IntegerField', [], {})
        },
        'panorama.panoramanote': {
            'Meta': {'object_name': 'PanoramaNote', '_ormbases': ['panorama.PanoramaInfo']},
            'panoramainfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['panorama.PanoramaInfo']", 'unique': 'True', 'primary_key': 'True'})
        },
        'panorama.panoramanotetranslation': {
            'Meta': {'ordering': "('language_code',)", 'unique_together': "(('language_code', 'master'),)", 'object_name': 'PanoramaNoteTranslation', 'db_table': "'panorama_panoramanote_translation'"},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'blank': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['panorama.PanoramaNote']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'panorama.panoramatranslation': {
            'Meta': {'ordering': "('language_code',)", 'unique_together': "(('language_code', 'master'),)", 'object_name': 'PanoramaTranslation', 'db_table': "'panorama_panorama_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'blank': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['panorama.Panorama']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['panorama']
