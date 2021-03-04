from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        "Заголовок",
        max_length=200,
        help_text="Дайте название группе"
    )
    slug = models.SlugField(
        unique=True,
    )
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        "Текст",
        help_text="Что нового?"
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text="Выберите группу",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="posts/",
        blank=True,
        null=True,
        help_text="Выберите изображение",
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = (
            "-pub_date",
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        "Текст",
        help_text="Напишите комментарий",
    )
    created = models.DateTimeField(
        "Дата публикации комментария",
        auto_now_add=True,
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )
