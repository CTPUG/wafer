# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ConferenceOptionGroup'
        db.create_table(u'conf_registration_conferenceoptiongroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'conf_registration', ['ConferenceOptionGroup'])

        # Adding model 'ConferenceOption'
        db.create_table(u'conf_registration_conferenceoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal(u'conf_registration', ['ConferenceOption'])

        # Adding M2M table for field groups on 'ConferenceOption'
        m2m_table_name = db.shorten_name(u'conf_registration_conferenceoption_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('conferenceoption', models.ForeignKey(orm[u'conf_registration.conferenceoption'], null=False)),
            ('conferenceoptiongroup', models.ForeignKey(orm[u'conf_registration.conferenceoptiongroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['conferenceoption_id', 'conferenceoptiongroup_id'])

        # Adding M2M table for field requirements on 'ConferenceOption'
        m2m_table_name = db.shorten_name(u'conf_registration_conferenceoption_requirements')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('conferenceoption', models.ForeignKey(orm[u'conf_registration.conferenceoption'], null=False)),
            ('conferenceoptiongroup', models.ForeignKey(orm[u'conf_registration.conferenceoptiongroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['conferenceoption_id', 'conferenceoptiongroup_id'])

        # Adding model 'RegisteredAttendee'
        db.create_table(u'conf_registration_registeredattendee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('registered_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created', to=orm['auth.User'])),
            ('waitlist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('waitlist_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'conf_registration', ['RegisteredAttendee'])

        # Adding unique constraint on 'RegisteredAttendee', fields ['name', 'email']
        db.create_unique(u'conf_registration_registeredattendee', ['name', 'email'])

        # Adding M2M table for field items on 'RegisteredAttendee'
        m2m_table_name = db.shorten_name(u'conf_registration_registeredattendee_items')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registeredattendee', models.ForeignKey(orm[u'conf_registration.registeredattendee'], null=False)),
            ('conferenceoption', models.ForeignKey(orm[u'conf_registration.conferenceoption'], null=False))
        ))
        db.create_unique(m2m_table_name, ['registeredattendee_id', 'conferenceoption_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'RegisteredAttendee', fields ['name', 'email']
        db.delete_unique(u'conf_registration_registeredattendee', ['name', 'email'])

        # Deleting model 'ConferenceOptionGroup'
        db.delete_table(u'conf_registration_conferenceoptiongroup')

        # Deleting model 'ConferenceOption'
        db.delete_table(u'conf_registration_conferenceoption')

        # Removing M2M table for field groups on 'ConferenceOption'
        db.delete_table(db.shorten_name(u'conf_registration_conferenceoption_groups'))

        # Removing M2M table for field requirements on 'ConferenceOption'
        db.delete_table(db.shorten_name(u'conf_registration_conferenceoption_requirements'))

        # Deleting model 'RegisteredAttendee'
        db.delete_table(u'conf_registration_registeredattendee')

        # Removing M2M table for field items on 'RegisteredAttendee'
        db.delete_table(db.shorten_name(u'conf_registration_registeredattendee_items'))


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
        u'conf_registration.conferenceoption': {
            'Meta': {'object_name': 'ConferenceOption'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'members'", 'symmetrical': 'False', 'to': u"orm['conf_registration.ConferenceOptionGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'enables'", 'blank': 'True', 'to': u"orm['conf_registration.ConferenceOptionGroup']"})
        },
        u'conf_registration.conferenceoptiongroup': {
            'Meta': {'object_name': 'ConferenceOptionGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'conf_registration.registeredattendee': {
            'Meta': {'unique_together': "(('name', 'email'),)", 'object_name': 'RegisteredAttendee'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'attendees'", 'blank': 'True', 'to': u"orm['conf_registration.ConferenceOption']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'registered_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created'", 'to': u"orm['auth.User']"}),
            'waitlist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'waitlist_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['conf_registration']