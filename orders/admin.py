from django.contrib import admin
from .models import Cart, CartItem, OrderItem, Order, ShippingMethod


class CartItemInline(admin.TabularInline):
    """Inline view for CartItem in Cart admin."""
    model = CartItem
    extra = 1  # Number of empty forms to display
    min_num = 1  # Minimum number of forms required
    max_num = 10  # Maximum number of forms allowed
    fields = ('product', 'quantity')  # Fields to display
    readonly_fields = ('product',)  # Make the product field read-only


class CartAdmin(admin.ModelAdmin):
    """Admin view for Cart model."""
    list_display = ('id', 'created_at')  # Fields to display in the list view
    search_fields = ('id',)  # Fields to search in the admin
    inlines = [CartItemInline]  # Include CartItem inline
    readonly_fields = ('created_at',)  # Make created_at field read-only


class CartItemAdmin(admin.ModelAdmin):
    """Admin view for CartItem model."""
    list_display = ('cart', 'product', 'quantity')  # Fields to display in the list view
    list_filter = ('cart',)  # Filters to add on the right side
    search_fields = ('product__name',)  # Search functionality based on product name


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False
    verbose_name = 'آیتم سفارش'
    verbose_name_plural = 'آیتم‌های سفارش'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'shipping_method', 'shipping_method_price', 'final_price', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__name', 'user__phone_number', 'id')
    readonly_fields = ('total_price', 'created_at', 'updated_at', 'final_price')
    inlines = [OrderItemInline]
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'shipping_address', 'postal_code')
        }),
        ('اطلاعات سفارش', {
            'fields': ('status', 'total_price', 'created_at', 'updated_at', 'final_price')
        }),
    )

    def shipping_method_name(self, obj):
        return obj.shipping_method.name if obj.shipping_method else 'N/A'
    shipping_method_name.short_description = 'نام روش ارسال'

    def shipping_method_price(self, obj):
        return obj.shipping_method.price if obj.shipping_method else 'N/A'
    shipping_method_price.short_description = 'هزینه ارسال'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    list_filter = ('order__status', 'product')
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('order', 'product', 'quantity', 'price')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    ordering = ('price',)

    def __str__(self):
        return self.name


# Register the models with the custom admin classes
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
