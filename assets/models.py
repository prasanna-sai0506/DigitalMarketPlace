from django.db import models
from profiles.models import User

class AssetManager(models.Manager):
    def published(self):
        return self.filter(status=Asset.PUBLISHED)

class Asset(models.Model):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default=DRAFT)
    banner = models.ImageField(upload_to="assets/banners/",blank=True,null=True)
    file = models.FileField(upload_to="assets/files/",blank=True,null=True)
    instructor = models.ForeignKey(User,on_delete=models.CASCADE,related_name="assets")
    inventory = models.PositiveIntegerField(default=0)
    objects = AssetManager()

    def __str__(self):
        return self.title