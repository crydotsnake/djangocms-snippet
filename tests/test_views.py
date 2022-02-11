from cms.test_utils.testcases import CMSTestCase
from cms.utils.urlutils import admin_reverse

from .utils.factories import SnippetWithVersionFactory


class PreviewViewTestCase(CMSTestCase):
    def setUp(self):
        self.snippet = SnippetWithVersionFactory(html="<h1>Test Title</h1><br><p>Test paragraph</p>")
        self.user = self.get_superuser()

    def test_preview_renders_html(self):
        """
        Check that our snippet HTML is rendered, unescaped, on the page
        """
        preview_url = admin_reverse(
            "djangocms_snippet_snippet_preview",
            kwargs={"snippet_id": self.snippet.id},
        )
        with self.login_user_context(self.user):
            response = self.client.get(preview_url)

        self.assertEqual(self.snippet.html, "<h1>Test Title</h1><br><p>Test paragraph</p>")
        self.assertEqual(response.status_code, 200)
        # Removing html escaping, means the content  is rendered including the tags on the page, but also means that
        # the response will contain character entity references.
        self.assertContains(response, "&lt;h1&gt;Test Title&lt;/h1&gt;&lt;br&gt;&lt;p&gt;Test paragraph&lt;/p&gt;")

    def test_preview_raises_302_no_snippet(self):
        """
        With no Snippet to preview, a 302 will be raised and the user will be redirected to the admin
        """
        preview_url = admin_reverse(
            "djangocms_snippet_snippet_preview",
            kwargs={"snippet_id": 999},  # Non existent PK!
        )
        with self.login_user_context(self.user):
            response = self.client.get(preview_url)

        self.assertEqual(response.status_code, 302)
