from django.contrib import admin

from django.contrib import admin
from .models import Category, Product, ProductImage, Inventory, Unit, CarouselBanner, Sale, BusinessSettings
from .forms import ProductImageForm, CarouselBannerForm

@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ("name", "whatsapp_number", "updated_at")

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

class ProductImageInline(admin.TabularInline):
    form = ProductImageForm
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "tag", "is_primary")


class InventoryInline(admin.StackedInline):
    model = Inventory
    extra = 0
    max_num = 1
    fields = ("sku", "quantity")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at", "icon")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, InventoryInline]

@admin.register(CarouselBanner)
class CarouselBannerAdmin(admin.ModelAdmin):
    form = CarouselBannerForm
    list_display = ("title", "order", "is_active", "created_at")

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "sold_price", "created_at")
    list_filter = ("created_at", "product")

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "sku", "quantity", "updated_at")
    search_fields = ("product__name", "sku")


# Optional: register directly (if you want quick access too)
admin.site.register(ProductImage)
# admin.site.register(Inventory)