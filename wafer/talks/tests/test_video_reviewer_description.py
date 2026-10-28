"""Tests for configurable video reviewer information."""

from django.test import TestCase, override_settings

from wafer.tests.utils import create_user
from wafer.talks.forms import TalkForm


class VideoReviewerDescriptionTests(TestCase):
    def setUp(self):
        self.user = create_user("description_author")

    @override_settings(
        WAFER_VIDEO_REVIEWER_DESCRIPTION=(
            "Review requests are expected within **two weeks**."
        )
    )
    def test_custom_markdown_description_is_added_before_reviewer_field(self):
        form = TalkForm(user=self.user, instance=None)

        layout_fields = form.helper.layout.fields
        reviewer_index = layout_fields.index("video_reviewer")
        description_blocks = [
            (index, getattr(field, "html", ""))
            for index, field in enumerate(layout_fields)
            if getattr(field, "html", None)
        ]

        matching_blocks = [
            (index, html)
            for index, html in description_blocks
            if "two weeks" in html
        ]
        self.assertTrue(
            matching_blocks,
            "The configured description should appear in the form layout.",
        )
        self.assertLess(matching_blocks[0][0], reviewer_index)
        self.assertIn("<strong>two weeks</strong>", matching_blocks[0][1])

    @override_settings(WAFER_VIDEO_REVIEWER_DESCRIPTION="")
    def test_empty_description_does_not_add_a_description_block(self):
        form = TalkForm(user=self.user, instance=None)
        layout_fields = form.helper.layout.fields

        self.assertIn("video_reviewer", layout_fields)
        self.assertFalse(
            any(
                "two weeks" in getattr(field, "html", "")
                for field in layout_fields
            )
        )
