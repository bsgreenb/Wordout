# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Customer'
        db.create_table('wordout_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('wordout', ['Customer'])

        # Adding model 'HOST'
        db.create_table('wordout_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host_name', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['HOST'])

        # Adding model 'Path'
        db.create_table('wordout_path', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path_loc', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Path'])

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
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Path'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Full_Link'])

        # Adding model 'Identifiers'
        db.create_table('wordout_identifiers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('identifier_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=8, db_index=True)),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='identifier_redirect_link', to=orm['wordout.Full_Link'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Identifiers'])

        # Adding model 'Request'
        db.create_table('wordout_request', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('referral_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Identifiers'])),
            ('redirect_link', self.gf('django.db.models.fields.related.ForeignKey')(related_name='request_redirect_link', to=orm['wordout.Full_Link'])),
            ('referrer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.Full_Link'], null=True, blank=True)),
            ('IP', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.IP'], null=True, blank=True)),
            ('Agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wordout.User_Agent'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('wordout', ['Request'])


    def backwards(self, orm):
        
        # Deleting model 'Customer'
        db.delete_table('wordout_customer')

        # Deleting model 'HOST'
        db.delete_table('wordout_host')

        # Deleting model 'Path'
        db.delete_table('wordout_path')

        # Deleting model 'IP'
        db.delete_table('wordout_ip')

        # Deleting model 'User_Agent'
        db.delete_table('wordout_user_agent')

        # Deleting model 'Full_Link'
        db.delete_table('wordout_full_link')

        # Deleting model 'Identifiers'
        db.delete_table('wordout_identifiers')

        # Deleting model 'Request'
        db.delete_table('wordout_request')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'identifier_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'redirect_link': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifier_redirect_link'", 'to': "orm['wordout.Full_Link']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
