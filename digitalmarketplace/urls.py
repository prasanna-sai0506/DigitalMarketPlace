from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
import profiles.urls
from profiles.views import UserLoginAPIView
import debug_toolbar
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/login/",UserLoginAPIView.as_view(),name = "login"),
    path("auth/token/refresh/",TokenRefreshView.as_view(),name="token_refresh"),
    path("userspace/", include(profiles.urls)),
    path("marketplace/", include("assets.urls")),
    path("marketplace/", include("orders.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

