from django.contrib import admin

from django.contrib import admin
from .models import Category, Product, ProductImage, Inventory, Unit, CarouselBanner

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1   # show one empty slot by default
    fields = ("image", "alt_text", "tag", "is_primary")


class InventoryInline(admin.StackedInline):
    model = Inventory
    extra = 0
    max_num = 1
    fields = ("sku", "quantity")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
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
    list_display = ("title", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")


# Optional: register directly (if you want quick access too)
admin.site.register(ProductImage)
admin.site.register(Inventory)