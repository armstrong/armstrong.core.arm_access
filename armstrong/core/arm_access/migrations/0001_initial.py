# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Level'
        db.create_table('arm_access_level', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('is_protected', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('arm_access', ['Level'])

        # Adding model 'AccessObject'
        db.create_table('arm_access_accessobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('arm_access', ['AccessObject'])

        # Adding model 'Assignment'
        db.create_table('arm_access_assignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assignments', to=orm['arm_access.AccessObject'])),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assignments', to=orm['arm_access.Level'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999))),
        ))
        db.send_create_signal('arm_access', ['Assignment'])

        # Adding model 'AccessMembership'
        db.create_table('arm_access_accessmembership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='access_memberships', to=orm['auth.User'])),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(related_name='access_memberships', to=orm['arm_access.Level'])),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('arm_access', ['AccessMembership'])


    def backwards(self, orm):
        
        # Deleting model 'Level'
        db.delete_table('arm_access_level')

        # Deleting model 'AccessObject'
        db.delete_table('arm_access_accessobject')

        # Deleting model 'Assignment'
        db.delete_table('arm_access_assignment')

        # Deleting model 'AccessMembership'
        db.delete_table('arm_access_accessmembership')


    models = {
        'arm_access.accessmembership': {
            'Meta': {'object_name': 'AccessMembership'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'access_memberships'", 'to': "orm['arm_access.Level']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'access_memberships'", 'to': "orm['auth.User']"})
        },
        'arm_access.accessobject': {
            'Meta': {'object_name': 'AccessObject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'arm_access.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'access_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['arm_access.AccessObject']"}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['arm_access.Level']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'arm_access.level': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Level'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_protected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
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
        }
    }

    complete_apps = ['arm_access']
