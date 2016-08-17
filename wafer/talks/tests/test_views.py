"""Tests for wafer.talk views."""

import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from wafer.talks.models import (Talk, ACCEPTED, REJECTED, PENDING,
                                CANCELLED)


def create_user(username, superuser=False, perms=()):
    if superuser:
        create = get_user_model().objects.create_superuser
    else:
        create = get_user_model().objects.create_user
    user = create(
        username, '%s@example.com' % username, '%s_password' % username)
    for codename in perms:
        perm = Permission.objects.get(codename=codename)
        user.user_permissions.add(perm)
    if perms:
        user = get_user_model().objects.get(pk=user.pk)
    return user


def create_talk(title, status, username):
    user = create_user(username)
    talk = Talk.objects.create(
        title=title, status=status, corresponding_author_id=user.id)
    talk.authors.add(user)
    talk.notes = "Some notes for talk %s" % title
    talk.private_notes = "Some private notes for talk %s" % title
    talk.save()
    return talk


def mock_avatar_url(self):
    if self.user.email is None:
        return None
    return "avatar-%s" % self.user.email


class UsersTalksTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_p = create_talk("Talk P", PENDING, "author_p")
        self.client = Client()

    def test_not_logged_in(self):
        """Test that unauthenticated users only see accepted talks."""
        response = self.client.get('/talks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['talk_list']),
                         set([self.talk_a]))

    def test_admin_user(self):
        """Test that admin users see all talks."""
        create_user('super', superuser=True)
        self.client.login(username='super', password='super_password')
        response = self.client.get('/talks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['talk_list']),
                         set([self.talk_a, self.talk_r, self.talk_p]))

    def test_user_with_view_all(self):
        """Test that users with the view_all permission see all talks."""
        create_user('reviewer', perms=['view_all_talks'])
        self.client.login(username='reviewer', password='reviewer_password')
        response = self.client.get('/talks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['talk_list']),
                         set([self.talk_a, self.talk_r, self.talk_p]))


class TalkViewTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_p = create_talk("Talk P", PENDING, "author_p")
        self.talk_c = create_talk("Talk C", CANCELLED, "author_c")
        self.client = Client()

    def check_talk_view(self, talk, status_code, auth=None):
        if auth is not None:
            self.client.login(**auth)
        response = self.client.get(
            reverse('wafer_talk', kwargs={'pk': talk.pk}))
        self.assertEqual(response.status_code, status_code)

    def test_view_accepted_not_logged_in(self):
        self.check_talk_view(self.talk_a, 200)

    def test_view_rejected_not_logged_in(self):
        self.check_talk_view(self.talk_r, 403)

    def test_view_cancelled_not_logged_in(self):
        self.check_talk_view(self.talk_c, 403)

    def test_view_pending_not_logged_in(self):
        self.check_talk_view(self.talk_p, 403)

    def test_view_accepted_author(self):
        self.check_talk_view(self.talk_a, 200, auth={
            'username': 'author_a', 'password': 'author_a_password',
        })

    def test_view_rejected_author(self):
        self.check_talk_view(self.talk_r, 200, auth={
            'username': 'author_r', 'password': 'author_r_password',
        })

    def test_view_pending_author(self):
        self.check_talk_view(self.talk_p, 200, auth={
            'username': 'author_p', 'password': 'author_p_password',
        })

    def test_view_accepted_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_a, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_rejected_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_r, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_cancelled_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_c, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_pending_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_p, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })


class TalkNoteViewTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.client = Client()

    def check_talk_view(self, talk, notes_visible, private_notes_visible,
                        auth=None):
        if auth is not None:
            self.client.login(**auth)
        response = self.client.get(
            reverse('wafer_talk', kwargs={'pk': talk.pk}))
        if notes_visible:
            self.assertTrue('Some notes for talk' in response.rendered_content)
        else:
            # If the response doesn't have a rendered_content
            # (HttpResponseForbidden, etc), this is trivially true,
            # so we don't bother to test it.
            if hasattr(response, 'rendered_content'):
                self.assertFalse('Some notes for talk' in
                                 response.rendered_content)
        if private_notes_visible:
            self.assertTrue('Some private notes for talk' in response.rendered_content)
        else:
            if hasattr(response, 'rendered_content'):
                self.assertFalse('Some private notes for talk' in
                                 response.rendered_content)

    def test_view_notes_accepted_not_logged_in(self):
        self.check_talk_view(self.talk_a, False, False)

    def test_view_notes_accepted_author(self):
        self.check_talk_view(self.talk_a, False, False, auth={
            'username': 'author_a', 'password': 'author_a_password',
        })

    def test_view_notes_rejected_author(self):
        self.check_talk_view(self.talk_r, False, False, auth={
            'username': 'author_r', 'password': 'author_r_password',
        })

    def test_view_notes_accepted_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_a, True, False, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_notes_rejected_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_r, True, False, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_notes_accepted_has_edit_private_notes(self):
        create_user('editor', perms=['edit_private_notes'])
        self.check_talk_view(self.talk_a, False, True, auth={
            'username': 'editor', 'password': 'editor_password',
        })

    def test_view_notes_rejected_has_edit_private_notes(self):
        # edit_private_notes doesn't imply view_all_talks
        create_user('editor', perms=['edit_private_notes'])
        self.check_talk_view(self.talk_r, False, False, auth={
            'username': 'editor', 'password': 'editor_password',
        })

    def test_view_notes_rejected_both_perms(self):
        create_user('editor', perms=['edit_private_notes', 'view_all_talks'])
        self.check_talk_view(self.talk_r, True, True, auth={
            'username': 'editor', 'password': 'editor_password',
        })

    def test_view_notes_accepted_superuser(self):
        create_user('super', superuser=True)
        self.check_talk_view(self.talk_a, True, True, auth={
            'username': 'super', 'password': 'super_password',
        })

    def test_view_notes_rejected_superuser(self):
        create_user('super', superuser=True)
        self.check_talk_view(self.talk_r, True, True, auth={
            'username': 'super', 'password': 'super_password',
        })


class TalkUpdateTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_p = create_talk("Talk P", PENDING, "author_p")
        self.client = Client()

    def check_talk_update(self, talk, status_code, auth=None):
        if auth is not None:
            self.client.login(**auth)
        response = self.client.get(
            reverse('wafer_talk_edit', kwargs={'pk': talk.pk}))
        self.assertEqual(response.status_code, status_code)
        return response

    def test_update_accepted_not_logged_in(self):
        self.check_talk_update(self.talk_a, 403)

    def test_update_rejected_not_logged_in(self):
        self.check_talk_update(self.talk_r, 403)

    def test_update_pending_not_logged_in(self):
        self.check_talk_update(self.talk_p, 403)

    def test_update_accepted_author(self):
        self.check_talk_update(self.talk_a, 403, auth={
            'username': 'author_a', 'password': 'author_a_password',
        })

    def test_update_rejected_author(self):
        self.check_talk_update(self.talk_r, 403, auth={
            'username': 'author_r', 'password': 'author_r_password',
        })

    def test_update_pending_author(self):
        self.check_talk_update(self.talk_p, 200, auth={
            'username': 'author_p', 'password': 'author_p_password',
        })

    def test_update_accepted_superuser(self):
        create_user('super', superuser=True)
        self.check_talk_update(self.talk_a, 200, auth={
            'username': 'super', 'password': 'super_password',
        })

    def test_update_rejected_superuser(self):
        create_user('super', superuser=True)
        self.check_talk_update(self.talk_r, 200, auth={
            'username': 'super', 'password': 'super_password',
        })

    def test_update_pending_superuser(self):
        create_user('super', superuser=True)
        self.check_talk_update(self.talk_p, 200, auth={
            'username': 'super', 'password': 'super_password',
        })

    def test_corresponding_author_displayed(self):
        response = self.check_talk_update(self.talk_p, 200, auth={
            'username': 'author_p', 'password': 'author_p_password',
        })
        self.assertContains(response, (
            '<p>Submitted by <a href="/users/author_p/">author_p</a>.</p>'),
            html=True)


class SpeakerTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_p = create_talk("Talk P", PENDING, "author_p")
        self.client = Client()

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_view_one_speaker(self):
        img = self.talk_a.corresponding_author.userprofile.avatar_url()
        username = self.talk_a.corresponding_author.username
        response = self.client.get(
            reverse('wafer_talks_speakers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\n".join([
            '<div class="container">',
            '<div class="row">',
            '    <div class="col-md-3">',
            '      <a href="/users/%s/">' % username,
            '        <img class="thumbnail center-block" src="%s">' % img,
            '      </a>',
            '      <a href="/users/%s/">' % username,
            '        <h3 class="text-center">author_a</h3>',
            '      </a>',
            '    </div>',
            '</div>',
            '</div>',
        ]), html=True)

    def check_n_speakers(self, n, expected_rows):
        self.talk_a.delete()
        talks = []
        for i in range(n):
            talks.append(create_talk("Talk %d" % i, ACCEPTED, "author_%d" % i))
        profiles = [t.corresponding_author.userprofile for t in talks]

        response = self.client.get(
            reverse('wafer_talks_speakers'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["speaker_rows"], [
            profiles[start:end] for start, end in expected_rows
        ])

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_view_three_speakers(self):
        self.check_n_speakers(3, [(0, 3)])

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_view_four_speakers(self):
        self.check_n_speakers(4, [(0, 4)])

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_view_five_speakers(self):
        self.check_n_speakers(5, [(0, 4), (4, 5)])

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_view_seven_speakers(self):
        self.check_n_speakers(7, [(0, 4), (4, 7)])


class TalkViewSetTests(TestCase):


    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_p = create_talk("Talk P", PENDING, "author_p")
        self.client = Client()

    def test_unauthorized_users(self):
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        response = self.client.get('/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get('/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.status_code, 404)

    def test_ordinary_users_get_accepted_talks(self):
        create_user('norm')
        self.client.login(username='norm', password='norm_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        response = self.client.get('/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get('/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.status_code, 404)

    def test_super_user_gets_everything(self):
        create_user('super', True)
        self.client.login(username='super', password='super_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk R")
        self.assertEqual(response.data['results'][2]['title'], "Talk P")
        response = self.client.get('/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get('/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.data['title'], 'Talk R')

    def test_reviewer_all_talks(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.client.login(username='reviewer', password='reviewer_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk R")
        self.assertEqual(response.data['results'][2]['title'], "Talk P")
        response = self.client.get('/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get('/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.data['title'], 'Talk R')

    def test_author_a_sees_own_talks_only(self):
        self.client.login(username='author_a', password='author_a_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")

    def test_author_r_sees_own_talk(self):
        self.client.login(username='author_r', password='author_r_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk R")

    def test_author_p_sees_own_talk(self):
        self.client.login(username='author_p', password='author_p_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk P")
