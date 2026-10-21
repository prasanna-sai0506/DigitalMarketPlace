import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from profiles.models import User


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticate(api_client):
    def do_authenticate(role=User.STUDENT,is_staff=False):
        user = baker.make(User,role=role,is_staff=is_staff)
        api_client.force_authenticate(user=user)
        return user
    return do_authenticate