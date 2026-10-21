from django.contrib import admin
from .models import Asset
    
@admin.action(description="Publish selected assets")
def publish_assets(modeladmin, request, queryset):
    queryset.update(status=Asset.PUBLISHED)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["id","title","price","status","instructor","inventory"]
    list_filter = [ "status","instructor",]
    search_fields = ["title","description",]
    actions = [publish_assets]