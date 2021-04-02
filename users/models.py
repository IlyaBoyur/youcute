from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        "Аватар",
        upload_to="profiles/",
        blank=True,
        null=True,
        help_text="Загрузите фотографию",
    )
    bio = models.TextField(
        "Об авторе",
        blank=True,
        help_text="Расскажите о себе",
    )

    def __str__(self):
        return str(self.user)
