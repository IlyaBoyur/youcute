from django.test import Client, TestCase
from django.urls import reverse


class AboutStaticPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.name_templates = {
            "about:author": "author.html",
            "about:tech": "tech.html",
        }

    def setUp(self):
        self.guest_client = Client()

    def test_static_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени, указанном в urlpatterns,
        доступен."""
        for name in AboutStaticPagesTests.name_templates:
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_static__page_uses_correct_template(self):
        """При запросе к имени, указанном в urlpatterns,
        применяется соответствующий шаблон."""
        for name, template in AboutStaticPagesTests.name_templates.items():
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
