from django.test import Client, TestCase


class AboutStaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_templates = {
            "/about/author/": "author.html",
            "/about/tech/": "tech.html",
        }

    def setUp(self):
        self.guest_client = Client()

    def test_static_url_is_available_for_guests(self):
        """Проверка доступности URL всем пользователям."""
        for url in AboutStaticURLTests.url_templates:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_static_url_uses_correct_template(self):
        """Проверка шаблона для URL."""
        for url, template in AboutStaticURLTests.url_templates.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
