# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SponsorshipPackage.order'
        db.add_column(u'sponsors_sponsorshippackage', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'SponsorshipPackage.currency'
        db.add_column(u'sponsors_sponsorshippackage', 'currency',
                      self.gf('django.db.models.fields.CharField')(default='$', max_length=16),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SponsorshipPackage.order'
        db.delete_column(u'sponsors_sponsorshippackage', 'order')

        # Deleting field 'SponsorshipPackage.currency'
        db.delete_column(u'sponsors_sponsorshippackage', 'currency')


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
            'description': ('wafer.snippets.markdown_field.MarkdownTextField', [], {'allow_html': 'False'}),
            'description_html': ('django.db.models.fields.TextField', [], {}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sponsors'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['sponsors.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sponsors'", 'symmetrical': 'False', 'to': u"orm['sponsors.SponsorshipPackage']"})
        },
        u'sponsors.sponsorshippackage': {
            'Meta': {'ordering': "['order', 'price', 'name']", 'object_name': 'SponsorshipPackage'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'$'", 'max_length': '16'}),
            'description': ('wafer.snippets.markdown_field.MarkdownTextField', [], {'allow_html': 'False'}),
            'description_html': ('django.db.models.fields.TextField', [], {}),
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