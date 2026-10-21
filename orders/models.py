from django.db import models
from profiles.models import User
from assets.models import Asset


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
class OrderItem(models.Model):
    
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    asset = models.ForeignKey(Asset,on_delete=models.PROTECT,related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.order} - {self.asset.title}"