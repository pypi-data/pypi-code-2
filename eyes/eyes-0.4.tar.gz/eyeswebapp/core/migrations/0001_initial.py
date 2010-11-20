
from south.db import db
from django.db import models
from core.models import Monitor, Datastore

class Migration:
    # pylint: disable=E1101
    def forwards(self, orm):
        
        # Adding model 'Datastore'
        db.create_table('core_datastore', (
            ('id', orm['core.Datastore:id']),
            ('monitor', orm['core.Datastore:monitor']),
            ('name', orm['core.Datastore:name']),
            ('dstype', orm['core.Datastore:dstype']),
            ('heartbeat', orm['core.Datastore:heartbeat']),
            ('step', orm['core.Datastore:step']),
        ))
        db.send_create_signal('core', ['Datastore'])
        
        # Adding model 'Monitor'
        db.create_table('core_monitor', (
            ('id', orm['core.Monitor:id']),
            ('name', orm['core.Monitor:name']),
            ('kind', orm['core.Monitor:kind']),
            ('json_argset', orm['core.Monitor:json_argset']),
            ('created', orm['core.Monitor:created']),
            ('modified', orm['core.Monitor:modified']),
            ('poll_frequency', orm['core.Monitor:poll_frequency']),
            ('lastupdate', orm['core.Monitor:lastupdate']),
            ('nextupdate', orm['core.Monitor:nextupdate']),
            ('latest_state', orm['core.Monitor:latest_state']),
            ('latest_result_string', orm['core.Monitor:latest_result_string']),
            ('hostname', orm['core.Monitor:hostname']),
            ('hostip', orm['core.Monitor:hostip']),
            ('timeout', orm['core.Monitor:timeout']),
            ('alerting', orm['core.Monitor:alerting']),
        ))
        db.send_create_signal('core', ['Monitor'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Datastore'
        db.delete_table('core_datastore')
        
        # Deleting model 'Monitor'
        db.delete_table('core_monitor')
        
    
    
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
            'hostip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
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
