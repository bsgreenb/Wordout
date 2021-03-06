# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'HOST'
        db.create_table('wordout_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host_name', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['HOST'])

        # Adding model 'IP'
        db.create_table('wordout_ip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['IP'])

        # Adding model 'User_Agent'
        db.create_table('wordout_user_agent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['User_Agent'])

        # Adding model 'Full_Link'
        db.create_table('wordout_full_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.HOST'])),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Full_Link'])

        # Adding model 'Customer_Group'
        db.create_table('wordout_customer_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('max_users', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=10)),
            ('max_actions', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=2)),
        ))
        db.send_create_signal('wordout', ['Customer_Group'])

        # Adding model 'Customer'
        db.create_table('wordout_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('client_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=9)),
            ('api_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('message_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('message_body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('customer_group', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['wordout.Customer_Group'])),
        ))
        db.send_create_signal('wordout', ['Customer'])

        # Adding model 'Sharer'
        db.create_table('wordout_sharer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Customer'])),
            ('customer_sharer_identifier', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=10)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=8, db_index=True)),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sharer_redirect_link', to=orm['wordout.Full_Link'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Sharer'])

        # Adding model 'Click'
        db.create_table('wordout_click', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sharer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Sharer'])),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='click_redirect_link', to=orm['wordout.Full_Link'])),
            ('referrer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Full_Link'], null=True, blank=True)),
            ('IP', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.IP'], null=True, blank=True)),
            ('Agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.User_Agent'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Click'])

        # Adding model 'Action_Type'
        db.create_table('wordout_action_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Customer'])),
            ('customer_action_type_identifier', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=2)),
            ('action_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Action_Type'])

        # Adding model 'Action'
        db.create_table('wordout_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('click', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Click'])),
            ('action_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Action_Type'])),
            ('extra_data', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Action'])


    def backwards(self, orm):
        
        # Deleting model 'HOST'
        db.delete_table('wordout_host')

        # Deleting model 'IP'
        db.delete_table('wordout_ip')

        # Deleting model 'User_Agent'
        db.delete_table('wordout_user_agent')

        # Deleting model 'Full_Link'
        db.delete_table('wordout_full_link')

        # Deleting model 'Customer_Group'
        db.delete_table('wordout_customer_group')

        # Deleting model 'Customer'
        db.delete_table('wordout_customer')

        # Deleting model 'Sharer'
        db.delete_table('wordout_sharer')

        # Deleting model 'Click'
        db.delete_table('wordout_click')

        # Deleting model 'Action_Type'
        db.delete_table('wordout_action_type')

        # Deleting model 'Action'
        db.delete_table('wordout_action')


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
        'wordout.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Action_Type']"}),
            'click': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Click']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.action_type': {
            'Meta': {'object_name': 'Action_Type'},
            'action_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Customer']"}),
            'customer_action_type_identifier': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.click': {
            'Agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.User_Agent']", 'null': 'True', 'blank': 'True'}),
            'IP': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.IP']", 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Click'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redirect_link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'click_redirect_link'", 'to': "orm['wordout.Full_Link']"}),
            'referrer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Full_Link']", 'null': 'True', 'blank': 'True'}),
            'sharer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Sharer']"})
        },
        'wordout.customer': {
            'Meta': {'object_name': 'Customer'},
            'api_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'client_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9'}),
            'customer_group': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['wordout.Customer_Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'message_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'wordout.customer_group': {
            'Meta': {'object_name': 'Customer_Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_actions': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2'}),
            'max_users': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '10'})
        },
        'wordout.full_link': {
            'Meta': {'object_name': 'Full_Link'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.HOST']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'wordout.host': {
            'Meta': {'object_name': 'HOST'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host_name': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.ip': {
            'Meta': {'object_name': 'IP'},
            'address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.sharer': {
            'Meta': {'object_name': 'Sharer'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Customer']"}),
            'customer_sharer_identifier': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '10'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'redirect_link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sharer_redirect_link'", 'to': "orm['wordout.Full_Link']"})
        },
        'wordout.user_agent': {
            'Meta': {'object_name': 'User_Agent'},
            'agent': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['wordout']
