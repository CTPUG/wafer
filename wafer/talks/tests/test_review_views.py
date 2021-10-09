"""Tests for wafer.talk review form behaviour."""

from django.test import Client, TestCase
from django.urls import reverse

from reversion import revisions
from reversion.models import Version

from wafer.talks.models import (SUBMITTED, UNDER_CONSIDERATION,
                                ReviewAspect, Review)
from wafer.talks.forms import ReviewForm, make_aspect_key

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
        self.assertTrue(Version.objects.get_for_object(self.talk_a), 1)
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': self.talk_a.pk}),
                                    data={'notes': 'Review notes',
                                          make_aspect_key(self.aspect_1): '1',
                                          make_aspect_key(self.aspect_2): '2'})
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(talk=self.talk_a, reviewer=self.reviewer_a)
        self.assertEqual(review.avg_score, 1.5)
        self.talk_a.refresh_from_db()
        self.assertEqual(self.talk_a.status, UNDER_CONSIDERATION)
        self.assertTrue(Version.objects.get_for_object(self.talk_a), 2)
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
        version = Version.objects.get_for_object(review).order_by('-pk').first()
        review_1_str = str(review)
        self.assertEqual(review_1_str, version.object_repr)
        response = self.client.post(reverse('wafer_talk_review',  kwargs={'pk': self.talk_a.pk}),
                                    data={'notes': 'New Notes',
                                          make_aspect_key(self.aspect_1): '2',
                                          make_aspect_key(self.aspect_2): '0'})
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get(talk=self.talk_a, reviewer=self.reviewer_a)
        version = Version.objects.get_for_object(review).order_by('-pk').first()
        self.assertEqual(str(review), version.object_repr)
        self.assertNotEqual(str(review), review_1_str)
