# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table(u'pages_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('item', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'pages', ['File'])

        # Adding model 'Page'
        db.create_table(u'pages_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page'], null=True, blank=True)),
            ('content', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False)),
            ('include_in_menu', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'pages', ['Page'])

        # Adding M2M table for field files on 'Page'
        m2m_table_name = db.shorten_name(u'pages_page_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('page', models.ForeignKey(orm[u'pages.page'], null=False)),
            ('file', models.ForeignKey(orm[u'pages.file'], null=False))
        ))
        db.create_unique(m2m_table_name, ['page_id', 'file_id'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table(u'pages_file')

        # Deleting model 'Page'
        db.delete_table(u'pages_page')

        # Removing M2M table for field files on 'Page'
        db.delete_table(db.shorten_name(u'pages_page_files'))


    models = {
        u'pages.file': {
            'Meta': {'object_name': 'File'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'pages.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('wafer.snippets.markdown_field.MarkdownTextField', [], {'allow_html': 'False'}),
            'content_html': ('django.db.models.fields.TextField', [], {}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'pages'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['pages.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pages.Page']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pages']