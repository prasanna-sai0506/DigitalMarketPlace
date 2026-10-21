from rest_framework import serializers
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["id","title","description","price","status","banner","file","instructor","inventory"]
        read_only_fields = ["id", "instructor"]

    def validate_price(self, value):
        if value <= 0 :
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_inventory(self, value):
        if value <= 0:
            raise serializers.ValidationError("Inventory cannot be negative.")
        return value
    
    def validate_banner(self, value):
        if value is None:
            return value
        max_size = 2 * 1024 * 1024  # supports only maximum size of 2MB
        if value.size > max_size:
            raise serializers.ValidationError("Banner image size must not exceed 2 MB.")
        return value