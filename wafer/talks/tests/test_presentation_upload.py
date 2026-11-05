"""Tests for talk presentation uploads and downloads."""

import io
import os
import tempfile
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from wafer.tests.utils import create_user
from wafer.talks.models import ACCEPTED, REJECTED
from wafer.talks.tests.fixtures import create_talk


class TalkPresentationUploadTests(TestCase):
    def setUp(self):
        self.media_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_directory.cleanup)

        media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

        self.speaker = create_user('presentation_speaker')
        self.talk = create_talk(
            'Presentation upload test', ACCEPTED, user=self.speaker)

        self.upload_url = reverse(
            'wafer_talk_presentation_upload', kwargs={'pk': self.talk.pk})
        self.download_url = reverse(
            'wafer_talk_presentation_download', kwargs={'pk': self.talk.pk})

    @staticmethod
    def pdf_file(name='slides.pdf'):
        return SimpleUploadedFile(
            name, b'%PDF-1.4\nTest presentation\n',
            content_type='application/pdf')

    @staticmethod
    def zip_file(name='slides.zip'):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('index.html', '<h1>Presentation</h1>')
        return SimpleUploadedFile(
            name, buffer.getvalue(), content_type='application/zip')

    def test_speaker_can_upload_pdf(self):
        self.client.force_login(self.speaker)

        response = self.client.post(
            self.upload_url, {'presentation': self.pdf_file()})

        self.assertEqual(response.status_code, 302)
        self.talk.refresh_from_db()
        self.assertTrue(self.talk.presentation.name.endswith('.pdf'))
        self.assertTrue(os.path.exists(self.talk.presentation.path))

    def test_speaker_can_upload_zip(self):
        self.client.force_login(self.speaker)

        response = self.client.post(
            self.upload_url, {'presentation': self.zip_file()})

        self.assertEqual(response.status_code, 302)
        self.talk.refresh_from_db()
        self.assertTrue(self.talk.presentation.name.endswith('.zip'))
        self.assertTrue(os.path.exists(self.talk.presentation.path))

    def test_rejects_unsupported_file_extension(self):
        self.client.force_login(self.speaker)
        file = SimpleUploadedFile('slides.txt', b'not a presentation')

        response = self.client.post(
            self.upload_url, {'presentation': file})

        self.assertEqual(response.status_code, 200)
        self.talk.refresh_from_db()
        self.assertFalse(self.talk.presentation)

    def test_rejects_invalid_pdf_content(self):
        self.client.force_login(self.speaker)
        file = SimpleUploadedFile('slides.pdf', b'This is not a PDF')

        response = self.client.post(
            self.upload_url, {'presentation': file})

        self.assertEqual(response.status_code, 200)
        self.talk.refresh_from_db()
        self.assertFalse(self.talk.presentation)

    def test_rejects_invalid_zip_content(self):
        self.client.force_login(self.speaker)
        file = SimpleUploadedFile('slides.zip', b'This is not a ZIP archive')

        response = self.client.post(
            self.upload_url, {'presentation': file})

        self.assertEqual(response.status_code, 200)
        self.talk.refresh_from_db()
        self.assertFalse(self.talk.presentation)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.upload_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_non_speaker_cannot_upload(self):
        other_user = create_user('presentation_other_user')
        self.client.force_login(other_user)

        response = self.client.get(self.upload_url)

        self.assertEqual(response.status_code, 403)

    def test_administrator_can_upload(self):
        administrator = create_user('presentation_admin', superuser=True)
        self.client.force_login(administrator)

        response = self.client.post(
            self.upload_url, {'presentation': self.pdf_file()})

        self.assertEqual(response.status_code, 302)
        self.talk.refresh_from_db()
        self.assertTrue(self.talk.presentation)

    def test_new_upload_replaces_old_file(self):
        self.talk.presentation.save(
            'old-slides.pdf', self.pdf_file(), save=True)
        old_file_path = self.talk.presentation.path
        self.client.force_login(self.speaker)

        response = self.client.post(
            self.upload_url, {'presentation': self.zip_file()})

        self.assertEqual(response.status_code, 302)
        self.talk.refresh_from_db()
        self.assertTrue(self.talk.presentation.name.endswith('.zip'))
        self.assertFalse(os.path.exists(old_file_path))
        self.assertTrue(os.path.exists(self.talk.presentation.path))

    def test_talk_viewer_can_download_presentation(self):
        self.talk.presentation.save('slides.pdf', self.pdf_file(), save=True)

        response = self.client.get(self.download_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        response.close()

    def test_non_viewer_cannot_download_presentation(self):
        private_talk = create_talk(
            'Private presentation test', REJECTED, username='private_speaker')
        private_talk.presentation.save(
            'private-slides.pdf', self.pdf_file(), save=True)
        other_user = create_user('presentation_non_viewer')
        self.client.force_login(other_user)
        url = reverse(
            'wafer_talk_presentation_download',
            kwargs={'pk': private_talk.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_missing_presentation_returns_404(self):
        response = self.client.get(self.download_url)

        self.assertEqual(response.status_code, 404)
