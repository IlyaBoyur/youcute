import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse

from users.models import Profile, User


USER_NAME = "Test User"
PROFILE_CREATE_URL = reverse("profile_create")
PROFILE_EDIT_URL = reverse("profile_edit")
PROFILE_URL = reverse("profile", args=[USER_NAME])

SMALL_GIF_CONTENT = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class UserProfileEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        Profile.objects.create(user=cls.user)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_update_user(self):
        """Валидная форма обновляет 'profile'."""
        form_data = {
            "bio": "Биография после редактирования",
            "image": SimpleUploadedFile(
                "small_forms_update.gif",
                content=SMALL_GIF_CONTENT,
                content_type="image/gif"
            ),
        }
        response = self.authorized_client.post(
            PROFILE_CREATE_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, PROFILE_URL)
        # Получаем обновленный профиль
        updated_profile = response.context["author"].profile
        self.assertEqual(updated_profile.bio, form_data["bio"])
        self.assertEqual(
            updated_profile.image,
            "profiles/small_forms_update.gif"
        )

    def test_update_user_guest(self):
        """Гость не может редактировать 'profile'."""
        profile_before_edit = Profile.objects.get(user=self.user)
        self.guest_client.post(
            PROFILE_EDIT_URL,
            data={
                "bio": "Новая биография",
                "image": SimpleUploadedFile("small_forms_update.gif",
                                            content=SMALL_GIF_CONTENT,
                                            content_type="image/gif"),
            },
        )
        profile_after_edit = Profile.objects.get(user=self.user)
        self.assertEqual(
            profile_before_edit,
            profile_after_edit
        )

    def test_user_profile_edit_form_show_correct_context(self):
        """Типы полей формы в словаре 'context' в ответе по URL-адресу
        соответствуют ожиданиям."""
        urls = [
            PROFILE_CREATE_URL,
            PROFILE_EDIT_URL,
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                form_fields = {
                    "bio": forms.fields.CharField,
                    "image": forms.fields.ImageField,
                }
                for value, expected_type in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context["form"].fields.get(value)
                        self.assertIsInstance(form_field, expected_type)
