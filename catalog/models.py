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

    quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.unit})"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.URLField(blank=True)
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


class Inventory(models.Model):
    sku = models.CharField(max_length=10, unique=True, blank=True)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="inventory_movements")
    quantity = models.IntegerField(default=0)  # positive for restock, could allow negative for adjustment
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # detect if this is a new movement
        if not self.sku:
            last_item = Inventory.objects.order_by('-sku').first()
            if last_item and last_item.sku.startswith("P"):
                last_number = int(last_item.sku[1:])
                new_number = last_number + 1
            else:
                new_number = 0
            self.sku = f"P{new_number:03d}"

        super().save(*args, **kwargs)

        # Only adjust product stock when this is a new record
        if is_new:
            self.product.quantity += self.quantity
            self.product.save()

class CarouselBanner(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True)
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
    sold_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.quantity > self.product.quantity:
            raise ValidationError(
                f"Not enough stock: only {self.product.quantity} left."
            )

    def save(self, *args, **kwargs):
        self.clean()
        self.product.quantity -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.quantity} x {self.product.name} at {self.sold_price}"