import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User
from posts.settings import POSTS_PER_PAGE


USER_NAME = "TestUser"
USER_NAME_OTHER = "TestUserOther"
GROUP_SLUG = "test-group-slug"
GROUP_OTHER_SLUG = "test-group-other-slug"

# STATIC URLS
INDEX_URL = reverse("index")
FOLLOW_INDEX_URL = reverse("follow_index")
# NON STATIC URLS
PROFILE_URL = reverse("profile", kwargs={"username": USER_NAME})
PROFILE_OTHER_URL = reverse("profile", kwargs={"username": USER_NAME_OTHER})
GROUP_URL = reverse("group_posts", kwargs={"slug": GROUP_SLUG})
GROUP_OTHER_URL = reverse("group_posts", kwargs={"slug": GROUP_OTHER_SLUG})
FOLLOW_URL = reverse("profile_follow", args=[USER_NAME])
UNFOLLOW_URL = reverse("profile_unfollow", args=[USER_NAME])


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.group = Group.objects.create(
            title="Заголовок",
            slug=GROUP_SLUG,
        )
        cls.group_other = Group.objects.create(
            title="Заголовок Другой",
            slug=GROUP_OTHER_SLUG,
        )
        uploaded = SimpleUploadedFile(
            "small_views.gif",
            content=(b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'),
            content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Тестовый пост с группой",
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )
        # NON STATIC GENERATED URLS
        cls.POST_URL = reverse("post", args=[USER_NAME, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit", args=[USER_NAME, cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_show_post_in_context(self):
        """Контекст шаблона ссодержит 'post'."""
        urls_with_page = [
            [INDEX_URL, self.guest_client],
            [GROUP_URL, self.guest_client],
            [PROFILE_URL, self.guest_client],
            [self.POST_URL, self.guest_client],
            [self.POST_EDIT_URL, self.authorized_client],
        ]
        for url, client in urls_with_page:
            with self.subTest(value=url):
                response = client.get(url)
                if "page" in response.context:
                    self.assertEqual(len(response.context["page"]), 1)
                    context_post = response.context["page"][0]
                else:
                    context_post = response.context["post"]
                self.assertEqual(self.post, context_post)

    def test_page_show_group_in_context(self):
        """Контекст шаблона ссодержит 'group'."""
        response = self.guest_client.get(GROUP_URL)
        self.assertEqual(self.group, response.context["group"])

    def test_page_group_other_no_posts(self):
        """Пост не попал на страницу группы, для которой он не предназначен."""
        response = self.guest_client.get(GROUP_OTHER_URL)
        self.assertNotIn(self.post, response.context["page"])

    def test_page_show_author_in_context(self):
        """Контекст шаблона ссодержит 'author'."""
        urls = [
            PROFILE_URL,
            self.POST_URL,
        ]
        for url in urls:
            with self.subTest(value=url):
                self.assertEqual(
                    self.guest_client.get(url).context["author"],
                    self.user
                )


class PaginatorPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username=USER_NAME)
        group = Group.objects.create(title="Заголовок", slug=GROUP_SLUG)
        for i in range(0, POSTS_PER_PAGE + 3):
            Post.objects.create(text=f"{i}", author=user, group=group)
        for i in range(POSTS_PER_PAGE + 3, POSTS_PER_PAGE + 7):
            Post.objects.create(text=f"{i}", author=user)
        cls.REST_GROUP_POSTS = 3
        cls.REST_POSTS = 7

    def setUp(self):
        self.guest_client = Client()

    def test_index_first_page_contains_number_of_posts(self):
        """Первая страница по адресу "index" содержит POSTS_PER_PAGE постов."""
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(len(response.context["page"]), POSTS_PER_PAGE)

    def test_index_second_page_contains_rest_posts(self):
        """Вторая страница по адресу "index" содержит остальные посты."""
        response = self.guest_client.get(INDEX_URL + "?page=2")
        self.assertEqual(len(response.context["page"]), self.REST_POSTS)

    def test_group_first_page_contains_number_of_posts(self):
        """Первая страница по адресу группы содержит
        POSTS_PER_PAGE постов группы."""
        response = self.guest_client.get(GROUP_URL)
        self.assertEqual(len(response.context["page"]), POSTS_PER_PAGE)

    def test_group_second_page_contains_rest_posts(self):
        """Вторая страница по адресу группы содержит остальные посты группы."""
        response = self.guest_client.get(GROUP_URL + "?page=2")
        self.assertEqual(len(response.context["page"]), self.REST_GROUP_POSTS)


class FollowsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_bob = User.objects.create_user(username=USER_NAME)
        cls.user_leo = User.objects.create_user(username=USER_NAME_OTHER)
        cls.post_bob = Post.objects.create(
            text="Пост Боба",
            author=cls.user_bob,
        )
        cls.post_leo = Post.objects.create(
            text="Пост Лео",
            author=cls.user_leo,
        )
        # NON STATIC GENERATED URLS
        cls.POST_BOB_URL = reverse("post", args=[USER_NAME, cls.post_bob.id])
        cls.POST_LEO_URL = reverse("post",
                                   args=[USER_NAME_OTHER, cls.post_leo.id])

    def setUp(self):
        self.authorized_client_bob = Client()
        self.authorized_client_bob.force_login(self.user_bob)
        self.authorized_client_leo = Client()
        self.authorized_client_leo.force_login(self.user_leo)

    def test_follow_auth_user_can_follow_other_user(self):
        """Авторизованный пользователь может подписаться
        на другого пользователя и отписаться от него."""
        self.authorized_client_leo.get(FOLLOW_URL)
        self.assertTrue(
            self.user_leo.follower.filter(author=self.user_bob).exists()
        )
        self.authorized_client_leo.get(UNFOLLOW_URL)
        self.assertFalse(
            self.user_leo.follower.filter(author=self.user_bob).exists()
        )

    def test_follow_index_follower_sees_author_posts_in_subs_feed(self):
        """Новый пост пользователя появляется в ленте того,
        кто на него подписан."""
        self.authorized_client_leo.get(FOLLOW_URL)
        response = self.authorized_client_leo.get(FOLLOW_INDEX_URL)
        self.assertIn(self.post_bob, response.context["page"])
        self.authorized_client_leo.get(UNFOLLOW_URL)

    def test_follow_index_non_follower_see_author_no_posts_in_subs_feed(self):
        """Новый пост пользователя не появляется в ленте того,
        кто не подписан на него."""
        self.assertFalse(
            self.user_bob.follower.filter(author=self.user_bob).exists()
        )
        response = self.authorized_client_bob.get(FOLLOW_INDEX_URL)
        self.assertNotIn(self.post_leo, response.context["page"])
