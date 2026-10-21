from django_filters.rest_framework import FilterSet
from .models import Order

class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {"user_id": ["exact"],
                  "created_at": ["gt", "lt"]
                }