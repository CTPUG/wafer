# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename field 'Page.content_html'
        db.rename_column(u'pages_page', 'content_html', '_content_rendered')


        # Changing field 'Page.content'
        db.alter_column(u'pages_page', 'content', self.gf('markitup.fields.MarkupField')(no_rendered_field=True))

    def backwards(self, orm):
        # Rename field 'Page._content_rendered'
        db.rename_column(u'pages_page', '_content_rendered', 'content_html')


        # Changing field 'Page.content'
        db.alter_column(u'pages_page', 'content', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False))

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
            '_content_rendered': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content': ('markitup.fields.MarkupField', [], {'no_rendered_field': 'True'}),
            'exclude_from_static': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'pages'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['pages.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pages.Page']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pages']
