from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, CarouselBanner, Sale, BusinessSettings
from .api_serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CarouselBannerSerializer,
    SaleSerializer,
    BusinessSettingsSerializer
)


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.filter(is_active=True).order_by("name")
    serializer_class = CategorySerializer


class ProductViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = (
        Product.objects.filter(is_active=True)
        .select_related("category", "unit")
        .prefetch_related("images")
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
            qs = qs.filter(quantity__gt=0)
        return qs

class CarouselBannerViewSet(viewsets.ModelViewSet):
    queryset = CarouselBanner.objects.filter(is_active=True).order_by("order")
    serializer_class = CarouselBannerSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by("-created_at")
    serializer_class = SaleSerializer


class BusinessSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessSettings.objects.all()
    serializer_class = BusinessSettingsSerializer