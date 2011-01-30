# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PanoramaLink'
        db.create_table('panorama_panoramalink', (
            ('panoramainfo_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['panorama.PanoramaInfo'], unique=True, primary_key=True)),
            ('target_panorama', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['panorama.Panorama'])),
        ))
        db.send_create_signal('panorama', ['PanoramaLink'])


    def backwards(self, orm):
        
        # Deleting model 'PanoramaLink'
        db.delete_table('panorama_panoramalink')


    models = {
        'panorama.panorama': {
            'Meta': {'object_name': 'Panorama'},
            'auto_start': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'control_display': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'mode_360': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'speed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_position': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'viewport_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
        'panorama.panoramalink': {
            'Meta': {'object_name': 'PanoramaLink', '_ormbases': ['panorama.PanoramaInfo']},
            'panoramainfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['panorama.PanoramaInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'target_panorama': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['panorama.Panorama']"})
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
