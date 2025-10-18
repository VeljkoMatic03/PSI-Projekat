"""
URL configuration for aplikacija project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app_veljko.views import adminpanel, verifyTutor, removeUser, logout_user, public_profile, home
from app_filip.views import homepage, register_user, login_user
from app_luka.views import create_ad, dashboard_student, search_ads, view_ad
urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_panel/', adminpanel, name='adminpanel'),
    path('admin_panel/verify/', verifyTutor, name='verifyTutor'),
    path('admin_panel/remove/', removeUser, name='removeUser'),
    path('', homepage, name='homepage'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', public_profile, name='profile'),
    path('home/<str:tip>', home, name='home'),
    path('create_ad/', create_ad, name='create_ad'),
    path('dashboard_student/', dashboard_student, name='dashboard-student'),
    path('search_ads/', search_ads, name='search_ads'),
    path('view_ad/<int:id>', view_ad, name='view_ad'),
]
