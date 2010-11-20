# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    # pylint: disable=E1101
    def forwards(self, orm):
        "Write your forwards methods here."
        for monitor in orm.Monitor.objects.all():
            monitor.passive = False
            monitor.save()

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'core.datastore': {
            'Meta': {'ordering': "['name']", 'object_name': 'Datastore'},
            'dstype': ('django.db.models.fields.CharField', [], {'default': "'GAUGE'", 'max_length': '8'}),
            'heartbeat': ('django.db.models.fields.IntegerField', [], {'default': '600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Monitor']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'step': ('django.db.models.fields.IntegerField', [], {'default': '300'})
        },
        'core.host': {
            'Meta': {'ordering': "['hostname']", 'object_name': 'Host'},
            'hostname': ('django.db.models.fields.CharField', [], {'default': "'localhost'", 'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.monitor': {
            'Meta': {'object_name': 'Monitor'},
            'alerting': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Host']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_argset': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'lastupdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'latest_result_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'latest_state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'nextupdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'passive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'plugin_name': ('django.db.models.fields.CharField', [], {'default': "'check_ping'", 'max_length': '250'}),
            'poll_frequency': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        }
    }

    complete_apps = ['core']
