"""TopsNight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from TopsListGenerator import views

urlpatterns = [

    path('', views.home, name="home"),

    path("signup/", views.signupuser, name="signupuser"),
    path('logout/', views.logoutuser, name='logoutuser'),
    path('login/', views.loginuser, name='loginuser'),

    path('FAQs/', views.FAQs, name='FAQs'),
    path('About/', views.about, name='about'),

    path("MyPlaylists/", views.userplaylists, name="userplaylists"),
    path("ImportPlaylist/", views.importplaylist, name="importplaylist"),
    path("EditPlaylist/<int:playlist_pk>',", views.editplaylist, name="editplaylist"),
    path("RemoveGroup/<int:playlist_pk>',", views.removegroupfromplaylist, name="removegroupfromplaylist"),
    path("Playlist/<int:playlist_pk>/delete", views.deleteplaylist, name='deleteplaylist'),
    path("Playlist/<int:playlist_pk>/refresh", views.refreshplaylist, name='refreshplaylist'),

    path("CreateGroup/", views.creategroup, name="creategroup"),
    path("MyGroups/", views.usergroups, name="usergroups"),
    path("AllGroups/", views.allgroups, name="allgroups"),
    path("ViewGroup/<int:group_pk>", views.viewgroup, name="viewgroup"),
    path("EditGroup/<int:group_pk>", views.editgroup, name="editgroup"),
    path("RemovePlaylist/<int:group_pk>',", views.removeplaylistfromgroup, name="removeplaylistfromgroup"),
    path("Group/<int:group_pk>/delete", views.deletegroup, name='deletegroup'),
    path("TopsList/Group/<int:group_pk>/aggregate", views.aggregategroup, name='aggregategroup'),

    path("admin/", admin.site.urls),
]
