from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .api_serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.filter(is_active=True).order_by("name")
    serializer_class = CategorySerializer


class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("images", "inventory")
        .order_by("-updated_at")
    )
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "description"]
    filterset_fields = {"category__slug": ["exact"]}

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == "retrieve" else ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        in_stock = self.request.query_params.get("in_stock")
        if in_stock in ("1", "true", "True"):
            qs = qs.filter(inventory__quantity__gt=0)
        return qs