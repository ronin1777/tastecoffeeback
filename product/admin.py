from django.contrib import admin
from .models import Category, Product, ProductImage



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_type', 'image')

    def has_add_permission(self, request, obj=None):
        if obj:
            # بررسی تعداد تصاویر موجود از هر نوع
            existing_primary = obj.images.filter(image_type=ProductImage.PRIMARY).exists()
            existing_secondary = obj.images.filter(image_type=ProductImage.SECONDARY).exists()
            existing_tertiary = obj.images.filter(image_type=ProductImage.TERTIARY).exists()

            # اجازه اضافه کردن تصاویر جدید را بر اساس نوع آن‌ها می‌دهد
            if not existing_primary or not existing_secondary or not existing_tertiary:
                return True
            return False
        return True  # اجازه برای محصولات جدید


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'coffee_type', 'weight', 'base_price', 'stock', 'category', 'created_at', 'updated_at', 'available'
    )
    list_filter = ('coffee_type', 'weight', 'category', 'created_at')
    search_fields = ('name', 'variety', 'tags', 'origin')
    ordering = ('-created_at',)
    inlines = [ProductImageInline]  # اضافه کردن کلاس Inline به ProductAdmin

    def available(self, obj):
        return obj.available
    available.boolean = True

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_type', 'image')
    list_filter = ('image_type',)
    search_fields = ('product__name',)
    ordering = ('product',)


