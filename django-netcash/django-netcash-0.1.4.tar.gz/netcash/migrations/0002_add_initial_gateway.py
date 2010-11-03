# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from netcash.models import random_secret

class Migration(DataMigration):

    def forwards(self, orm):
        gateway = orm.NetcashGateway.objects.create()
        gateway.secret = random_secret()
        gateway.slug = 'gateway'
        gateway.save()
        "Write your forwards methods here."


    def backwards(self, orm):
        "Write your backwards methods here."


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
