# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table(u'djiki_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'djiki', ['Page'])

        # Adding model 'PageRevision'
        db.create_table(u'djiki_pagerevision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, blank=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['djiki.Page'])),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'djiki', ['PageRevision'])

        # Adding model 'Image'
        db.create_table(u'djiki_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal(u'djiki', ['Image'])

        # Adding model 'ImageRevision'
        db.create_table(u'djiki_imagerevision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[AUTH_USER_MODEL], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['djiki.Image'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'djiki', ['ImageRevision'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table(u'djiki_page')

        # Deleting model 'PageRevision'
        db.delete_table(u'djiki_pagerevision')

        # Deleting model 'Image'
        db.delete_table(u'djiki_image')

        # Deleting model 'ImageRevision'
        db.delete_table(u'djiki_imagerevision')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'djiki.image': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Image'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'djiki.imagerevision': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'ImageRevision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['" + AUTH_USER_MODEL + "']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': u"orm['djiki.Image']"})
        },
        u'djiki.page': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Page'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'djiki.pagerevision': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'PageRevision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['" + AUTH_USER_MODEL +"']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': u"orm['djiki.Page']"})
        }
    }
    models[AUTH_USER_MODEL] = {
        u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
    }

    complete_apps = ['djiki']
