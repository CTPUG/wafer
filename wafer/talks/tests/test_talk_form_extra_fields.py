"""Tests for the key-value backed extra fields on the talk form"""

from unittest import mock

from django.contrib.auth.models import Group
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from wafer.talks.forms import TalkForm
from wafer.talks.models import (
    ACCEPTED, SUBMITTED, TALK_EXTRA_FIELDS_GROUP, Talk)
from wafer.talks.tests.fixtures import create_talk
from wafer.tests.utils import create_user, mock_avatar_url


EXTRA_FIELDS = {
    'presenters': {
        'label': 'Multiple presenters?', 'type': 'boolean',
        'visibility': 'public',
    },
    'shows_video': {
        'label': 'Will you be showing video?', 'type': 'choice',
        'required': True,
        'choices': (('no', 'No'), ('yes', 'Yes, with audio')),
        'visibility': 'reviewers',
    },
    'guidelines': {
        'label': 'I accept the guidelines', 'type': 'boolean',
        'required': True, 'visibility': 'organisers',
    },
}


def set_extra(talk, **values):
    group, _ = Group.objects.get_or_create(name=TALK_EXTRA_FIELDS_GROUP)
    for key, value in values.items():
        talk.kv.create(group=group, key=key, value=value)


@override_settings(WAFER_TALK_EXTRA_FIELDS=EXTRA_FIELDS,
                   WAFER_VIDEO=False, WAFER_VIDEO_REVIEWER=False)
class TalkFormExtraFieldsTests(TestCase):
    def setUp(self):
        self.user = create_user('author')
        self.client = Client()
        self.client.login(username='author', password='author_password')

    def submit_data(self, **kwargs):
        data = {
            'title': 'My talk', 'abstract': 'Abstract',
            'authors': [self.user.pk], 'notes': '',
            'shows_video': 'yes', 'guidelines': 'on',
        }
        data.update(kwargs)
        return data

    def test_submit_stores_kv(self):
        response = self.client.post(
            reverse('wafer_talk_submit'), self.submit_data(presenters='on'))
        self.assertEqual(response.status_code, 302)
        talk = Talk.objects.get()
        values = {kv.key: kv.value for kv in talk.kv.all()}
        self.assertEqual(values, {
            'presenters': True, 'shows_video': 'yes', 'guidelines': True})
        self.assertTrue(all(kv.group.name == TALK_EXTRA_FIELDS_GROUP
                            for kv in talk.kv.all()))

    def test_required_extra_field(self):
        data = self.submit_data()
        del data['guidelines']
        response = self.client.post(reverse('wafer_talk_submit'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('guidelines', response.context['form'].errors)
        self.assertFalse(Talk.objects.exists())

    def test_edit_updates_kv(self):
        self.client.post(reverse('wafer_talk_submit'), self.submit_data())
        talk = Talk.objects.get()
        response = self.client.get(
            reverse('wafer_talk_edit', kwargs={'pk': talk.pk}))
        self.assertEqual(response.context['form']['shows_video'].initial, 'yes')
        response = self.client.post(
            reverse('wafer_talk_edit', kwargs={'pk': talk.pk}),
            self.submit_data(shows_video='no'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(talk.kv.count(), 3)
        self.assertEqual(talk.kv.get(key='shows_video').value, 'no')


@override_settings(WAFER_TALK_EXTRA_FIELDS=EXTRA_FIELDS)
@mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
class TalkExtraFieldsDisplayTests(TestCase):
    def setUp(self):
        self.talk = create_talk('Talk A', ACCEPTED, 'author_a')
        set_extra(self.talk, presenters=True, shows_video='yes',
                  guidelines=True)
        self.client = Client()

    def labels_for(self, user):
        return [label for label, _value in self.talk.get_extra_fields(user)]

    def visible_on_page(self):
        response = self.client.get(
            self.talk.get_absolute_url())
        return [label for label, _value in response.context['extra_fields']]

    def test_anonymous(self):
        self.assertEqual(self.visible_on_page(), ['Multiple presenters?'])

    def test_reviewer(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.client.login(username='reviewer', password='reviewer_password')
        self.assertEqual(self.visible_on_page(), [
            'Multiple presenters?', 'Will you be showing video?'])

    def test_organiser(self):
        create_user('mentor', perms=['view_all_talks', 'change_talk'])
        self.client.login(username='mentor', password='mentor_password')
        self.assertEqual(self.visible_on_page(), [
            'Multiple presenters?', 'Will you be showing video?',
            'I accept the guidelines'])

    def test_author_sees_all(self):
        self.client.login(username='author_a', password='author_a_password')
        self.assertEqual(len(self.visible_on_page()), 3)

    def test_display_values(self):
        self.assertEqual(self.talk.get_extra_fields(), [
            ('Multiple presenters?', 'Yes'),
            ('Will you be showing video?', 'Yes, with audio'),
            ('I accept the guidelines', 'Yes'),
        ])

    def test_rendered(self):
        response = self.client.get(
            self.talk.get_absolute_url())
        self.assertContains(response, 'id="extra_fields"')
        self.assertContains(response, 'Multiple presenters?')
        self.assertNotContains(response, 'I accept the guidelines')

    def test_admin_shows_all(self):
        create_user('super', superuser=True)
        self.client.login(username='super', password='super_password')
        response = self.client.get(
            reverse('admin:talks_talk_change', args=(self.talk.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, '<strong>I accept the guidelines</strong>: Yes',
            html=False)


@mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
class TalkNoExtraFieldsTests(TestCase):
    def test_default_form_unchanged(self):
        user = create_user('author')
        form = TalkForm(user=user, instance=None)
        for key in EXTRA_FIELDS:
            self.assertNotIn(key, form.fields)
        talk = create_talk('Talk S', SUBMITTED, user=user)
        self.assertEqual(talk.get_extra_fields(user), [])

    def test_page_without_extra_fields(self):
        talk = create_talk('Talk A', ACCEPTED, 'author_a')
        response = Client().get(talk.get_absolute_url())
        self.assertNotContains(response, 'id="extra_fields"')
