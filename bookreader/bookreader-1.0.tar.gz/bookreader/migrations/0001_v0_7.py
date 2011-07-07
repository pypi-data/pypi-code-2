# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Repository'
        db.create_table('bookreader_repository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('bookreader', ['Repository'])

        # Adding model 'Collection'
        db.create_table('bookreader_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(related_name='collections', to=orm['bookreader.Repository'])),
            ('handle', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('bookreader', ['Collection'])

        # Adding unique constraint on 'Collection', fields ['repository', 'handle']
        db.create_unique('bookreader_collection', ['repository_id', 'handle'])

        # Adding model 'Book'
        db.create_table('bookreader_book', (
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(related_name='books', to=orm['bookreader.Collection'])),
            ('canonical', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='copies', null=True, to=orm['bookreader.Book'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('issued', self.gf('django.db.models.fields.DateTimeField')()),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('additional_metadata', self.gf('bookreader.fields.MultiValueDictField')(null=True, blank=True)),
        ))
        db.send_create_signal('bookreader', ['Book'])

        # Adding model 'Page'
        db.create_table('bookreader_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['bookreader.Book'])),
            ('internal', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('sequence', self.gf('django.db.models.fields.PositiveIntegerField')(default=9999)),
            ('jp2', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('bookreader', ['Page'])

        # Adding model 'Link'
        db.create_table('bookreader_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='links', to=orm['bookreader.Book'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('bundle', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('bookreader', ['Link'])

        # Adding model 'Annotation'
        db.create_table('bookreader_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='annotations', to=orm['bookreader.Book'])),
            ('offset', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('length', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('structural', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('bookreader', ['Annotation'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Collection', fields ['repository', 'handle']
        db.delete_unique('bookreader_collection', ['repository_id', 'handle'])

        # Deleting model 'Repository'
        db.delete_table('bookreader_repository')

        # Deleting model 'Collection'
        db.delete_table('bookreader_collection')

        # Deleting model 'Book'
        db.delete_table('bookreader_book')

        # Deleting model 'Page'
        db.delete_table('bookreader_page')

        # Deleting model 'Link'
        db.delete_table('bookreader_link')

        # Deleting model 'Annotation'
        db.delete_table('bookreader_annotation')


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
