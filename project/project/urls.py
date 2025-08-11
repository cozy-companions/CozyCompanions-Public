"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from user import views as user_view
from django.contrib.auth import views as auth
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls'), name='index'),
    path('login/', user_view.Login, name = 'Login'),
    path('logout/', auth.LogoutView.as_view(template_name = 'landing.html'), name = 'logout'),
    path('register/', user_view.register, name='register'),
    path('profile-creation/', user_view.profile_creation, name='profile-creation'),
    path('tracking/', include("tracking.urls"), name="tracking"),
    path('companions/', include("creatures.urls"), name="companions"),
    path('wiki/', user_view.wiki, name='wiki'),
    path('all-companions/', user_view.all_creatures, name="all_companions"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

