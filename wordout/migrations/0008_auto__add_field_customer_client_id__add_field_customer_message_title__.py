# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Customer.client_id'
        db.add_column('wordout_customer', 'client_id', self.gf('django.db.models.fields.CharField')(default=123456789, max_length=9), keep_default=False)

        # Adding field 'Customer.message_title'
        db.add_column('wordout_customer', 'message_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Customer.message_body'
        db.add_column('wordout_customer', 'message_body', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Customer.client_id'
        db.delete_column('wordout_customer', 'client_id')

        # Deleting field 'Customer.message_title'
        db.delete_column('wordout_customer', 'message_title')

        # Deleting field 'Customer.message_body'
        db.delete_column('wordout_customer', 'message_body')


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
        'wordout.customer': {
            'Meta': {'object_name': 'Customer'},
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'message_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'wordout.full_link': {
            'Meta': {'object_name': 'Full_Link'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.HOST']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Path']"})
        },
        'wordout.host': {
            'Meta': {'object_name': 'HOST'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host_name': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.identifiers': {
            'Meta': {'object_name': 'Identifiers'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Customer']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'redirect_link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifier_redirect_link'", 'to': "orm['wordout.Full_Link']"})
        },
        'wordout.ip': {
            'Meta': {'object_name': 'IP'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.path': {
            'Meta': {'object_name': 'Path'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path_loc': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'wordout.request': {
            'Agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.User_Agent']", 'null': 'True', 'blank': 'True'}),
            'IP': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.IP']", 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Request'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redirect_link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'request_redirect_link'", 'to': "orm['wordout.Full_Link']"}),
            'referral_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Identifiers']"}),
            'referrer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Full_Link']", 'null': 'True', 'blank': 'True'})
        },
        'wordout.user_agent': {
            'Meta': {'object_name': 'User_Agent'},
            'agent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['wordout']
