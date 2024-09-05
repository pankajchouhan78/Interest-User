from django.urls import path
from .API.api import (
    RegisterView,
    LoginView,
    UsersList,
    SentRequestView,
    AcceptInterestView,
    RejectInterestView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("userslist/", UsersList.as_view()),
    path("sentinterest/", SentRequestView.as_view()),
    path("acceptinterest/", AcceptInterestView.as_view()),
    path("rejectinterest/", RejectInterestView.as_view()),
]
