"""Tests for wafer.talk review form behaviour."""

from django.test import Client, TestCase
from django.urls import reverse

from reversion import revisions
from reversion.models import Version

from wafer.talks.models import (SUBMITTED, UNDER_CONSIDERATION,
                                ReviewAspect, Review)
from wafer.talks.forms import make_aspect_key

from wafer.tests.utils import create_user
from wafer.talks.tests.fixtures import create_talk




class ReviewFormTests(TestCase):
    def setUp(self):
        self.reviewer_a = create_user('reviewer_a', perms=('add_review',))
        self.talk_a = create_talk('Talk A', SUBMITTED, "author_a")
        with revisions.create_revision():
            # Ensure we have an initial revision
            self.talk_a.save()
        self.aspect_1 = ReviewAspect.objects.create(name='General')
        self.aspect_2 = ReviewAspect.objects.create(name='Other')
        self.client = Client()

    def test_review_submission(self):
        """Test that submitting a review works"""
        self.client.login(username='reviewer_a', password='reviewer_a_password')
        self.assertEqual(Version.objects.get_for_object(self.talk_a).count(), 1)
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': self.talk_a.pk}),
                                    data={'notes': 'Review notes',
                                          make_aspect_key(self.aspect_1): '1',
                                          make_aspect_key(self.aspect_2): '2'})
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(talk=self.talk_a, reviewer=self.reviewer_a)
        self.assertEqual(review.avg_score, 1.5)
        self.talk_a.refresh_from_db()
        self.assertEqual(self.talk_a.status, UNDER_CONSIDERATION)
        self.assertEqual(Version.objects.get_for_object(self.talk_a).count(), 2)
        self.assertTrue(review.is_current())

    def test_review_revision_str(self):
        """Check that we update the revision repr correctly."""
        self.client.login(username='reviewer_a', password='reviewer_a_password')
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': self.talk_a.pk}),
                                    data={'notes': 'Review notes',
                                          make_aspect_key(self.aspect_1): '1',
                                          make_aspect_key(self.aspect_2): '2'})
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(talk=self.talk_a, reviewer=self.reviewer_a)
        self.assertEqual(Version.objects.get_for_object(review).count(), 1)
        version = Version.objects.get_for_object(review).order_by('-pk').first()
        review_1_str = str(review)
        self.assertEqual(review_1_str, version.object_repr)
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': self.talk_a.pk}),
                                    data={'notes': 'New Notes',
                                          make_aspect_key(self.aspect_1): '2',
                                          make_aspect_key(self.aspect_2): '0'})
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(talk=self.talk_a, reviewer=self.reviewer_a)
        self.assertEqual(Version.objects.get_for_object(review).count(), 2)
        version = Version.objects.get_for_object(review).order_by('-pk').first()
        self.assertEqual(str(review), version.object_repr)
        self.assertNotEqual(str(review), review_1_str)


class ReviewViewSetTests(TestCase):

    def setUp(self):
        self.super = create_user('super', superuser=True)
        self.reviewer_a = create_user('reviewer_a', perms=('add_review',))
        self.reviewer_b = create_user('reviewer_b', perms=['add_review', 'view_all_reviews'])
        self.aspect_1 = ReviewAspect.objects.create(name='General')
        self.aspect_2 = ReviewAspect.objects.create(name='Other')
        self.client = Client()

    def mk_result(self, review_id, talk, reviewer, scores):
        def mk_aspects(scores):
            return [
                {'aspect': {'name': self.aspect_1.name}, 'value': scores[0]},
                {'aspect': {'name': self.aspect_2.name}, 'value': scores[1]},
            ]
        return {
            'id': review_id, 'talk': talk.talk_id,
            'reviewer': reviewer.id,
            'notes': f'<p>{reviewer.username} notes</p>',
            'scores':  mk_aspects(scores),
            'avg_score': sum(scores)/len(scores),
        }

    def test_list_talk_reviews(self):
        talk = create_talk("Talk", UNDER_CONSIDERATION, "author")
        talk2 = create_talk("Talk 2", UNDER_CONSIDERATION, "author 2")

        self.client.login(username='reviewer_a', password='reviewer_a_password')
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': talk.pk}),
                                    data={'notes': 'reviewer_a notes',
                                          make_aspect_key(self.aspect_1): '1',
                                          make_aspect_key(self.aspect_2): '2'})
        self.client.login(username='reviewer_b', password='reviewer_b_password')
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': talk.pk}),
                                    data={'notes': 'reviewer_b notes',
                                          make_aspect_key(self.aspect_1): '2',
                                          make_aspect_key(self.aspect_2): '2'})

        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': talk2.pk}),
                                    data={'notes': 'reviewer_b notes',
                                          make_aspect_key(self.aspect_1): '1',
                                          make_aspect_key(self.aspect_2): '1'})


        review1 = Review.objects.get(talk=talk, reviewer=self.reviewer_a)
        review2 = Review.objects.get(talk=talk, reviewer=self.reviewer_b)
        review3 = Review.objects.get(talk=talk2, reviewer=self.reviewer_b)


        # Check that the user with 'view_all_reviews' sees the reviews
        response = self.client.get('/talks/api/talks/%d/reviews/' % talk.talk_id)
        self.assertEqual(response.data['results'], [
            self.mk_result(review1.id, talk, self.reviewer_a, [1, 2]),
            self.mk_result(review2.id, talk, self.reviewer_b, [2, 2]),
        ])

        response = self.client.get('/talks/api/talks/%d/reviews/' % talk2.talk_id)
        self.assertEqual(response.data['results'], [
            self.mk_result(review3.id, talk2, self.reviewer_b, [1, 1]),
        ])
        # Check that the user without the permissions doesn't
        self.client.login(username='reviewer_a', password='reviewer_a_password')
        response = self.client.get('/talks/api/talks/%d/reviews/' % talk.talk_id)
        self.assertEqual(response.data['results'], [])
        # Check the super user can see the eiews
        self.client.login(username='super', password='super_password')
        response = self.client.get('/talks/api/talks/%d/reviews/' % talk.talk_id)
        self.assertEqual(response.data['results'], [
            self.mk_result(review1.id, talk, self.reviewer_a, [1, 2]),
            self.mk_result(review2.id, talk, self.reviewer_b, [2, 2]),
        ])

        response = self.client.get('/talks/api/talks/%d/reviews/' % talk2.talk_id)
        self.assertEqual(response.data['results'], [
            self.mk_result(review3.id, talk2, self.reviewer_b, [1, 1]),
        ])
