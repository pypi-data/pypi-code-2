# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Book.is_canonical'
        db.add_column('bookreader_book', 'is_canonical', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Book.is_canonical'
        db.delete_column('bookreader_book', 'is_canonical')


    models = {
        'bookreader.annotation': {
            'Meta': {'ordering': "('book', 'offset', '-length')", 'object_name': 'Annotation'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'annotations'", 'to': "orm['bookreader.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'offset': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'structural': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'bookreader.book': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Book'},
            'additional_metadata': ('bookreader.fields.MultiValueDictField', [], {'null': 'True', 'blank': 'True'}),
            'canonical': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'copies'", 'null': 'True', 'to': "orm['bookreader.Book']"}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['bookreader.Collection']"}),
            'created': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'is_canonical': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'issued': ('django.db.models.fields.DateTimeField', [], {}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'bookreader.collection': {
            'Meta': {'ordering': "('name', 'handle')", 'unique_together': "(('repository', 'handle'),)", 'object_name': 'Collection'},
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collections'", 'to': "orm['bookreader.Repository']"})
        },
        'bookreader.link': {
            'Meta': {'ordering': "('book', 'title')", 'object_name': 'Link'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['bookreader.Book']"}),
            'bundle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'bookreader.page': {
            'Meta': {'ordering': "('book', 'sequence', 'title')", 'object_name': 'Page'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': "orm['bookreader.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'jp2': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.PositiveIntegerField', [], {'default': '9999'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'bookreader.repository': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Repository'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['bookreader']
