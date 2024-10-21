from django.core.management.base import BaseCommand

from product.factories import ProductFactory

from product.factories import ProductImageFactory


class Command(BaseCommand):
    help = 'Create 20 fake products with images'

    def handle(self, *args, **kwargs):
        for _ in range(20):
            product = ProductFactory.create()
            ProductImageFactory.create(product=product)

        self.stdout.write(self.style.SUCCESS('Successfully created 20 fake products with images!'))