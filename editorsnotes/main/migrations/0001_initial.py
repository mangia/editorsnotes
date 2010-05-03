# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Note'
        db.create_table('main_note', (
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_note_set', to=orm['auth.User'])),
            ('content', self.gf('main.fields.XHTMLField')()),
            ('last_updater', self.gf('django.db.models.fields.related.ForeignKey')(related_name='last_to_update_note_set', to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('main', ['Note'])

        # Adding model 'Reference'
        db.create_table('main_reference', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('citation', self.gf('main.fields.XHTMLField')()),
            ('note', self.gf('django.db.models.fields.related.ForeignKey')(related_name='references', to=orm['main.Note'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_reference_set', to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('main', ['Reference'])

        # Adding model 'Term'
        db.create_table('main_term', (
            ('preferred_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length='80')),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length='80')),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_term_set', to=orm['auth.User'])),
        ))
        db.send_create_signal('main', ['Term'])

        # Adding model 'Alias'
        db.create_table('main_alias', (
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['main.Term'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length='80')),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_alias_set', to=orm['auth.User'])),
        ))
        db.send_create_signal('main', ['Alias'])

        # Adding unique constraint on 'Alias', fields ['term', 'name']
        db.create_unique('main_alias', ['term_id', 'name'])

        # Adding model 'TermAssignment'
        db.create_table('main_termassignment', (
            ('note', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notes', to=orm['main.Note'])),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Term'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_termassignment_set', to=orm['auth.User'])),
        ))
        db.send_create_signal('main', ['TermAssignment'])

        # Adding unique constraint on 'TermAssignment', fields ['term', 'note']
        db.create_unique('main_termassignment', ['term_id', 'note_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Note'
        db.delete_table('main_note')

        # Deleting model 'Reference'
        db.delete_table('main_reference')

        # Deleting model 'Term'
        db.delete_table('main_term')

        # Deleting model 'Alias'
        db.delete_table('main_alias')

        # Removing unique constraint on 'Alias', fields ['term', 'name']
        db.delete_unique('main_alias', ['term_id', 'name'])

        # Deleting model 'TermAssignment'
        db.delete_table('main_termassignment')

        # Removing unique constraint on 'TermAssignment', fields ['term', 'note']
        db.delete_unique('main_termassignment', ['term_id', 'note_id'])
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.alias': {
            'Meta': {'unique_together': "(('term', 'name'),)", 'object_name': 'Alias'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_alias_set'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'80'"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': "orm['main.Term']"})
        },
        'main.note': {
            'Meta': {'object_name': 'Note'},
            'content': ('main.fields.XHTMLField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_note_set'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'last_updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_to_update_note_set'", 'to': "orm['auth.User']"}),
            'terms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Term']", 'through': "orm['main.TermAssignment']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'})
        },
        'main.reference': {
            'Meta': {'object_name': 'Reference'},
            'citation': ('main.fields.XHTMLField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_reference_set'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'references'", 'to': "orm['main.Note']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'main.term': {
            'Meta': {'object_name': 'Term'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_term_set'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preferred_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'80'"}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': "'80'"})
        },
        'main.termassignment': {
            'Meta': {'unique_together': "(('term', 'note'),)", 'object_name': 'TermAssignment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_termassignment_set'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': "orm['main.Note']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Term']"})
        }
    }
    
    complete_apps = ['main']