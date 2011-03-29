# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        db.add_column('bookreader_book', 'type', self.gf('django.db.models.fields.CharField')(default='extant', max_length=32, db_index=True), keep_default=True)
        db.add_column('bookreader_book', 'work', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='manifestations', null=True, to=orm['bookreader.Book']), keep_default=False)
        db.add_column('bookreader_book', 'published', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=True)
        db.add_column('bookreader_repository', 'oai_path', self.gf('django.db.models.fields.CharField')(default='dspace-oai/request', max_length=255), keep_default=True)
        db.add_column('bookreader_repository', 'sword_enabled', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=True)
        db.add_column('bookreader_repository', 'sword_service_path', self.gf('django.db.models.fields.CharField')(default='sword/servicedocument', max_length=255), keep_default=True)
        db.add_column('bookreader_repository', 'sword_deposit_path', self.gf('django.db.models.fields.CharField')(default='sword/deposit', max_length=255), keep_default=True)
        db.add_column('bookreader_repository', 'sword_user', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)
        db.add_column('bookreader_repository', 'sword_password', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)
    
    def backwards(self, orm):
        db.delete_column('bookreader_book', 'type')
        db.delete_column('bookreader_book', 'work_id')
        db.delete_column('bookreader_book', 'published')
        db.delete_column('bookreader_repository', 'oai_path')
        db.delete_column('bookreader_repository', 'sword_enabled')
        db.delete_column('bookreader_repository', 'sword_service_path')
        db.delete_column('bookreader_repository', 'sword_deposit_path')
        db.delete_column('bookreader_repository', 'sword_user')
        db.delete_column('bookreader_repository', 'sword_password')

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
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thumbnail': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'extant'", 'max_length': '32', 'db_index': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'manifestations'", 'null': 'True', 'to': "orm['bookreader.Book']"})
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
            'oai_path': ('django.db.models.fields.CharField', [], {'default': "'dspace-oai/request'", 'max_length': '255'}),
            'sword_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sword_deposit_path': ('django.db.models.fields.CharField', [], {'default': "'sword/deposit'", 'max_length': '255'}),
            'sword_password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sword_service_path': ('django.db.models.fields.CharField', [], {'default': "'sword/servicedocument'", 'max_length': '255'}),
            'sword_user': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['bookreader']
