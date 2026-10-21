from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from assets.filter import AssetFilter
from digitalmarketplace.pagination import DefaultPagination
from digitalmarketplace.permissions import IsInstructorOrReadOnly
from .models import Asset
from .serializers import AssetSerializer

class AssetListCreateAPIView(APIView):
    permission_classes = [IsInstructorOrReadOnly]
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = AssetFilter
    search_fields = ["title", "description"]
    ordering_fields = ["price", "title", "inventory"]
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:   #admin can view all the assets  
            return Asset.objects.select_related("instructor").all()
        if user.is_authenticated and user.role == "INSTRUCTOR":     # instructors can view the assets which are only published by them.
            return Asset.objects.select_related("instructor").filter(instructor=user)
        return Asset.objects.select_related("instructor").filter(status=Asset.PUBLISHED) # if you logged in as the student you can only view the published assets

    def filter_queryset(self, queryset):
        for backend_class in self.filter_backends:
            backend = backend_class()
            queryset = backend.filter_queryset(self.request,queryset,self)
        return queryset

    def get(self, request):
        # Cache only anonymous users' public asset lists.
        cache_key = None
        if not request.user.is_authenticated:
            cache_key = f"public_assets:{request.get_full_path()}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset,request,view=self,)
        serializer = AssetSerializer(page, many=True)
        response = paginator.get_paginated_response(serializer.data)

        if cache_key is not None:
            cache.set(cache_key, response.data, 60)
        return response

    def post(self, request):
        serializer = AssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(instructor=request.user)
        return Response(serializer.data,status=status.HTTP_201_CREATED)


class AssetDetailAPIView(APIView):
    permission_classes = [IsInstructorOrReadOnly]
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Asset.objects.select_related("instructor").all()
        if user.is_authenticated and user.role == "INSTRUCTOR":
            return Asset.objects.select_related("instructor").filter(instructor=user)
        return Asset.objects.select_related("instructor").filter(status=Asset.PUBLISHED)

    def get_object(self, pk):
        asset = get_object_or_404(self.get_queryset(), pk=pk)
        self.check_object_permissions(self.request, asset)
        return asset

    def get(self, request, pk):
        asset = self.get_object(pk)
        serializer = AssetSerializer(asset)

        return Response(serializer.data)

    def put(self, request, pk):
        asset = self.get_object(pk)

        serializer = AssetSerializer(
            asset,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, pk):
        asset = self.get_object(pk)

        serializer = AssetSerializer(
            asset,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        asset = self.get_object(pk)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
