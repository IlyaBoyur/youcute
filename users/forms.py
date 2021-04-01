from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelForm


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )


class EditForm(ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
        )
