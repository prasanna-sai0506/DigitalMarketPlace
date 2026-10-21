from django.urls import path
from .views import OrderListCreateAPIView,OrderDetailAPIView,OrderReportAPIView

urlpatterns = [
    path("orders/", OrderListCreateAPIView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("orders/reports/", OrderReportAPIView.as_view(), name="order-reports")
]
