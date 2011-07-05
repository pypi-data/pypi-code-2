# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Page'
        db.create_table('contentadmin_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('contentadmin', ['Page'])

        # Adding model 'TextContent'
        db.create_table('contentadmin_textcontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contentadmin.Page'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('admin_label', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('contentadmin', ['TextContent'])

        # Adding model 'ImageContent'
        db.create_table('contentadmin_imagecontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contentadmin.Page'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('admin_label', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('width', self.gf('django.db.models.fields.IntegerField')(default=150)),
            ('height', self.gf('django.db.models.fields.IntegerField')(default=150)),
        ))
        db.send_create_signal('contentadmin', ['ImageContent'])


    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('contentadmin_page')

        # Deleting model 'TextContent'
        db.delete_table('contentadmin_textcontent')

        # Deleting model 'ImageContent'
        db.delete_table('contentadmin_imagecontent')


    models = {
        'contentadmin.imagecontent': {
            'Meta': {'ordering': "['position']", 'object_name': 'ImageContent'},
            'admin_label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contentadmin.Page']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '150'})
        },
        'contentadmin.page': {
            'Meta': {'object_name': 'Page'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'contentadmin.textcontent': {
            'Meta': {'ordering': "['position']", 'object_name': 'TextContent'},
            'admin_label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contentadmin.Page']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['contentadmin']
