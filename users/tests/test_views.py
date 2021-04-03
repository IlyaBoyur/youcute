from django.test import Client, TestCase
from django.urls import reverse

from users.models import Profile, User


USER_NAME = "Test User"
USER_NAME_OTHER = "Test User Other"
# STATIC URLS
PROFILE_EDIT_URL = reverse("profile_edit")


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(username=USER_NAME)
        cls.profile = Profile.objects.create(user=user)
        cls.authorized_client_with_profile = Client()
        cls.authorized_client_with_profile.force_login(user)

    def test_page_show_profile_in_context(self):
        """Контекст шаблона содержит 'profile'."""
        response = self.authorized_client_with_profile.get(PROFILE_EDIT_URL)
        self.assertEqual(self.profile, response.context["profile"])
