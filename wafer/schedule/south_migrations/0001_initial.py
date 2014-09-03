# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Venue'
        db.create_table(u'schedule_venue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('notes', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(allow_html=False)),
            ('notes_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'schedule', ['Venue'])

        # Adding model 'Slot'
        db.create_table(u'schedule_slot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'schedule', ['Slot'])

        # Adding model 'ScheduleItem'
        db.create_table(u'schedule_scheduleitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('venue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Venue'])),
            ('talk', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['talks.Talk'], null=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page'], null=True)),
            ('details', self.gf('wafer.snippets.markdown_field.MarkdownTextField')(blank=True, allow_html=False)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('details_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'schedule', ['ScheduleItem'])

        # Adding M2M table for field slots on 'ScheduleItem'
        m2m_table_name = db.shorten_name(u'schedule_scheduleitem_slots')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scheduleitem', models.ForeignKey(orm[u'schedule.scheduleitem'], null=False)),
            ('slot', models.ForeignKey(orm[u'schedule.slot'], null=False))
        ))
        db.create_unique(m2m_table_name, ['scheduleitem_id', 'slot_id'])


    def backwards(self, orm):
        # Deleting model 'Venue'
        db.delete_table(u'schedule_venue')

        # Deleting model 'Slot'
        db.delete_table(u'schedule_slot')

        # Deleting model 'ScheduleItem'
        db.delete_table(u'schedule_scheduleitem')

        # Removing M2M table for field slots on 'ScheduleItem'
        db.delete_table(db.shorten_name(u'schedule_scheduleitem_slots'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        },
        u'schedule.scheduleitem': {
            'Meta': {'object_name': 'ScheduleItem'},
            'details': ('wafer.snippets.markdown_field.MarkdownTextField', [], {'blank': 'True', 'allow_html': 'False'}),
            'details_html': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pages.Page']", 'null': 'True'}),
            'slots': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.Slot']", 'symmetrical': 'False'}),
            'talk': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['talks.Talk']", 'null': 'True'}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Venue']"})
        },
        u'schedule.slot': {
            'Meta': {'object_name': 'Slot'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'schedule.venue': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'Venue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'notes': ('wafer.snippets.markdown_field.MarkdownTextField', [], {'allow_html': 'False'}),
            'notes_html': ('django.db.models.fields.TextField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'talks.talk': {
            'Meta': {'object_name': 'Talk'},
            '_abstract_rendered': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'abstract': ('markitup.fields.MarkupField', [], {'no_rendered_field': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'talks'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'corresponding_author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_talks'", 'to': u"orm['auth.User']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'talk_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['schedule']