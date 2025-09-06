from django.core.management.base import BaseCommand
from catalog.models import Category, Product, Inventory, ProductImage, Unit
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Seed ECOLO SUR categories and products (use --flush to replace all data)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all products, categories, inventory and images before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("⚠️ Flushing existing catalog..."))
            ProductImage.objects.all().delete()
            Inventory.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

        # Define categories (based on your real product list)
        categories_data = {
            "Hierbas": [
                "Albahaca", "Cebollin", "Culantro", "Curcuma", "Espinaca hoja gd",
                "Espinaca hoja pq", "Estragon", "Mostaza roja", "Oregano hoja Gd",
                "Perejil Italiano", "Zacate limon", "Insulina"
            ],
            "Frutas": [
                "Aguacate", "Calala", "Granadilla", "Guineo cuadrado", "Limon Criollo",
                "Limon Tahiti", "Mora Fresca", "Nonni", "Pitaya pequeña/grande", "Platano verde", "Platano maduro"
            ],
            "Tubérculos y raíces": [
                "Jengibre", "Nopal", "Frijol Camague", "Chilotes"
            ],
            "Procesados": [
                "Chutney de mango", "Mermelada de mora", "Mermelada de limon"
            ],
            "Plantas y otros": [
                "Aloe vera (gel)", "Aloe vera (Planta)"
            ],
        }

        # Create categories
        categories = {}
        for name in categories_data.keys():
            cat, _ = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "description": f"Productos de la categoría {name}",
                    "is_active": True,
                },
            )
            categories[name] = cat

        # Product list from your table (name, unit, quantity, price, category)
        products_data = [
            ("Albahaca", "4 onz", 8, 35, "Hierbas"),
            ("Aguacate", "peq", 12, 15, "Frutas"),
            ("Aloe vera (gel)", "8 onz", 20, 50, "Plantas y otros"),
            ("Aloe vera (Planta)", "en bolsa", 10, 45, "Plantas y otros"),
            ("Calala", "Docena", 10, 35, "Frutas"),
            ("Cebollin", "Docena", 10, 30, "Hierbas"),
            ("Chilotes", "Docena", 2, 40, "Tubérculos y raíces"),
            ("Chutney de mango", "8 onz", 3, 135, "Procesados"),
            ("Culantro", "4 onz", 4, 30, "Hierbas"),
            ("Curcuma", "4 onz", 2, 40, "Hierbas"),
            ("Espinaca hoja gd", "4 onz", 4, 55, "Hierbas"),
            ("Espinaca hoja pq", "8 onz", 1, 60, "Hierbas"),
            ("Estragon", "4 onz", 8, 55, "Hierbas"),
            ("Frijol Camague", "lb", 10, 40, "Tubérculos y raíces"),
            ("Granadilla", "Unidad", 2, 75, "Frutas"),
            ("Guineo cuadrado", "Docena", 6, 25, "Frutas"),
            ("Insulina", "4 onz", 10, 40, "Hierbas"),
            ("Jengibre", "8 onz", 10, 35, "Tubérculos y raíces"),
            ("Limon Criollo", "Docena", 3, 30, "Frutas"),
            ("Limon Tahiti", "Docena", 2, 60, "Frutas"),
            ("Mermelada de mora", "8 onz", 2, 125, "Procesados"),
            ("Mermelada de limon", "8 onz", 2, 125, "Procesados"),
            ("Mora Fresca", "12 onz", 5, 125, "Frutas"),
            ("Mostaza roja", "8 onz", 5, 40, "Hierbas"),
            ("Nonni", "Docena", 5, 45, "Frutas"),
            ("Nopal", "Docena", 5, 30, "Tubérculos y raíces"),
            ("Oregano hoja Gd", "lb", 5, 100, "Hierbas"),
            ("Perejil Italiano", "4 onz", 8, 40, "Hierbas"),
            ("Pitaya pequeña/grande", "Unidad", 2, 30, "Frutas"),
            ("Platano verde", "Docena", 2, 85, "Frutas"),
            ("Platano maduro", "Docena", 2, 85, "Frutas"),
            ("Zacate limon", "4 onz", 5, 30, "Hierbas"),
        ]

        for idx, (name, unidad, dispo, precio, cat_name) in enumerate(products_data, start=1):
            category = categories[cat_name]
            # ensure Unit exists or get it
            unit_obj, _ = Unit.objects.get_or_create(name=unidad)

            product, _ = Product.objects.update_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "category": category,
                    "unit": unit_obj,  # ✅ now a Unit instance
                    "description": f"{name} orgánico ({unidad})",
                    "price": precio,
                    "is_active": True,
                },
            )
            Inventory.objects.update_or_create(
                product=product,
                defaults={
                    "sku": f"P{idx:03d}",
                    "quantity": dispo,
                },
            )

        self.stdout.write(self.style.SUCCESS("✅ ECOLO SUR products seeded successfully!"))