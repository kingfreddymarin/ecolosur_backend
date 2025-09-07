from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet, CarouselBannerViewSet, BusinessSettingsViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r'carousel', CarouselBannerViewSet, basename="carousel")
router.register(r'settings', BusinessSettingsViewSet, basename="settings")


urlpatterns = [
    path("", include(router.urls)),
]