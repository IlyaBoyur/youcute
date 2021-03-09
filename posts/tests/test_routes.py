from django.test.testcases import TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostsRoutesTests(TestCase):
    def test_routes(self):
        """URL-адрес, рассчитанный через name,
        соответствует ожидаемому видимому URL."""
        user = User.objects.create_user(username="TestUser")
        GROUP_SLUG = "test-group-slug"
        post = Post.objects.create(
            author=user,
            text="Тестовый пост",
        )
        routes = {
            # Static URLs
            "/": reverse("index"),
            "/new/": reverse("new_post"),
            "/follow/": reverse("follow_index"),
            # Non static URLs
            f"/{user.username}/": reverse("profile", args=[user.username]),
            f"/group/{GROUP_SLUG}/": reverse("group_posts", args=[GROUP_SLUG]),
            f"/{user.username}/follow/": reverse(
                "profile_follow",
                args=[user.username],
            ),
            f"/{user.username}/unfollow/": reverse(
                "profile_unfollow",
                args=[user.username],
            ),
            # Non static generated URLs
            f"/{user.username}/{post.id}/": reverse(
                "post",
                args=[user.username, post.id],
            ),
            f"/{user.username}/{post.id}/edit/": reverse(
                "post_edit",
                args=[user.username, post.id],
            ),
            f"/{user.username}/{post.id}/comment/": reverse(
                "add_comment",
                args=[user.username, post.id],
            ),
        }
        for url, reversed_url in routes.items():
            self.assertEqual(url, reversed_url)
