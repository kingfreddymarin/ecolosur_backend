from django.db import models
from django.utils.text import slugify


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