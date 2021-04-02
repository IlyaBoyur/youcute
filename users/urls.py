from django.urls import path

from . import views


urlpatterns = [
    path("signup/",
         views.SignUp.as_view(),
         name="signup"),
    path("user_edit/",
         views.UserEditView.as_view(),
         name="user_edit"),
]
