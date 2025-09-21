from rest_framework import serializers
from .models import Category, Product, ProductImage, Unit, CarouselBanner, Sale, BusinessSettings


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "icon")


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "name")


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "tag", "is_primary", "alt_text", "image")  # now just returns the URL


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

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


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ["id", "product", "quantity", "sold_price", "created_at"]

    def validate(self, data):
        product = data["product"]
        quantity = data["quantity"]
        if not hasattr(product, "inventory"):
            raise serializers.ValidationError("This product has no inventory record.")
        if quantity > product.inventory.quantity:
            raise serializers.ValidationError(
                f"Not enough stock: only {product.inventory.quantity} left."
            )
        return data


class BusinessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSettings
        fields = ["id", "name", "whatsapp_number"]