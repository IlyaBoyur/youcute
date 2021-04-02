from django.test import TestCase
from users.models import User, Profile


class ProfileModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='TestUser')
        cls.profile = Profile.objects.create(user=user)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        profile = self.profile
        field_verboses = {
            "image": "Аватар",
            "bio": "Об авторе",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    profile._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        profile = self.profile
        field_help_texts = {
            "image": "Загрузите фотографию",
            "bio": "Расскажите о себе",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    profile._meta.get_field(value).help_text, expected
                )
