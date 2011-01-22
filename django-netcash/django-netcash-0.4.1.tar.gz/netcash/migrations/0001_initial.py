# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NetcashGateway'
        db.create_table('netcash_netcashgateway', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='gateway', max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('netcash_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal('netcash', ['NetcashGateway'])

        # Adding model 'NetcashOrder'
        db.create_table('netcash_netcashorder', (
            ('Reference', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('TransactionAccepted', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
            ('CardHolderIpAddr', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('Amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('Reason', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('RETC', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('Extra1', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('Extra2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('Extra3', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('gateway', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['netcash.NetcashGateway'], null=True, blank=True)),
        ))
        db.send_create_signal('netcash', ['NetcashOrder'])


    def backwards(self, orm):
        
        # Deleting model 'NetcashGateway'
        db.delete_table('netcash_netcashgateway')

        # Deleting model 'NetcashOrder'
        db.delete_table('netcash_netcashorder')


    models = {
        'netcash.netcashgateway': {
            'Meta': {'object_name': 'NetcashGateway'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'gateway'", 'max_length': '50'}),
            'netcash_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'netcash.netcashorder': {
            'Amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'CardHolderIpAddr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'Extra1': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'Extra2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'Extra3': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'NetcashOrder'},
            'RETC': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'Reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'Reference': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'TransactionAccepted': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['netcash.NetcashGateway']", 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['netcash']
