from django.test.testcases import TestCase
from django.urls import reverse


class UsersRoutesTests(TestCase):
    def test_routes(self):
        """URL-адрес, рассчитанный через name,
        соответствует ожидаемому видимому URL."""
        routes = {
            # Static URLs
            "/auth/profile_create/": reverse("profile_create"),
            "/auth/profile_edit/": reverse("profile_edit"),
        }
        for url, reversed_url in routes.items():
            self.assertEqual(url, reversed_url)
