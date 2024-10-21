from rest_framework import serializers

from .models import Product, Category, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_type']


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'base_price', 'weight', 'images', 'available', 'category', 'coffee_type', 'created_at']

    def get_category(self, obj):
        return obj.category.name


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'coffee_type',
            'weight',
            'variety',
            'flavor_notes',
            'origin',
            'brewing_method',
            'body',
            'sweetness',
            'bitterness',
            'packaging_color',
            'roast_level',
            'base_price',
            'stock',
            'available',
            'category',
            'tags',
            'created_at',
            'images',
        ]
