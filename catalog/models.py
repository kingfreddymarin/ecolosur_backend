from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class BusinessSettings(models.Model):
    name = models.CharField(max_length=255, default="Ecolo-Sur Market 🌱")
    whatsapp_number = models.CharField(
        max_length=20,
        help_text="Include country code, e.g., 50585723217"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Business Setting"
        verbose_name_plural = "Business Settings"

    def __str__(self):
        return self.name


class TimeStampedModel(models.Model):
    """Abstract base with created/updated fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Emoji or short text icon for frontend display"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Unit(TimeStampedModel):
    """Unidad de venta (ej: 4 onz, Docena, kg)."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey("Category", related_name="products", on_delete=models.CASCADE)
    unit = models.ForeignKey("Unit", related_name="products", on_delete=models.PROTECT)  # 👈 NEW FK

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.unit})"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=160, blank=True)
    tag = models.CharField(
        max_length=20, blank=True,
        help_text="front / back / side / etc."
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "id"]

    def __str__(self):
        return f"{self.product.name} ({self.tag or 'image'})"


class Inventory(TimeStampedModel):
    product = models.OneToOneField(Product, related_name="inventory", on_delete=models.CASCADE)
    sku = models.CharField(max_length=64, unique=True)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.sku} • {self.quantity}"

class CarouselBanner(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="carousel/", blank=False, null=False)
    link = models.URLField(blank=True, null=True, help_text="Optional link when clicking the banner")
    order = models.PositiveIntegerField(default=0, help_text="Sorting order in carousel")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title if self.title else f"Banner {self.id}"

class Sale(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="sales")
    quantity = models.PositiveIntegerField(default=1)
    sold_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Sold price per unit"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not hasattr(self.product, "inventory"):
            raise ValidationError(f"Product {self.product.name} has no inventory record")
        if self.quantity > self.product.inventory.quantity:
            raise ValidationError(
                f"Not enough stock: only {self.product.inventory.quantity} left."
            )

    def save(self, *args, **kwargs):
        self.clean()
        # Ensure product has inventory
        if not hasattr(self.product, "inventory"):
            raise ValueError(f"Product {self.product.name} has no inventory record")

        if self.product.inventory.quantity >= self.quantity:
            self.product.inventory.quantity -= self.quantity
            self.product.inventory.save()
        else:
            raise ValueError("Not enough stock available for this sale")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.quantity} x {self.product.name} at {self.sold_price}"