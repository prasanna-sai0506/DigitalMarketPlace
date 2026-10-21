import pytest
from rest_framework import status
from model_bakery import baker
from profiles.models import User
from assets.models import Asset

@pytest.fixture
def create_asset(api_client):
    def do_create_asset(asset):
        return api_client.post("/marketplace/assets/",asset,format="json")
    return do_create_asset


@pytest.mark.django_db
class TestCreateAsset:
    def test_if_user_is_anonymous_returns_401(self, create_asset):
        # Arrange

        # Act
        response = create_asset({"title": "Python Course","description": "Python programming","price": 999,"inventory": 10})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_student_returns_403(self,authenticate,create_asset):
        # Arrange
        authenticate(role=User.STUDENT)

        # Act
        response = create_asset({
            "title": "Python Course",
            "description": "Python programming",
            "price": 999,
            "inventory": 10
        })

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self,authenticate,create_asset):
        # Arrange
        authenticate(role=User.INSTRUCTOR)

        # Act
        response = create_asset({"title": "Python Course","description": "Python programming","price": 0,"inventory": 10})

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["price"] is not None

    def test_if_data_is_valid_returns_201(self,authenticate,create_asset):
        # Arrange
        instructor = authenticate(role=User.INSTRUCTOR)

        # Act
        response = create_asset({"title": "Python Course","description": "Python programming","price": 999,"inventory": 10})

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0
        assert response.data["instructor"] == instructor.id
        
@pytest.mark.django_db
class TestRetrieveAsset:

    def test_if_asset_exists_returns_200(self, api_client):
        # Arrange
        instructor = baker.make(User,role=User.INSTRUCTOR)

        asset = baker.make(Asset,instructor=instructor,status=Asset.PUBLISHED)

        # Act
        response = api_client.get(f"/marketplace/assets/{asset.id}/")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == asset.id
        assert response.data["title"] == asset.title