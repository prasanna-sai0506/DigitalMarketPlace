from django.db.models import Sum,F,DecimalField,ExpressionWrapper
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from digitalmarketplace.pagination import DefaultPagination
from .filters import OrderFilter
from .tasks import send_order_confirmation
from .models import Order, OrderItem
from .serializers import CreateOrderSerializer,OrderSerializer,UpdateOrderSerializer


# Common functionality for order views
class OrderBaseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        queryset = (Order.objects.select_related("user").prefetch_related("items__asset"))
        if user.is_staff:
            return queryset
        return queryset.filter(user=user)


# List orders and create purchases
class OrderListCreateAPIView(OrderBaseAPIView):
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ["user__username","user__email","items__asset__title"]
    ordering_fields = ["created_at", "updated_at"]

    def filter_queryset(self, queryset):
        for backend_class in self.filter_backends:
            queryset = backend_class().filter_queryset(self.request, queryset,self)
        return queryset

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset,request,view=self)
        serializer = OrderSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data,context={"user_id": request.user.id},)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        send_order_confirmation.delay(order.id)   #  for Sending confirmation email asynchronously
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data,status=status.HTTP_201_CREATED)


# Retrieve, update, or delete a particular order
class OrderDetailAPIView(OrderBaseAPIView):

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        # Only administrators may update orders
        self.check_permissions(request)
        if not request.user.is_staff:
            return Response({"detail": "Administrator permission required."},status=status.HTTP_403_FORBIDDEN,)
        order = self.get_object(pk)
        serializer = UpdateOrderSerializer(order,data=request.data,partial=True,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        # Only administrators may delete orders
        if not request.user.is_staff:
            return Response({"detail": "Administrator permission required."},status=status.HTTP_403_FORBIDDEN,)
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT,)

# Administrator order reports
class OrderReportAPIView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        revenue = OrderItem.objects.aggregate(
            total_revenue=Sum(
                ExpressionWrapper(
                    F("unit_price") * F("quantity"),\
                    output_field=DecimalField(\
                        max_digits=12,\
                        decimal_places=2,\
                    ),
                )
            )
        )
        purchases = (
            OrderItem.objects.values("asset_id", "asset__title")
            .annotate(
                purchase_count=Sum("quantity"), \
                revenue=Sum(\
                    ExpressionWrapper(\
                        F("unit_price") * F("quantity"),\
                        output_field=DecimalField(\
                            max_digits=12,\
                            decimal_places=2,\
                        ),
                    )
                ),
            ).order_by("-purchase_count"))
        return Response(
            {
                "total_revenue": revenue["total_revenue"] or 0,
                "assets": list(purchases),
            },status=status.HTTP_200_OK,)