# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("conf_registration", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'InvoiceTemplate'
        db.create_table(u'invoices_invoicetemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Unnamed', max_length=255)),
            ('company_name', self.gf('django.db.models.fields.TextField')(default='Wafercon 20XX')),
            ('company_info', self.gf('django.db.models.fields.TextField')(default='Wafercon Foundation\nwafercon.example.com\nteam@waferconf.example.com')),
            ('tax_name', self.gf('django.db.models.fields.TextField')(default='VAT')),
            ('tax_percentage', self.gf('django.db.models.fields.DecimalField')(default=None, null=True, max_digits=12, decimal_places=2, blank=True)),
            ('currency_symbol', self.gf('django.db.models.fields.CharField')(default='R', max_length=16)),
            ('payment_details', self.gf('django.db.models.fields.TextField')(default='Pay by EFT to:\nAccount number: XXX\nBranch code: YYY\nAccount name: Wafercon\nBank: ZZZ\nReference: %(reference)s')),
            ('additional_notes', self.gf('django.db.models.fields.TextField')(default='Created with Billable.me')),
            ('reference_template', self.gf('django.db.models.fields.TextField')(default='INVOICE:%(invoice_no)s')),
        ))
        db.send_create_signal(u'invoices', ['InvoiceTemplate'])

        # Adding model 'Invoice'
        db.create_table(u'invoices_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='provisional', max_length=32)),
            ('recipient_info', self.gf('django.db.models.fields.TextField')()),
            ('pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('company_name', self.gf('django.db.models.fields.TextField')()),
            ('company_info', self.gf('django.db.models.fields.TextField')()),
            ('tax_name', self.gf('django.db.models.fields.TextField')()),
            ('tax_percentage', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2)),
            ('currency_symbol', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('payment_details', self.gf('django.db.models.fields.TextField')()),
            ('additional_notes', self.gf('django.db.models.fields.TextField')()),
            ('reference_template', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'invoices', ['Invoice'])

        # Adding M2M table for field attendees on 'Invoice'
        m2m_table_name = db.shorten_name(u'invoices_invoice_attendees')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('invoice', models.ForeignKey(orm[u'invoices.invoice'], null=False)),
            ('registeredattendee', models.ForeignKey(orm[u'conf_registration.registeredattendee'], null=False))
        ))
        db.create_unique(m2m_table_name, ['invoice_id', 'registeredattendee_id'])

        # Adding model 'InvoiceItem'
        db.create_table(u'invoices_invoiceitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['invoices.Invoice'])),
        ))
        db.send_create_signal(u'invoices', ['InvoiceItem'])


    def backwards(self, orm):
        # Deleting model 'InvoiceTemplate'
        db.delete_table(u'invoices_invoicetemplate')

        # Deleting model 'Invoice'
        db.delete_table(u'invoices_invoice')

        # Removing M2M table for field attendees on 'Invoice'
        db.delete_table(db.shorten_name(u'invoices_invoice_attendees'))

        # Deleting model 'InvoiceItem'
        db.delete_table(u'invoices_invoiceitem')


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
        },
        u'invoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'additional_notes': ('django.db.models.fields.TextField', [], {}),
            'attendees': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['conf_registration.RegisteredAttendee']", 'symmetrical': 'False'}),
            'company_info': ('django.db.models.fields.TextField', [], {}),
            'company_name': ('django.db.models.fields.TextField', [], {}),
            'currency_symbol': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_details': ('django.db.models.fields.TextField', [], {}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'recipient_info': ('django.db.models.fields.TextField', [], {}),
            'reference_template': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'provisional'", 'max_length': '32'}),
            'tax_name': ('django.db.models.fields.TextField', [], {}),
            'tax_percentage': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'invoices.invoiceitem': {
            'Meta': {'object_name': 'InvoiceItem'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        u'invoices.invoicetemplate': {
            'Meta': {'object_name': 'InvoiceTemplate'},
            'additional_notes': ('django.db.models.fields.TextField', [], {'default': "'Created with Billable.me'"}),
            'company_info': ('django.db.models.fields.TextField', [], {'default': "'Wafercon Foundation\\nwafercon.example.com\\nteam@waferconf.example.com'"}),
            'company_name': ('django.db.models.fields.TextField', [], {'default': "'Wafercon 20XX'"}),
            'currency_symbol': ('django.db.models.fields.CharField', [], {'default': "'R'", 'max_length': '16'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed'", 'max_length': '255'}),
            'payment_details': ('django.db.models.fields.TextField', [], {'default': "'Pay by EFT to:\\nAccount number: XXX\\nBranch code: YYY\\nAccount name: Wafercon\\nBank: ZZZ\\nReference: %(reference)s'"}),
            'reference_template': ('django.db.models.fields.TextField', [], {'default': "'INVOICE:%(invoice_no)s'"}),
            'tax_name': ('django.db.models.fields.TextField', [], {'default': "'VAT'"}),
            'tax_percentage': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['invoices']
