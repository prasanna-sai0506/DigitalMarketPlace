from django_filters.rest_framework import FilterSet
from .models import Asset

class AssetFilter(FilterSet):
    class Meta:
        model = Asset
        fields = {
            "status": ["exact"],
            "price": ["gt", "lt"],
            "inventory": ["gt", "lt"]
        }