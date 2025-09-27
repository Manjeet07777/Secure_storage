from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("upload/", views.upload_file_view, name="upload"),
    path("download/<int:file_id>/", views.download_file_view, name="download"),
    path("history/", views.history_view, name="history"),
    path("delete/<int:file_id>/", views.delete_file_view, name="delete"),

]
