# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from projects.models import *
from txcommon.db.models import IntegerTupleField

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Release'
        db.create_table('projects_release', (
            ('id', orm['projects.release:id']),
            ('slug', orm['projects.release:slug']),
            ('name', orm['projects.release:name']),
            ('description', orm['projects.release:description']),
            ('long_description', orm['projects.release:long_description']),
            ('homepage', orm['projects.release:homepage']),
            ('release_date', orm['projects.release:release_date']),
            ('stringfreeze_date', orm['projects.release:stringfreeze_date']),
            ('develfreeze_date', orm['projects.release:develfreeze_date']),
            ('created', orm['projects.release:created']),
            ('modified', orm['projects.release:modified']),
            ('long_description_html', orm['projects.release:long_description_html']),
            ('project', orm['projects.release:project']),
        ))
        db.send_create_signal('projects', ['Release'])
        
        # Dropping ManyToManyField 'Project.collections'
        db.delete_table('projects_project_collections')
        
        # Dropping ManyToManyField 'Component.releases'
        db.delete_table('projects_component_releases')
        
        # Creating unique_together for [slug, project] on Release.
        db.create_unique('projects_release', ['slug', 'project_id'])

        # Adding ManyToManyField 'Release.components'
        db.create_table('projects_release_components', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('release', models.ForeignKey(orm.Release, null=False)),
            ('component', models.ForeignKey(orm.Component, null=False))
        ))
    
    
    def backwards(self, orm):

        # Dropping ManyToManyField 'Release.components'
        db.delete_table('projects_release_components')
                
        # Deleting unique_together for [slug, project] on Release.
        db.delete_unique('projects_release', ['slug', 'project_id'])
        
        # Deleting model 'Release'
        db.delete_table('projects_release')
        
        # Adding ManyToManyField 'Project.collections'
        db.create_table('projects_project_collections', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm.Project, null=False)),
            ('collection', models.ForeignKey(orm['txcollections.collection'], null=False))
        ))
        
        # Adding ManyToManyField 'Component.releases'
        db.create_table('projects_component_releases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('component', models.ForeignKey(orm.Component, null=False)),
            ('collectionrelease', models.ForeignKey(orm['txcollections.collectionrelease'], null=False))
        ))
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'codebases.unit': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_checkout': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'root': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'languages.language': {
            'Meta': {'db_table': "'translations_language'"},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'code_aliases': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'nplurals': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'pluralequation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'specialchars': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'projects.component': {
            'Meta': {'unique_together': "(('project', 'slug'),)"},
            '_unit': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['codebases.Unit']", 'unique': 'True', 'null': 'True', 'db_column': "'unit_id'", 'blank': 'True'}),
            'allows_submission': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'file_filter': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'i18n_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'long_description_html': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pofiles': ('django.contrib.contenttypes.generic.GenericRelation', [], {'to': "orm['translations.POFile']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'should_calculate': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30', 'db_index': 'True'}),
            'source_lang': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'submission_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'projects.project': {
            'anyone_submit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'bug_tracker': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'long_description_html': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'projects.release': {
            'Meta': {'unique_together': "(('slug', 'project'),)"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'develfreeze_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_description': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'long_description_html': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['projects.Project']"}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30', 'db_index': 'True'}),
            'stringfreeze_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'translations.pofile': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'filename'),)"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'fuzzy': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'fuzzy_perc': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_msgmerged': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_pot': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['languages.Language']", 'null': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rev': ('IntegerTupleField', [], {'max_length': '64', 'null': 'True'}),
            'total': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'trans': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'trans_perc': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'untrans': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'untrans_perc': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'})
        }
    }
    
    complete_apps = ['projects']
