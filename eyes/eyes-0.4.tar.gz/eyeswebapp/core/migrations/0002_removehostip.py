
from south.db import db
from django.db import models
from core.models import Monitor, Datastore

class Migration:
    # pylint: disable=E1101
    def forwards(self, orm):
        
        # Deleting field 'Monitor.hostip'
        db.delete_column('core_monitor', 'hostip')
        
    
    
    def backwards(self, orm):
        
        # Adding field 'Monitor.hostip'
        db.add_column('core_monitor', 'hostip', orm['core.monitor:hostip'])
        
    
    
    models = {
        'core.datastore': {
            'dstype': ('django.db.models.fields.CharField', [], {'default': "'GAUGE'", 'max_length': '8'}),
            'heartbeat': ('django.db.models.fields.IntegerField', [], {'default': '600'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Monitor']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '18'}),
            'step': ('django.db.models.fields.IntegerField', [], {'default': '300'})
        },
        'core.monitor': {
            'alerting': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
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
