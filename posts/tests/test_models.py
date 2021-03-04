from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            author=test_user,
            text="Самый простой тестовый пост",
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            "group": "Группа",
            "text": "Текст"
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            "group": "Выберите группу",
            "text": "Что нового?",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_object_name_returns_post_data(self):
        """__str__ возвращает первые 15 символов поля text."""
        post = self.post
        self.assertEqual(post.text[:15], str(post))


class GroupModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create()

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            "title": "Заголовок",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            "title": "Дайте название группе",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )

    def test_object_name_is_title_field(self):
        """__str__ возвращает поле title."""
        group = self.group
        self.assertEqual(group.title, str(group))
