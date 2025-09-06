from rest_framework import serializers
from .models import Category, Product, ProductImage, Unit, CarouselBanner


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "name")


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("id", "tag", "is_primary", "alt_text", "image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()  # 👈 new

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "price",
            "unit",
            "category",
            "primary_image",
            "in_stock",
            "availability",
        )

    def get_primary_image(self, obj):
        img = obj.images.order_by("-is_primary", "id").first()
        return ProductImageSerializer(img, context=self.context).data if img else None

    def get_in_stock(self, obj):
        inv = getattr(obj, "inventory", None)
        return bool(inv and inv.quantity > 0)

    def get_availability(self, obj):
        inv = getattr(obj, "inventory", None)
        return inv.quantity if inv else 0


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ("description", "images")

class CarouselBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarouselBanner
        fields = ["id", "title", "description", "image", "link", "order", "is_active"]