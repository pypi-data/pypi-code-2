# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Renaming model 'ExternalLink'
        db.rename_table('panorama_panoramaexternallink','panorama_externallink')

        # Renaming model 'Link'
        db.rename_table('panorama_panoramalink', 'panorama_link')

        # Renaming model 'ExternalLinkTranslation'
        db.rename_table('panorama_panoramaexternallink_translation',
                        'panorama_externallink_translation')

        # Renaming model 'Note'
        db.rename_table('panorama_panoramanote', 'panorama_note')

        # Renaming model 'NoteTranslation'
        db.rename_table('panorama_panoramanote_translation', 'panorama_note_translation')

    def backwards(self, orm):

        # Renaming model 'ExternalLink'
        db.rename_table('panorama_externallink','panorama_panoramaexternallink')

        # Renaming model 'Link'
        db.rename_table('panorama_link', 'panorama_panoramalink')

        # Renaming model 'ExternalLinkTranslation'
        db.rename_table('panorama_externallink_translation',
                        'panorama_panoramaexternallink_translation')

        # Renaming model 'Note'
        db.rename_table('panorama_note', 'panorama_panoramanote')

        # Renaming model 'NoteTranslation'
        db.rename_table('panorama_note_translation', 'panorama_panoramanote_translation')


    models = {
        'panorama.externallink': {
            'Meta': {'object_name': 'ExternalLink', '_ormbases': ['panorama.PanoramaInfo']},
            'panoramainfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['panorama.PanoramaInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'panorama.externallinktranslation': {
            'Meta': {'ordering': "('language_code',)", 'unique_together': "(('language_code', 'master'),)", 'object_name': 'ExternalLinkTranslation', 'db_table': "'panorama_externallink_translation'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'blank': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['panorama.ExternalLink']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'panorama.link': {
            'Meta': {'object_name': 'Link', '_ormbases': ['panorama.PanoramaInfo']},
            'panoramainfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['panorama.PanoramaInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'target_panorama': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['panorama.Panorama']"})
        },
        'panorama.note': {
            'Meta': {'object_name': 'Note', '_ormbases': ['panorama.PanoramaInfo']},
            'panoramainfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['panorama.PanoramaInfo']", 'unique': 'True', 'primary_key': 'True'})
        },
        'panorama.notetranslation': {
            'Meta': {'ordering': "('language_code',)", 'unique_together': "(('language_code', 'master'),)", 'object_name': 'NoteTranslation', 'db_table': "'panorama_note_translation'"},
            'description': ('tinymce.models.HTMLField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '15', 'blank': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'to': "orm['panorama.Note']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
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
        'panorama.panoramainfo': {
            'Meta': {'object_name': 'PanoramaInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'panorama': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'panorama'", 'to': "orm['panorama.Panorama']"}),
            'x0': ('django.db.models.fields.IntegerField', [], {}),
            'x1': ('django.db.models.fields.IntegerField', [], {}),
            'y0': ('django.db.models.fields.IntegerField', [], {}),
            'y1': ('django.db.models.fields.IntegerField', [], {})
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
