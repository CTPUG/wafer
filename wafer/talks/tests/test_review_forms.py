"""Tests for wafer.talk review form behaviour."""

from django.test import TestCase, override_settings
from django.urls import reverse

from reversion import revisions

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

    def _save_review(self, review, scores=('1', '1')):
        form = ReviewForm(instance=review, talk=self.talk_a, user=self.reviewer_a,
                       data={'notes': "Test review",
                             make_aspect_key(self.aspect_1): scores[0],
                             make_aspect_key(self.aspect_2): scores[1]})
        form.is_valid()
        with revisions.create_revision():
            form.save()
        return Review.objects.get(talk=self.talk_a, reviewer=self.reviewer_a)

    def test_review_form(self):
        """Test that submitting a review works"""
        form = ReviewForm(instance=None, talk=self.talk_a, user=self.reviewer_a,
                       data={'notes': "Test review",
                             make_aspect_key(self.aspect_1): '1',
                             make_aspect_key(self.aspect_2): '1'})
        self.assertTrue(form.is_valid())
        self.assertEqual(Review.objects.count(), 0)
        with revisions.create_revision():
            form.save()
        self.assertEqual(Review.objects.count(), 1)

    def test_review_outdated(self):
        """Test that reviews are marked as outdated correctly
           and that updatingt the review does the right thing"""
        review = self._save_review(None)
        self.assertTrue(review.is_current())
        # Change the talk time
        self.talk_a.notes = 'New note'
        with revisions.create_revision():
            self.talk_a.save()
        self.assertFalse(review.is_current())
        # Change the review
        review.notes = 'New notes'
        with revisions.create_revision():
            review.save()
        self.assertTrue(review.is_current())

    def test_review_scores(self):
        """Test the behaviour of review scores"""
        review = self._save_review(None)
        self.assertEqual(review.avg_score, 1.0)
        self._save_review(review, ('1', '0'))
        self.assertEqual(review.avg_score, 0.5)
        self._save_review(review, ('-1', '1'))
        self.assertEqual(review.avg_score, 0)
        
    def test_score_limits(self):
        """"Test that we set the limits correctly in the form"""
        key1 = make_aspect_key(self.aspect_1)
        key2 = make_aspect_key(self.aspect_2)
        review = self._save_review(None)

        form = ReviewForm(instance=review, talk=self.talk_a, user=self.reviewer_a,
                          data={'notes': "Test review", key1:'1', key2: '3'})
        self.assertIn(key2, form.errors)
        self.assertNotIn(key1, form.errors)
        self.assertIn("less than or equal", form.errors[key2][0])
        form = ReviewForm(instance=review, talk=self.talk_a, user=self.reviewer_a,
                          data={'notes': "Test review", key1:'-3', key2: '1'})
        self.assertIn(key1, form.errors)
        self.assertNotIn(key2, form.errors)
        self.assertIn("greater than or equal", form.errors[key1][0])

        # Check that we handle settings correctly
        with override_settings(WAFER_TALK_REVIEW_SCORES=(2, 7)):
            form = ReviewForm(instance=review, talk=self.talk_a, user=self.reviewer_a,
                              data={'notes': "Test review",
                                    make_aspect_key(self.aspect_1): '1',
                                    make_aspect_key(self.aspect_2): '5'})
            self.assertIn(key1, form.errors)
            self.assertNotIn(key2, form.errors, key2)
            self.assertIn("greater than or equal", form.errors[key1][0])
            form = ReviewForm(instance=review, talk=self.talk_a, user=self.reviewer_a,
                              data={'notes': "Test review",
                                    make_aspect_key(self.aspect_1): '5',
                                    make_aspect_key(self.aspect_2): '9'})
            self.assertIn(key2, form.errors)
            self.assertNotIn(key1, form.errors)
            self.assertIn("less than or equal", form.errors[key2][0])
