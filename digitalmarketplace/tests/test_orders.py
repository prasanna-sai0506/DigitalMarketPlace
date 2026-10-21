import pytest
from rest_framework import status
from model_bakery import baker
from profiles.models import User
from assets.models import Asset

@pytest.fixture
def create_order(api_client):
    def do_create_order(order):
        return api_client.post("/marketplace/orders/",order,format="json")
    return do_create_order

@pytest.mark.django_db
class TestCreateOrder:
    def test_if_user_is_anonymous_returns_401(self,create_order):
        # Arrange

        # Act
        response = create_order({
            "items": [
                {
                    "asset": 1,
                    "quantity": 1
                }
            ]
        })
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_student_creates_order_returns_201(self,authenticate,create_order):
        # Arrange
        instructor = baker.make(User,role=User.INSTRUCTOR)
        asset = baker.make(Asset,instructor=instructor,status=Asset.PUBLISHED,inventory=10,price=999)
        authenticate(role=User.STUDENT)

        # Act
        response = create_order({
            "items": [
                {
                    "asset": asset.id,
                    "quantity": 1
                }
            ]
        })

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0
        
    def test_successful_order_decrements_inventory(self,authenticate,create_order):
        # Arrange
        instructor = baker.make(User,role=User.INSTRUCTOR)
        asset = baker.make(Asset,instructor=instructor,status=Asset.PUBLISHED,inventory=10,price=999)
        authenticate(role=User.STUDENT)
        # Act
        response = create_order({
            "items": [
                {
                    "asset": asset.id,
                    "quantity": 2
                }
            ]
        })
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        asset.refresh_from_db()
        assert asset.inventory == 8