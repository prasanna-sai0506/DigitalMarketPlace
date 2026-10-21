import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

from profiles.models import Profile, User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestUserProfileAPIView:
    def test_admin_can_view_any_user_profile(self, api_client):
        admin = baker.make(User, is_staff=True)
        user = baker.make(User)
        profile = baker.make(Profile, user=user, bio="User bio")
        api_client.force_authenticate(user=admin)

        response = api_client.get(
            reverse("user-profile", kwargs={"pk": user.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == profile.id
        assert response.data["user"] == user.id
        assert response.data["bio"] == "User bio"

    def test_regular_user_cannot_view_another_users_profile(self, api_client):
        authenticated_user = baker.make(User)
        other_user = baker.make(User)
        baker.make(Profile, user=other_user)
        api_client.force_authenticate(user=authenticated_user)

        response = api_client.get(
            reverse("user-profile", kwargs={"pk": other_user.pk})
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
