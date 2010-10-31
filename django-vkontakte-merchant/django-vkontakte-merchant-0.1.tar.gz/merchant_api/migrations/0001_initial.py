# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Order'
        db.create_table('merchant_api_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_id', self.gf('django.db.models.fields.IntegerField')()),
            ('wish_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('merchant_id', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_test', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notification_type', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('new_state', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('currency_str', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('order_date', self.gf('merchant_api.fields.ISO8601Field')()),
            ('django_user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='vk_orders', null=True, to=orm['auth.User'])),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('shipping_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('shipping_method', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('shipping_country', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('shipping_country_str', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('shipping_code', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('shipping_city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('shipping_street', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('shipping_house', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('shipping_flat', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('shipping_phone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('recipient_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('recipient_phone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('merchant_api', ['Order'])

        # Adding unique constraint on 'Order', fields ['order_id', 'is_test']
        db.create_unique('merchant_api_order', ['order_id', 'is_test'])

        # Adding model 'CustomField'
        db.create_table('merchant_api_customfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='custom_fields', to=orm['merchant_api.Order'])),
        ))
        db.send_create_signal('merchant_api', ['CustomField'])

        # Adding unique constraint on 'CustomField', fields ['number', 'order']
        db.create_unique('merchant_api_customfield', ['number', 'order_id'])

        # Adding model 'Item'
        db.create_table('merchant_api_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['merchant_api.Order'])),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('item_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('currency_str', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal('merchant_api', ['Item'])

        # Adding unique constraint on 'Item', fields ['number', 'order']
        db.create_unique('merchant_api_item', ['number', 'order_id'])

        # Adding model 'OrderChange'
        db.create_table('merchant_api_orderchange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['merchant_api.Order'])),
            ('changed_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('changes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('merchant_api', ['OrderChange'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Item', fields ['number', 'order']
        db.delete_unique('merchant_api_item', ['number', 'order_id'])

        # Removing unique constraint on 'CustomField', fields ['number', 'order']
        db.delete_unique('merchant_api_customfield', ['number', 'order_id'])

        # Removing unique constraint on 'Order', fields ['order_id', 'is_test']
        db.delete_unique('merchant_api_order', ['order_id', 'is_test'])

        # Deleting model 'Order'
        db.delete_table('merchant_api_order')

        # Deleting model 'CustomField'
        db.delete_table('merchant_api_customfield')

        # Deleting model 'Item'
        db.delete_table('merchant_api_item')

        # Deleting model 'OrderChange'
        db.delete_table('merchant_api_orderchange')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'merchant_api.customfield': {
            'Meta': {'unique_together': "(('number', 'order'),)", 'object_name': 'CustomField'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_fields'", 'to': "orm['merchant_api.Order']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'merchant_api.item': {
            'Meta': {'unique_together': "(('number', 'order'),)", 'object_name': 'Item'},
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_str': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['merchant_api.Order']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'merchant_api.order': {
            'Meta': {'unique_together': "(['order_id', 'is_test'],)", 'object_name': 'Order'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_str': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'django_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'vk_orders'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_test': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'merchant_id': ('django.db.models.fields.IntegerField', [], {}),
            'new_state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'notification_type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'order_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'order_date': ('merchant_api.fields.ISO8601Field', [], {}),
            'order_id': ('django.db.models.fields.IntegerField', [], {}),
            'recipient_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'recipient_phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shipping_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'shipping_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'shipping_country_str': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'shipping_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'shipping_flat': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'shipping_house': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shipping_phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'shipping_street': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'wish_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'merchant_api.orderchange': {
            'Meta': {'ordering': "['-id']", 'object_name': 'OrderChange'},
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'changes': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['merchant_api.Order']"})
        }
    }

    complete_apps = ['merchant_api']
