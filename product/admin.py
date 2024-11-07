from django.contrib import admin
from .models import Category, Product, ProductImage, ProductWeight

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # تعداد عکس‌های اضافی برای بارگذاری
    fields = ('image', 'image_type')  # فیلدهایی که نمایش داده می‌شوند
    max_num = 3  # حداکثر تعداد عکس‌ها


class ProductWeightInline(admin.TabularInline):
    model = ProductWeight
    extra = 1  # تعداد رکوردهای اضافی برای وارد کردن وزن
    fields = ('weight', 'price')  # فیلدهایی که نمایش داده می‌شوند
    max_num = 5  # حداکثر تعداد وزن‌ها (می‌توانید این مقدار را تغییر دهید)
    
    def get_queryset(self, request):
        # برای اطمینان از اینکه فقط وزن‌های مربوط به این محصول نمایش داده شوند
        return super().get_queryset(request)
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'coffee_type','stock', 'available')
    search_fields = ('name', 'description', 'coffee_type')
    list_filter = ('coffee_type', 'category')
    inlines = [ProductImageInline, ProductWeightInline]  # اضافه کردن Inline برای وزن‌ها
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            if formset.model == ProductImage:
                formset.save()



class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields = ('name',)
#     list_filter = ('name',)
#     ordering = ('name',)


# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1
#     fields = ('image_type', 'image')



# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = (
#         'name', 'coffee_type', 'weight', 'base_price', 'stock', 'category', 'created_at', 'updated_at', 'available'
#     )
#     list_filter = ('coffee_type', 'weight', 'category', 'created_at')
#     search_fields = ('name', 'variety', 'tags', 'origin')
#     ordering = ('-created_at',)
#     inlines = [ProductImageInline]  # اضافه کردن کلاس Inline به ProductAdmin

#     def available(self, obj):
#         return obj.available
#     available.boolean = True

# @admin.register(ProductImage)
# class ProductImageAdmin(admin.ModelAdmin):
    # list_display = ('product', 'image_type', 'image')
    # list_filter = ('image_type',)
    # search_fields = ('product__name',)
    # ordering = ('product',)


