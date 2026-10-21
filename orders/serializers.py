from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from assets.models import Asset
from profiles.models import User
from .models import Order, OrderItem


class SimpleAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["id","title","price"]

class OrderItemSerializer(serializers.ModelSerializer):
    asset = SimpleAssetSerializer()
    class Meta:
        model = OrderItem
        fields = ["id","asset","unit_price","quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ["id","user","created_at","updated_at","items"]

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = []

class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    def validate_items(self, items):
        for item in items:
            
            if "asset" not in item:
                raise serializers.ValidationError("Each order item must contain an asset ID.")

            if "quantity" not in item:
                raise serializers.ValidationError("Each order item must contain a quantity.")

            try:
                asset_id = int(item["asset"])
                quantity = int(item["quantity"])
            except (ValueError, TypeError):
                raise serializers.ValidationError("Asset ID and quantity must be valid integers.")
            
            if quantity <= 0:
                raise serializers.ValidationError("Quantity must be greater than 0.")

            if not Asset.objects.filter(pk=asset_id).exists():
                raise serializers.ValidationError(f"No asset with ID {asset_id} was found.")
        return items

    def save(self, **kwargs):
        user_id = self.context["user_id"]
        with transaction.atomic():
            user = User.objects.get(pk=user_id)
            order = Order.objects.create(user=user)
            order_items = []
            for item in self.validated_data["items"]:
                asset_id = int(item["asset"])
                quantity = int(item["quantity"])
                asset = Asset.objects.select_for_update().get(pk=asset_id)
                if asset.status != Asset.PUBLISHED:
                    raise serializers.ValidationError(
                        f"Asset '{asset.title}' is not published."
                    )
                if asset.inventory < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient inventory for '{asset.title}'. "
                        f"Available: {asset.inventory}."
                    )
                Asset.objects.filter(pk=asset.pk).update(inventory=F("inventory") - quantity)
                order_items.append(
                    OrderItem(
                        order=order,\
                        asset=asset,\
                        unit_price=asset.price,\
                        quantity=quantity\
                    )
                )
            OrderItem.objects.bulk_create(order_items)
            return order