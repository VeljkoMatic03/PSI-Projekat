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
#Andjela Dimitrijevic, Veljko Matic, Filip Pantic, Luka Zdravic
from django.contrib import admin
from django.urls import path, include
from app_veljko.views import adminpanel, verifyTutor, removeUser, logout_user, public_profile, home, rate
from app_filip.views import homepage, register_user, login_user, reset_password
from app_luka.views import create_ad, dashboard_student, search_ads, view_ad, prekini_saradnju, prihvati_zahtev, odbij_zahtev, posalji_zahtev, download_attachment
from app_andjela.views import dashboard_tutor, create_cv, edit_cv, download_cv, download_tutors_cv, wiki_search
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
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
    path('prekini_saradnju/<int:id>', prekini_saradnju, name='prekini_saradnju'),
    path('prihvati_zahtev/<int:id>', prihvati_zahtev, name='prihvati_zahtev'),
    path('odbij_zahtev/<int:id>', odbij_zahtev, name='odbij_zahtev'),
    path('posalji_zahtev/<int:id>', posalji_zahtev, name='posalji_zahtev'),
    path('download_attachment/<int:id>',download_attachment,name="download_attachment"),
    path('rate/<int:id>', rate, name='rate'),
    path('dashboard_tutor/', dashboard_tutor, name='dashboard-tutor'),
    path('create_cv/', create_cv, name='create_cv'),
    path('edit_cv/', edit_cv, name='edit_cv'),
    path('reset_password/', reset_password, name='reset_password'),
    path('download_cv/', download_cv, name='download_cv'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('download_tutors_cv/<str:username>', download_tutors_cv, name='download_tutors_cv'),
    path("wiki-search/", wiki_search, name="wiki_search"),
]
