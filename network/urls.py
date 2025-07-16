
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new/", views.create_post, name= "new_post"),
    path("profile/<str:username>",views.profile, name= "profile"),

    ## Api routes
    path("follow/", views.follow, name= "follow")

]
