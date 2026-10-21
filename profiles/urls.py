from django.urls import path
from .views import (
    RegistrationAPIView,
    UserListCreateAPIView,
    UserDetailAPIView,
    CurrentUserAPIView,
    CurrentProfileAPIView,
    UserProfileAPIView,
)

urlpatterns = [
    # Register a user with POST; list users with GET (admin only)
    path("users/", UserListCreateAPIView.as_view(), name="user-list"),

    # Register a new user
    path("users/register/", RegistrationAPIView.as_view(), name="user-register"),

    path("users/me/", CurrentUserAPIView.as_view(), name="user-me"),
    path("users/me/profile/", CurrentProfileAPIView.as_view(), name="profile-me"),
    path("users/<int:pk>/profile/", UserProfileAPIView.as_view(), name="user-profile"),
    # Manage a specific user (admin only)
    path("users/<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
]