"""Tests for wafer.pages views."""

from django.test import Client, TestCase


class UsersTalksTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_missing_index_page(self):
        """Test that when there is no page named index, the missing index page is
           returned."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, """
              <section>
                <h1>Index page missing</h1>
                <p>Create a Page called 'index'.</p>
              </section>
        """, html=True)
