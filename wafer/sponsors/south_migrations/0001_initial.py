# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'File'
        db.create_table(u'sponsors_file', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('item', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'sponsors', ['File'])

        # Adding model 'SponsorshipPackage'
        db.create_table(u'sponsors_sponsorshippackage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('number_available', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('short_description', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False)),
            ('description_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'sponsors', ['SponsorshipPackage'])

        # Adding M2M table for field files on 'SponsorshipPackage'
        m2m_table_name = db.shorten_name(u'sponsors_sponsorshippackage_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sponsorshippackage', models.ForeignKey(orm[u'sponsors.sponsorshippackage'], null=False)),
            ('file', models.ForeignKey(orm[u'sponsors.file'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sponsorshippackage_id', 'file_id'])

        # Adding model 'Sponsor'
        db.create_table(u'sponsors_sponsor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False)),
            ('description_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'sponsors', ['Sponsor'])

        # Adding M2M table for field packages on 'Sponsor'
        m2m_table_name = db.shorten_name(u'sponsors_sponsor_packages')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sponsor', models.ForeignKey(orm[u'sponsors.sponsor'], null=False)),
            ('sponsorshippackage', models.ForeignKey(orm[u'sponsors.sponsorshippackage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sponsor_id', 'sponsorshippackage_id'])

        # Adding M2M table for field files on 'Sponsor'
        m2m_table_name = db.shorten_name(u'sponsors_sponsor_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sponsor', models.ForeignKey(orm[u'sponsors.sponsor'], null=False)),
            ('file', models.ForeignKey(orm[u'sponsors.file'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sponsor_id', 'file_id'])


    def backwards(self, orm):
        # Deleting model 'File'
        db.delete_table(u'sponsors_file')

        # Deleting model 'SponsorshipPackage'
        db.delete_table(u'sponsors_sponsorshippackage')

        # Removing M2M table for field files on 'SponsorshipPackage'
        db.delete_table(db.shorten_name(u'sponsors_sponsorshippackage_files'))

        # Deleting model 'Sponsor'
        db.delete_table(u'sponsors_sponsor')

        # Removing M2M table for field packages on 'Sponsor'
        db.delete_table(db.shorten_name(u'sponsors_sponsor_packages'))

        # Removing M2M table for field files on 'Sponsor'
        db.delete_table(db.shorten_name(u'sponsors_sponsor_files'))


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
            'Meta': {'object_name': 'SponsorshipPackage'},
            'description': ('wafer.snippets.markdown_field.MarkdownTextField', [], {'allow_html': 'False'}),
            'description_html': ('django.db.models.fields.TextField', [], {}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'packages'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['sponsors.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'number_available': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'short_description': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['sponsors']