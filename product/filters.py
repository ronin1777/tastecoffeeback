from django_filters import rest_framework as filters
from .models import Product


class ProductFilter(filters.FilterSet):
    coffee_type = filters.ChoiceFilter(field_name='coffee_type', choices=Product.COFFEE_TYPE_CHOICES)
    weight = filters.ChoiceFilter(field_name='weight', choices=Product.WEIGHT_CHOICES)
    min_price = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', label='نام محصول')
    available = filters.BooleanFilter(method='filter_by_stock', label='موجودی')

    class Meta:
        model = Product
        fields = ['coffee_type', 'weight', 'min_price', 'max_price', 'name', 'available']

    def filter_by_stock(self, queryset, name, value):
        """Filter products that have stock if 'available' is True."""
        if value:  # اگر موجودی را TRUE کنید
            return queryset.filter(stock__gt=0)  # فقط محصولاتی که موجودی آنها بیشتر از صفر است
        return queryset  # در غیر این صورت همه‌ی محصولات را باز می‌گرداند


