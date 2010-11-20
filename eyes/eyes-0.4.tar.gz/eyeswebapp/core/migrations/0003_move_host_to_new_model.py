# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    # pylint: disable=E1101
    def forwards(self, orm):
        
        # Adding model 'Host'
        db.create_table('core_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(default='localhost', max_length=250)),
        ))
        db.send_create_signal('core', ['Host'])

        # Deleting field 'monitor.hostname'
        db.delete_column('core_monitor', 'hostname')

        # Adding field 'Monitor.host'
        db.add_column('core_monitor', 'host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Host'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Host'
        db.delete_table('core_host')

        # Adding field 'monitor.hostname'
        db.add_column('core_monitor', 'hostname', self.gf('django.db.models.fields.CharField')(default='localhost', max_length=250), keep_default=False)

        # Deleting field 'Monitor.host'
        db.delete_column('core_monitor', 'host_id')


    models = {
        'core.datastore': {
            'Meta': {'object_name': 'Datastore'},
            'dstype': ('django.db.models.fields.CharField', [], {'default': "'GAUGE'", 'max_length': '8'}),
            'heartbeat': ('django.db.models.fields.IntegerField', [], {'default': '600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Monitor']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'step': ('django.db.models.fields.IntegerField', [], {'default': '300'})
        },
        'core.host': {
            'Meta': {'object_name': 'Host'},
            'hostname': ('django.db.models.fields.CharField', [], {'default': "'localhost'", 'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.monitor': {
            'Meta': {'object_name': 'Monitor'},
            'alerting': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Host']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_argset': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'lastupdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'latest_result_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'latest_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'nextupdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'poll_frequency': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        }
    }

    complete_apps = ['core']
