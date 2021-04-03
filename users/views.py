from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView

from .forms import CreationForm, EditForm, ProfileForm
from django.shortcuts import redirect, render


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"


class UserEditView(UpdateView):
    form_class = EditForm
    success_url = reverse_lazy("index")
    template_name = "registration/user_edit.html"

    def get_object(self):
        return self.request.user


@login_required
def profile_create(request):
    if hasattr(request.user, 'profile'):
        return redirect("profile_edit")
    form = ProfileForm(request.POST or None,
                       files=request.FILES or None)
    context = {"form": form}
    if not form.is_valid():
        return render(request, "registration/profile_new.html", context)
    profile = form.save(commit=False)
    profile.user = request.user
    profile.save()
    return redirect("profile", username=request.user.username)


@login_required
def profile_edit(request):
    if not hasattr(request.user, 'profile'):
        return redirect("profile_create")
    form = ProfileForm(request.POST or None,
                       files=request.FILES or None,
                       instance=request.user.profile)
    context = {"form": form, "profile": request.user.profile}
    if not form.is_valid():
        return render(request, "registration/profile_new.html", context)
    form.save()
    return redirect("profile", username=request.user.username)
