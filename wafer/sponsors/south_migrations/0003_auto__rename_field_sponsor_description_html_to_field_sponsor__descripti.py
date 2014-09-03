# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename field 'Sponsor.description_html'
        db.rename_column(u'sponsors_sponsor', 'description_html',
                         '_description_rendered')

        # Changing field 'Sponsor.description'
        db.alter_column(u'sponsors_sponsor', 'description', self.gf('markitup.fields.MarkupField')(no_rendered_field=True))
        # Rename field 'SponsorshipPackage.description_html'
        db.rename_column(u'sponsors_sponsorshippackage', 'description_html',
                         '_description_rendered')


        # Changing field 'SponsorshipPackage.description'
        db.alter_column(u'sponsors_sponsorshippackage', 'description', self.gf('markitup.fields.MarkupField')(no_rendered_field=True))

    def backwards(self, orm):
        # Rename field 'Sponsor._description_rendered'
        db.rename_column(u'sponsors_sponsor', '_description_rendered',
                         'description_html')


        # Changing field 'Sponsor.description'
        db.alter_column(u'sponsors_sponsor', 'description', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False))
        # Rename field 'SponsorshipPackage._description_rendered'
        db.rename_column(u'sponsors_sponsorshippackage', '_description_rendered',
                         'description_html')


        # Changing field 'SponsorshipPackage.description'
        db.alter_column(u'sponsors_sponsorshippackage', 'description', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False))

    models = {
        u'sponsors.file': {
            'Meta': {'object_name': 'File'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'sponsors.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            '_description_rendered': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('markitup.fields.MarkupField', [], {'no_rendered_field': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sponsors'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['sponsors.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sponsors'", 'symmetrical': 'False', 'to': u"orm['sponsors.SponsorshipPackage']"})
        },
        u'sponsors.sponsorshippackage': {
            'Meta': {'ordering': "['order', '-price', 'name']", 'object_name': 'SponsorshipPackage'},
            '_description_rendered': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'$'", 'max_length': '16'}),
            'description': ('markitup.fields.MarkupField', [], {'no_rendered_field': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'packages'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['sponsors.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number_available': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'short_description': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['sponsors']
