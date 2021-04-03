
from django.test import Client, TestCase
from users.models import Profile, User
from django.urls import reverse


USER_NAME = "Test User"
USER_NAME_WIH_PROFILE = "Test User With Profile"
# STATIC URLS
PROFILE_CREATE_URL = reverse("profile_create")
PROFILE_EDIT_URL = reverse("profile_edit")
LOGIN_URL = reverse("login")


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username=USER_NAME)
        user_with_profile = User.objects.create_user(
            username=USER_NAME_WIH_PROFILE
        )
        Profile.objects.create(
            user=user_with_profile,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user)
        cls.authorized_client_with_profile = Client()
        cls.authorized_client_with_profile.force_login(user_with_profile)
    
    def test_posts_url_exists_at_desired_location(self):
        """Страницы возвращают ожидаемый код ответа
        соответствующему клиенту."""
        urls = [
            [PROFILE_CREATE_URL, self.guest_client, 302],
            [PROFILE_CREATE_URL, self.authorized_client, 200],
            [PROFILE_CREATE_URL, self.authorized_client_with_profile, 302],
            [PROFILE_EDIT_URL, self.guest_client, 302],
            [PROFILE_EDIT_URL, self.authorized_client, 302],
            [PROFILE_EDIT_URL, self.authorized_client_with_profile, 200],
        ]
        for url, client, response_code in urls:
            with self.subTest(value=url):
                self.assertEqual(client.get(url).status_code, response_code)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий ему html-шаблон,
        если у пользователя есть права на просмотр страниц по данным URL."""
        url_templates = [
            [
                PROFILE_CREATE_URL,
                self.authorized_client,
                "registration/profile_new.html"
            ],
            [
                PROFILE_EDIT_URL,
                self.authorized_client_with_profile,
                "registration/profile_new.html"
            ],
        ]
        for url, client, template in url_templates:
            with self.subTest(value=url):
                self.assertTemplateUsed(client.get(url), template)

    def test_posts_url_redirects_client_to_url(self):
        """Страница перенаправляет пользователя на соответствующий URL."""
        urls = [
            [
                PROFILE_CREATE_URL,
                self.guest_client,
                f"{LOGIN_URL}?next={PROFILE_CREATE_URL}"
            ],
            [
                PROFILE_CREATE_URL,
                self.authorized_client_with_profile,
                PROFILE_EDIT_URL
            ],
            [
                PROFILE_EDIT_URL,
                self.guest_client,
                f"{LOGIN_URL}?next={PROFILE_EDIT_URL}"
            ],
            [
                PROFILE_EDIT_URL,
                self.authorized_client,
                PROFILE_CREATE_URL
            ],
        ]
        for url, client, target_url in urls:
            with self.subTest(value=url):
                self.assertRedirects(client.get(url, follow=True), target_url)