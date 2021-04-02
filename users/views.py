from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView

from .forms import CreationForm, EditForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"


class  UserEditView(UpdateView):
    form_class = EditForm
    success_url = reverse_lazy("index")
    template_name = "registration/user_edit.html"

    def get_object(self):
        return self.request.user
