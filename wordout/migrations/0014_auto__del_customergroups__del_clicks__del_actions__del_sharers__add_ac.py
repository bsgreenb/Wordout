# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Customergroups'
        db.delete_table('wordout_customergroups')

        # Deleting model 'Clicks'
        db.delete_table('wordout_clicks')

        # Deleting model 'Actions'
        db.delete_table('wordout_actions')

        # Deleting model 'Sharers'
        db.delete_table('wordout_sharers')

        # Adding model 'Action'
        db.create_table('wordout_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('click', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Click'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Action_Type'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Action'])

        # Adding model 'Sharer'
        db.create_table('wordout_sharer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Customer'])),
            ('customer_sharer_id', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=8, db_index=True)),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sharer_redirect_link', to=orm['wordout.Full_Link'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Sharer'])

        # Adding model 'Customergroup'
        db.create_table('wordout_customergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('max_users', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
        ))
        db.send_create_signal('wordout', ['Customergroup'])

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

        # Changing field 'Customer.customergroup'
        db.alter_column('wordout_customer', 'customergroup_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Customergroup']))


    def backwards(self, orm):
        
        # Adding model 'Customergroups'
        db.create_table('wordout_customergroups', (
            ('max_users', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('wordout', ['Customergroups'])

        # Adding model 'Clicks'
        db.create_table('wordout_clicks', (
            ('referrer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Full_Link'], null=True, blank=True)),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='click_redirect_link', to=orm['wordout.Full_Link'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('IP', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.IP'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.User_Agent'], null=True, blank=True)),
            ('sharer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Sharers'])),
        ))
        db.send_create_signal('wordout', ['Clicks'])

        # Adding model 'Actions'
        db.create_table('wordout_actions', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('click', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Clicks'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Action_Type'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('wordout', ['Actions'])

        # Adding model 'Sharers'
        db.create_table('wordout_sharers', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=8, unique=True, db_index=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Customer'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('customer_sharer_id', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sharer_redirect_link', to=orm['wordout.Full_Link'])),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Sharers'])

        # Deleting model 'Action'
        db.delete_table('wordout_action')

        # Deleting model 'Sharer'
        db.delete_table('wordout_sharer')

        # Deleting model 'Customergroup'
        db.delete_table('wordout_customergroup')

        # Deleting model 'Click'
        db.delete_table('wordout_click')

        # Changing field 'Customer.customergroup'
        db.alter_column('wordout_customer', 'customergroup_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Customergroups']))


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
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Action_Type']"}),
            'click': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Click']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'wordout.action_type': {
            'Meta': {'object_name': 'Action_Type'},
            'action_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Customer']"}),
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
            'api_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9'}),
            'client_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9'}),
            'customergroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Customergroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'message_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'wordout.customergroup': {
            'Meta': {'object_name': 'Customergroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_users': ('django.db.models.fields.IntegerField', [], {'max_length': '10'})
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
        'wordout.sharer': {
            'Meta': {'object_name': 'Sharer'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '8', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wordout.Customer']"}),
            'customer_sharer_id': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
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
