import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse

from posts.models import Comment, Group, Post, User


USER_NAME = "TestUser"
GROUP_SLUG = "test-group-slug"

# STATIC URLS
INDEX_URL = reverse("index")
NEW_POST_URL = reverse("new_post")
# NON STATIC URLS
PROFILE_URL = reverse("profile", kwargs={"username": USER_NAME})
GROUP_URL = reverse("group_posts", kwargs={"slug": GROUP_SLUG})


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст до редактирования",
        )
        # NON STATIC GENERATED URLS
        cls.POST_URL = reverse("post", args=[USER_NAME, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit", args=[USER_NAME, cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Валидная форма создает Post."""
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 1)
        uploaded = SimpleUploadedFile(
            "small_forms.gif",
            content=(b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'),
            content_type="image/gif"
        )
        form_data = {
            "group": self.group.id,
            "text": "Тестовый текст",
            "image": uploaded,
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        created_post = [post for post in response.context["page"]
                        if self.post.id != post.id][0]
        self.assertEqual(created_post.author, self.user)
        self.assertEqual(created_post.group.id, form_data["group"])
        self.assertEqual(created_post.text, form_data["text"])
        self.assertEqual(created_post.image, "posts/small_forms.gif")

    def test_update_post(self):
        """Валидная форма обновляет существующий Post."""
        form_data = {
            "group": self.group.id,
            "text": "Тестовый текст после редактирования",
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.POST_URL)
        # Получаем обновленный пост со страницы поста
        updated_post = response.context["post"]
        self.assertEqual(updated_post.author, self.user)
        self.assertEqual(updated_post.group.id, form_data["group"])
        self.assertEqual(updated_post.text, form_data["text"])

    def test_page_post_form_show_correct_context(self):
        """Типы полей формы в словаре 'context' в ответе по URL-адресу
        соответствуют ожиданиям."""
        urls = [
            NEW_POST_URL,
            self.POST_EDIT_URL,
        ]
        for url in urls:
            with self.subTest(value=url):
                response = self.authorized_client.get(url)
                form_fields = {
                    "group": forms.fields.ChoiceField,
                    "text": forms.fields.CharField,
                    "image": forms.fields.ImageField,
                }
                for value, expected_type in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context["form"].fields.get(value)
                        self.assertIsInstance(form_field, expected_type)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )
        cls.POST_URL = reverse("post", args=[USER_NAME, cls.post.id])
        cls.POST_COMMENT_URL = reverse("add_comment",
                                       args=[USER_NAME, cls.post.id])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_comment(self):
        """Валидная форма создает Comment."""
        comment_count = Comment.objects.count()
        form_data = {
            "text": "Тестовый комментарий",
        }
        response = self.authorized_client.post(
            self.POST_COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(response.context["post"].comments.count(), 1)
        added_comment = response.context["comments"][0]
        self.assertEqual(added_comment.post, self.post)
        self.assertEqual(added_comment.author, self.user)
        self.assertEqual(added_comment.text, form_data["text"])
