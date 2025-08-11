from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.view_profile, name="profile"),
    path("profile/delete-account/", views.delete_account, name="delete-account"),
    path("profile/update/", views.profile_update, name="profile-update"),
]
