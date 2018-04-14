"""Tests for wafer.talk views."""

import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from wafer.tests.api_utils import SortedResultsClient
from wafer.talks.models import (
    Talk, TalkUrl, ACCEPTED, REJECTED, SUBMITTED, UNDER_CONSIDERATION,
    CANCELLED, PROVISIONAL)


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
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.talk_u = create_talk("Talk U", UNDER_CONSIDERATION, "author_u")
        self.talk_p = create_talk("Talk P", PROVISIONAL, "author_p")
        self.talk_c = create_talk("Talk c", CANCELLED, "author_c")
        self.client = Client()

    def test_not_logged_in(self):
        """Test that unauthenticated users only see accepted and
           cancelled talks."""
        response = self.client.get('/talks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['talk_list']),
                         set([self.talk_a, self.talk_c]))

    def test_admin_user(self):
        """Test that admin users see all talks."""
        create_user('super', superuser=True)
        self.client.login(username='super', password='super_password')
        response = self.client.get('/talks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['talk_list']),
                         set([self.talk_a, self.talk_r, self.talk_p,
                              self.talk_s, self.talk_u, self.talk_c]))

    def test_user_with_view_all(self):
        """Test that users with the view_all permission see all talks."""
        create_user('reviewer', perms=['view_all_talks'])
        self.client.login(username='reviewer', password='reviewer_password')
        response = self.client.get('/talks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['talk_list']),
                         set([self.talk_a, self.talk_r, self.talk_p,
                              self.talk_s, self.talk_u, self.talk_c]))


class TalkViewTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.talk_u = create_talk("Talk U", UNDER_CONSIDERATION, "author_u")
        self.talk_p = create_talk("Talk P", PROVISIONAL, "author_p")
        self.talk_c = create_talk("Talk C", CANCELLED, "author_c")
        self.client = Client()

    def check_talk_view(self, talk, status_code, auth=None):
        if auth is not None:
            self.client.login(**auth)
        response = self.client.get(talk.get_absolute_url())
        self.assertEqual(response.status_code, status_code)

    def test_view_accepted_not_logged_in(self):
        self.check_talk_view(self.talk_a, 200)

    def test_view_rejected_not_logged_in(self):
        self.check_talk_view(self.talk_r, 403)

    def test_view_cancelled_not_logged_in(self):
        self.check_talk_view(self.talk_c, 200)

    def test_view_submitted_not_logged_in(self):
        self.check_talk_view(self.talk_s, 403)

    def test_view_consideration_not_logged_in(self):
        self.check_talk_view(self.talk_u, 403)

    def test_view_provisional_not_logged_in(self):
        self.check_talk_view(self.talk_p, 403)

    def test_view_accepted_author(self):
        self.check_talk_view(self.talk_a, 200, auth={
            'username': 'author_a', 'password': 'author_a_password',
        })

    def test_view_rejected_author(self):
        self.check_talk_view(self.talk_r, 200, auth={
            'username': 'author_r', 'password': 'author_r_password',
        })

    def test_view_submitted_author(self):
        self.check_talk_view(self.talk_s, 200, auth={
            'username': 'author_s', 'password': 'author_s_password',
        })

    def test_view_consideration_author(self):
        self.check_talk_view(self.talk_u, 200, auth={
            'username': 'author_u', 'password': 'author_u_password',
        })

    def test_view_provisional_author(self):
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

    def test_view_submitted_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_s, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_provisional_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_p, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_consideration_has_view_all_perm(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.check_talk_view(self.talk_u, 200, auth={
            'username': 'reviewer', 'password': 'reviewer_password',
        })

    def test_view_canonicalizes_url(self):
        response = self.client.get(
            reverse('wafer_talk', kwargs={'pk': self.talk_a.pk}))
        self.assertEqual(response.status_code, 302)

    def test_view_canonicalizes_url_correctly(self):
        response = self.client.get(
            reverse('wafer_talk', kwargs={'pk': self.talk_a.pk}),
            follow=True)
        self.assertEqual(response.status_code, 200)


class TalkNoteViewTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.client = Client()

    def check_talk_view(self, talk, notes_visible, private_notes_visible,
                        auth=None):
        if auth is not None:
            self.client.login(**auth)
        response = self.client.get(talk.get_absolute_url())
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
            self.assertTrue(
                'Some private notes for talk' in response.rendered_content)
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
        self.talk_p = create_talk("Talk P", PROVISIONAL, "author_p")
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.talk_u = create_talk("Talk U", UNDER_CONSIDERATION, "author_u")
        self.talk_c = create_talk("Talk C", CANCELLED, "author_c")
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

    def test_update_submitted_not_logged_in(self):
        self.check_talk_update(self.talk_s, 403)

    def test_update_cancelled_not_logged_in(self):
        self.check_talk_update(self.talk_c, 403)

    def test_update_provisional_not_logged_in(self):
        self.check_talk_update(self.talk_p, 403)

    def test_update_consideration_not_logged_in(self):
        self.check_talk_update(self.talk_u, 403)

    def test_update_accepted_author(self):
        self.check_talk_update(self.talk_a, 403, auth={
            'username': 'author_a', 'password': 'author_a_password',
        })

    def test_update_rejected_author(self):
        self.check_talk_update(self.talk_r, 403, auth={
            'username': 'author_r', 'password': 'author_r_password',
        })

    def test_update_cancelled_author(self):
        self.check_talk_update(self.talk_c, 403, auth={
            'username': 'author_c', 'password': 'author_c_password',
        })

    def test_update_provisional_author(self):
        self.check_talk_update(self.talk_p, 403, auth={
            'username': 'author_p', 'password': 'author_p_password',
        })

    def test_update_submitted_author(self):
        self.check_talk_update(self.talk_s, 200, auth={
            'username': 'author_s', 'password': 'author_s_password',
        })

    def test_update_consideration_author(self):
        self.check_talk_update(self.talk_u, 200, auth={
            'username': 'author_u', 'password': 'author_u_password',
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

    def test_update_submitted_superuser(self):
        create_user('super', superuser=True)
        self.check_talk_update(self.talk_s, 200, auth={
            'username': 'super', 'password': 'super_password',
        })

    def test_corresponding_author_displayed(self):
        response = self.check_talk_update(self.talk_s, 200, auth={
            'username': 'author_s', 'password': 'author_s_password',
        })
        self.assertContains(response, (
            '<p>Submitted by <a href="/users/author_s/">author_s</a>.</p>'),
            html=True)


class SpeakerTests(TestCase):
    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.client = Client()

    @mock.patch('wafer.users.models.UserProfile.avatar_url', mock_avatar_url)
    def test_view_one_speaker(self):
        img = self.talk_a.corresponding_author.userprofile.avatar_url()
        username = self.talk_a.corresponding_author.username
        response = self.client.get(
            reverse('wafer_talks_speakers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\n".join([
            '<section class="wafer wafer-speakers">',
            '<h1>Speakers</h1>'
            '<div class="container">'
            '  <div class="row">',
            '    <div class="col-md-3">',
            '      <div class="wafer-speakers-logo">',
            '        <a href="/users/%s/">' % username,
            '          <img class="thumbnail mx-auto" src="%s">' % img,
            '        </a>',
            '      </div>',
            '      <div class="wafer-speakers-name">',
            '        <a href="/users/%s/">' % username,
            '          author_a',
            '        </a>',
            '      </div>',
            '    </div>',
            '  </div>',
            '</div>',
            '</section>',
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


class TalkViewSetPermissionTests(TestCase):

    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.client = SortedResultsClient(sort_key="title")

    def test_unauthorized_users(self):
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.status_code, 404)

    def test_ordinary_users_get_accepted_talks(self):
        create_user('norm')
        self.client.login(username='norm', password='norm_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.status_code, 404)

    def test_super_user_gets_everything(self):
        create_user('super', True)
        self.client.login(username='super', password='super_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk R")
        self.assertEqual(response.data['results'][2]['title'], "Talk S")
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_r.talk_id)
        self.assertEqual(response.data['title'], 'Talk R')

    def test_reviewer_all_talks(self):
        create_user('reviewer', perms=['view_all_talks'])
        self.client.login(username='reviewer', password='reviewer_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk R")
        self.assertEqual(response.data['results'][2]['title'], "Talk S")
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_a.talk_id)
        self.assertEqual(response.data['title'], 'Talk A')
        response = self.client.get(
            '/talks/api/talks/%d/' % self.talk_r.talk_id)
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

    def test_author_s_sees_own_talk(self):
        self.client.login(username='author_s', password='author_s_password')
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['title'], "Talk A")
        self.assertEqual(response.data['results'][1]['title'], "Talk S")


class TalkViewSetTests(TestCase):

    def setUp(self):
        create_user('super', True)
        self.client = SortedResultsClient(sort_key="title")
        self.client.login(username='super', password='super_password')

    def mk_result(self, talk):
        def mk_url(talk_url):
            return {
                'id': talk_url.id, 'description': talk_url.description,
                'url': talk_url.url,
            }
        return {
            'talk_id': talk.talk_id, 'talk_type': talk.talk_type,
            'status': talk.status, 'title': talk.title,
            'abstract': talk.abstract.raw,
            'corresponding_author': talk.corresponding_author.id,
            'authors': [talk.corresponding_author.id],
            'kv': [],
            'urls': [mk_url(url) for url in talk.urls.all()]
        }

    def test_list_talks(self):
        talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        talk_b = create_talk("Talk B", REJECTED, "author_b")
        response = self.client.get('/talks/api/talks/')
        self.assertEqual(response.data['results'], [
            self.mk_result(talk_a), self.mk_result(talk_b),
        ])

    def test_retrieve_talk(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        talk.abstract = "Abstract Talk A"
        talk.save()
        TalkUrl.objects.create(
            talk=talk, url="http://example.com/", description="video")
        response = self.client.get(
            '/talks/api/talks/%d/' % talk.talk_id)
        self.assertEqual(response.data, self.mk_result(talk))

    def test_create_talk(self):
        author = create_user("author")
        response = self.client.post('/talks/api/talks/', data={
            'talk_type': None, 'status': 'A', 'title': 'Talk Foo',
            'abstract': 'Concrete',
            'corresponding_author': author.id,
            'authors': [author.id],
        }, format='json')
        talk = Talk.objects.get()
        self.assertEqual(response.data, self.mk_result(talk))

    def test_update_talk(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        response = self.client.put(
            '/talks/api/talks/%d/' % talk.talk_id, data={
                'talk_type': None, 'status': 'R', 'title': 'Talk Zoom',
                'abstract': 'Concreter',
                'corresponding_author': talk.corresponding_author.id,
                'authors': [talk.corresponding_author.id],
            }, format="json")
        talk = Talk.objects.get()
        self.assertEqual(response.data, self.mk_result(talk))
        self.assertEqual(talk.abstract.raw, u"Concreter")

    def test_patch_talk(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        response = self.client.patch(
            '/talks/api/talks/%d/' % talk.talk_id, data={
                'abstract': 'Concrete',
            }, format="json")
        talk = Talk.objects.get()
        self.assertEqual(response.data, self.mk_result(talk))
        self.assertEqual(talk.abstract.raw, u"Concrete")

    def test_delete_talk(self):
        talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        talk_b = create_talk("Talk B", ACCEPTED, "author_b")
        response = self.client.delete('/talks/api/talks/%d/' % talk_a.talk_id)
        talk_remaining = Talk.objects.get()
        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(talk_remaining, talk_b)


class TalkUrlsViewSetPermissionTests(TestCase):

    def setUp(self):
        self.talk_a = create_talk("Talk A", ACCEPTED, "author_a")
        self.talk_r = create_talk("Talk R", REJECTED, "author_r")
        self.talk_s = create_talk("Talk S", SUBMITTED, "author_s")
        self.client = SortedResultsClient(sort_key="url")

    def assert_urls_accessible(self, talk):
        response = self.client.get(
            '/talks/api/talks/%d/urls/' % talk.talk_id)
        self.assertEqual(response.data['results'], [])

    def assert_urls_forbidden(self, talk):
        response = self.client.get(
            '/talks/api/talks/%d/urls/' % talk.talk_id)
        self.assertEqual(response.status_code, 403)

    def assert_missing_talk_urls_code(self, code):
        missing_talk_id = 4242  # implausibly large id
        response = self.client.get(
            '/talks/api/talks/%d/urls/' % missing_talk_id)
        self.assertEqual(response.status_code, code)

    def test_unauthorized_users_get_no_talk_urls(self):
        self.assert_urls_forbidden(self.talk_a)
        self.assert_urls_forbidden(self.talk_s)
        self.assert_urls_forbidden(self.talk_r)
        self.assert_missing_talk_urls_code(403)

    def test_ordinary_users_get_no_talk_urls(self):
        create_user('norm')
        self.assert_urls_forbidden(self.talk_a)
        self.assert_urls_forbidden(self.talk_s)
        self.assert_urls_forbidden(self.talk_r)
        self.assert_missing_talk_urls_code(403)

    def test_super_user_gets_all_talk_urls(self):
        create_user('super', True)
        self.client.login(username='super', password='super_password')
        self.assert_urls_accessible(self.talk_a)
        self.assert_urls_accessible(self.talk_s)
        self.assert_urls_accessible(self.talk_r)
        self.assert_missing_talk_urls_code(404)


class TalkUrlsViewSetTests(TestCase):

    def setUp(self):
        create_user('super', True)
        self.client = SortedResultsClient(sort_key="url")
        self.client.login(username='super', password='super_password')

    def mk_result(self, talk_url):
        return {
            'id': talk_url.id, 'description': talk_url.description,
            'url': talk_url.url,
        }

    def test_list_talk_urls(self):
        talk = create_talk("Talk", ACCEPTED, "author")
        url_a = TalkUrl.objects.create(
            talk=talk, url="http://a.example.com/", description="video")
        url_b = TalkUrl.objects.create(
            talk=talk, url="http://b.example.com/", description="slides")
        response = self.client.get('/talks/api/talks/%d/urls/' % talk.talk_id)
        self.assertEqual(response.data['results'], [
            self.mk_result(url_a), self.mk_result(url_b),
        ])

    def test_retrieve_talk_url(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        url = TalkUrl.objects.create(
            talk=talk, url="http://a.example.com/", description="video")
        response = self.client.get(
            '/talks/api/talks/%d/urls/%d/' % (talk.talk_id, url.id))
        self.assertEqual(response.data, self.mk_result(url))

    def test_create_talk_url(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        response = self.client.post(
            '/talks/api/talks/%d/urls/' % talk.talk_id, data={
                'description': u'slides',
                'url': u'http://www.example.com/video',
            }, format="json")
        [talk_url] = talk.urls.all()
        self.assertEqual(response.data, self.mk_result(talk_url))
        self.assertEqual(talk_url.url, u'http://www.example.com/video')
        self.assertEqual(talk_url.description, u'slides')

    def test_update_talk_url(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        url = TalkUrl.objects.create(
            talk=talk, url="http://a.example.com/", description="video")
        response = self.client.put(
            '/talks/api/talks/%d/urls/%d/' % (talk.talk_id, url.id), data={
                'description': u'slides',
                'url': u'http://www.example.com/video',
            }, format="json")
        [talk_url] = talk.urls.all()
        self.assertEqual(response.data, self.mk_result(talk_url))
        self.assertEqual(talk_url.url, u'http://www.example.com/video')
        self.assertEqual(talk_url.description, u'slides')

    def test_patch_talk_url(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        url = TalkUrl.objects.create(
            talk=talk, url="http://a.example.com/", description="video")
        response = self.client.patch(
            '/talks/api/talks/%d/urls/%d/' % (talk.talk_id, url.id), data={
                'url': 'http://new.example.com/',
            }, format="json")
        [talk_url] = talk.urls.all()
        self.assertEqual(response.data, self.mk_result(talk_url))
        self.assertEqual(talk_url.url, u'http://new.example.com/')
        self.assertEqual(talk_url.description, u'video')

    def test_delete_talk_url(self):
        talk = create_talk("Talk A", ACCEPTED, "author_a")
        url_a = TalkUrl.objects.create(
            talk=talk, url="http://a.example.com/", description="video")
        url_b = TalkUrl.objects.create(
            talk=talk, url="http://a.example.com/", description="video")
        response = self.client.delete(
            '/talks/api/talks/%d/urls/%d/' % (talk.talk_id, url_a.id))
        [talk_url_b] = talk.urls.all()
        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(talk_url_b, url_b)
