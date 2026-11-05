"""Tests for talk attachment uploads and downloads."""

import os
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from wafer.tests.utils import create_user
from wafer.talks.models import ACCEPTED, REJECTED, TalkFile
from wafer.talks.tests.fixtures import create_talk


class TalkAttachmentTests(TestCase):

    def setUp(self):
        self.private_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.private_directory.cleanup)

        self.storage = TalkFile._meta.get_field('item').storage
        self.original_storage_location = self.storage.location
        self.storage.location = self.private_directory.name
        self.addCleanup(
            lambda: setattr(
                self.storage, 'location', self.original_storage_location
            )
        )

        self.speaker = create_user('attachment_speaker')
        self.talk = create_talk(
            'Attachment upload test', ACCEPTED, user=self.speaker
        )

        self.upload_url = reverse(
            'wafer_talk_file_upload', kwargs={'pk': self.talk.pk}
        )

    @staticmethod
    def uploaded_file(name='slides.pdf', content=b'Test file content'):
        return SimpleUploadedFile(
            name, content, content_type='application/octet-stream'
        )

    def download_url(self, attachment):
        return reverse(
            'wafer_talk_file_download',
            kwargs={'file_pk': attachment.pk},
        )

    def create_attachment(self, public=False, talk=None):
        attachment = TalkFile(
            talk=talk or self.talk,
            name='test-document.txt',
            description='Test attachment',
            public=public,
        )
        attachment.item.save(
            'test-document.txt',
            self.uploaded_file('test-document.txt'),
            save=True,
        )
        return attachment

    def test_speaker_can_upload_multiple_files(self):
        self.client.force_login(self.speaker)

        response = self.client.post(
            self.upload_url,
            {
                'files': [
                    self.uploaded_file('slides.pdf'),
                    self.uploaded_file('example.py', b'print("hello")'),
                ],
            },
        )

        self.assertEqual(response.status_code, 302)

        attachments = list(self.talk.attachments.order_by('name'))
        self.assertEqual(len(attachments), 2)
        self.assertEqual(
            {item.name for item in attachments},
            {'slides.pdf', 'example.py'},
        )

        for attachment in attachments:
            self.assertFalse(attachment.public)
            self.assertTrue(attachment.item.storage.exists(
                attachment.item.name
            ))

    def test_speaker_can_upload_non_pdf_file(self):
        self.client.force_login(self.speaker)

        response = self.client.post(
            self.upload_url,
            {'files': self.uploaded_file('notes.txt', b'Example notes')},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.talk.attachments.filter(name='notes.txt').exists()
        )

    def test_new_uploads_are_private_by_default(self):
        self.client.force_login(self.speaker)

        self.client.post(
            self.upload_url,
            {'files': self.uploaded_file('private.pdf')},
        )

        attachment = self.talk.attachments.get()
        self.assertFalse(attachment.public)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.upload_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_non_speaker_cannot_upload(self):
        other_user = create_user('attachment_other_user')
        self.client.force_login(other_user)

        response = self.client.get(self.upload_url)

        self.assertEqual(response.status_code, 403)

    def test_administrator_can_upload(self):
        administrator = create_user(
            'attachment_admin', superuser=True
        )
        self.client.force_login(administrator)

        response = self.client.post(
            self.upload_url,
            {'files': self.uploaded_file('admin-file.pdf')},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.talk.attachments.filter(name='admin-file.pdf').exists()
        )

    def test_author_can_download_private_attachment(self):
        attachment = self.create_attachment(public=False)
        self.client.force_login(self.speaker)

        response = self.client.get(self.download_url(attachment))

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        response.close()

    def test_anonymous_user_cannot_download_private_attachment(self):
        attachment = self.create_attachment(public=False)

        response = self.client.get(self.download_url(attachment))

        self.assertEqual(response.status_code, 403)

    def test_unrelated_user_cannot_download_private_attachment(self):
        attachment = self.create_attachment(public=False)
        other_user = create_user('attachment_unrelated_user')
        self.client.force_login(other_user)

        response = self.client.get(self.download_url(attachment))

        self.assertEqual(response.status_code, 403)

    def test_public_attachment_can_be_downloaded_by_viewer(self):
        attachment = self.create_attachment(public=True)

        response = self.client.get(self.download_url(attachment))

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        response.close()

    def test_public_attachment_is_not_available_for_private_talk(self):
        private_talk = create_talk(
            'Rejected attachment test',
            REJECTED,
            username='attachment_private_speaker',
        )
        attachment = self.create_attachment(
            public=True,
            talk=private_talk,
        )

        other_user = create_user('attachment_private_viewer')
        self.client.force_login(other_user)

        response = self.client.get(self.download_url(attachment))

        self.assertEqual(response.status_code, 403)

    def test_administrator_can_download_private_attachment(self):
        attachment = self.create_attachment(public=False)
        administrator = create_user(
            'attachment_download_admin', superuser=True
        )
        self.client.force_login(administrator)

        response = self.client.get(self.download_url(attachment))

        self.assertEqual(response.status_code, 200)
        response.close()

    def test_missing_attachment_returns_404(self):
        response = self.client.get(
            reverse(
                'wafer_talk_file_download',
                kwargs={'file_pk': 999999},
            )
        )

        self.assertEqual(response.status_code, 404)
