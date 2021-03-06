from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from yatube.settings import LOGIN_URL


USER_NAME = "TestUser"
USER_NAME_OTHER = "TestUserOther"
GROUP_SLUG = "test-group-slug"

# STATIC URLS
INDEX_URL = reverse("index")
NEW_POST_URL = reverse("new_post")
# NON STATIC URLS
PROFILE_URL = reverse("profile", kwargs={"username": USER_NAME})
GROUP_URL = reverse("group_posts", kwargs={"slug": GROUP_SLUG})
UNKNOWN_URL = "/url_does_not_exist/"


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)
        cls.user_other = User.objects.create_user(username=USER_NAME_OTHER)
        Group.objects.create(
            title="Test Group",
            slug=GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )
        # NON STATIC GENERATED URLS
        cls.POST_URL = reverse("post", args=[USER_NAME, cls.post.id])
        cls.POST_EDIT_URL = reverse("post_edit", args=[USER_NAME, cls.post.id])
        cls.POST_COMMENT_URL = reverse("add_comment",
                                       args=[USER_NAME, cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.user_other)

    def test_posts_url_exists_at_desired_location(self):
        """Страницы возвращают ожидаемый код ответа
        соответствующему клиенту."""
        urls = [
            [INDEX_URL, self.guest_client, 200],
            [NEW_POST_URL, self.guest_client, 302],
            [NEW_POST_URL, self.authorized_client_other, 200],
            [PROFILE_URL, self.guest_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.authorized_client_other, 302],
            [self.POST_EDIT_URL, self.authorized_client, 200],
            [UNKNOWN_URL, self.guest_client, 404],
        ]
        for url, client, response_code in urls:
            with self.subTest(value=url):
                self.assertEqual(client.get(url).status_code, response_code)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий ему html-шаблон,
        если у пользователя есть права на просмотр страниц по данным URL."""
        url_templates = [
            [INDEX_URL, self.guest_client, "index.html"],
            [NEW_POST_URL, self.authorized_client_other, "new_post.html"],
            [PROFILE_URL, self.guest_client, "profile.html"],
            [GROUP_URL, self.guest_client, "group.html"],
            [self.POST_URL, self.guest_client, "post.html"],
            [self.POST_EDIT_URL, self.authorized_client, "new_post.html"],
            [UNKNOWN_URL, self.guest_client, "misc/404.html"],
        ]
        for url, client, template in url_templates:
            with self.subTest(value=url):
                self.assertTemplateUsed(client.get(url), template)

    def test_posts_url_redirects_client_to_url(self):
        """Страница перенаправляет пользователя на соответствующий URL."""
        urls = [
            [
                NEW_POST_URL,
                self.guest_client,
                f"{LOGIN_URL}?next={NEW_POST_URL}"
            ],
            [
                self.POST_EDIT_URL,
                self.guest_client,
                f"{LOGIN_URL}?next={self.POST_EDIT_URL}"
            ],
            [
                self.POST_EDIT_URL,
                self.authorized_client_other,
                self.POST_URL
            ],
            [
                self.POST_COMMENT_URL,
                self.guest_client,
                f"{LOGIN_URL}?next={self.POST_COMMENT_URL}"
            ],
        ]
        for url, client, target_url in urls:
            with self.subTest(value=url):
                self.assertRedirects(client.get(url, follow=True), target_url)
