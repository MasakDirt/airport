from django.urls import path

from user.views import CreateUserView, CreateTokenView, ManageUserView

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user-register"),
    path("login/", CreateTokenView.as_view(), name="user-login"),
    path("me/", ManageUserView.as_view(), name="user-detail")
]
