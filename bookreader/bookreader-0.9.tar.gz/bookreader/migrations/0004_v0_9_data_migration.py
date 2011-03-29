# encoding: utf-8
from urlparse import urlparse

from south.db import db
from south.v2 import SchemaMigration



class Migration(SchemaMigration):
    
    no_dry_run = True
    
    def forwards(self, orm):
        for book in orm.Book.objects.all():
            if book.is_canonical:
                if book.pages.filter(jp2__isnull=False).count() > 0:
                    book.type = 'frankenbook'
                else:
                    book.type = 'canonical'
            else:
                book.type = 'extant'
            book.save()
        
        for repository in orm.Repository.objects.all():
            try:
                parsed = urlparse(repository.url)
                repository.url = '%s://%s' % (parsed[0], parsed[1])
                repository.oai_path = parsed[2].ltrim('/')
                repository.save()
            except:
                pass
    
    def backwards(self, orm):
        for book in orm.Book.objects.all():
            if book.type in ('canonical', 'frankenbook'):
                book.is_canonical = True
            elif book.type == 'extant':
                book.is_canonical = False
            book.save()
        
        for repository in orm.Repository.objects.all():
            repository.url = '%s/%s' % (repository.url, repository.oai_path)

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
