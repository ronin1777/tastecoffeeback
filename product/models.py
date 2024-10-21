import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('نام دسته‌بندی'))
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name=_('اسلاگ'))

    class Meta:
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')

    def __str__(self):
        return self.name


class Product(models.Model):
    COFFEE_TYPE_CHOICES = (
        ('bean', 'دان قهوه'),
        ('ground', 'پودر قهوه'),
    )

    WEIGHT_CHOICES = (
        ('250g', '۲۵۰ گرم'),
        ('500g', 'نیم کیلو'),
        ('1000g', 'یک کیلو'),
    )

    name = models.CharField(max_length=100, verbose_name=_('نام'), db_index=True)
    description = models.TextField(verbose_name=_('توضیحات'), blank=True, null=True)
    coffee_type = models.CharField(max_length=10, choices=COFFEE_TYPE_CHOICES, verbose_name=_('نوع قهوه'))
    weight = models.CharField(max_length=10, choices=WEIGHT_CHOICES, verbose_name=_('وزن'))
    variety = models.CharField(max_length=100, verbose_name=_('گونه'), blank=True, null=True)
    flavor_notes = models.CharField(max_length=100,verbose_name=_('طعم‌یادها'), blank=True, null=True)
    origin = models.CharField(max_length=100, verbose_name=_('خاستگاه'), blank=True, null=True)
    brewing_method = models.CharField(max_length=100, verbose_name=_('دم افزار'), blank=True, null=True)
    body = models.CharField(max_length=100, verbose_name=_('جان‌مایه (بادی)'), blank=True, null=True)
    sweetness = models.CharField(max_length=100, verbose_name=_('شیرینی'), blank=True, null=True)
    bitterness = models.CharField(max_length=100, verbose_name=_('میزان تلخی'), blank=True, null=True)
    packaging_color = models.CharField(max_length=30, verbose_name=_('رنگ بسته‌بندی'), blank=True, null=True)
    roast_level = models.CharField(max_length=50, verbose_name=_('درجه برشته‌کاری'), blank=True, null=True)
    base_price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_('قیمت پایه'))
    stock = models.PositiveSmallIntegerField(verbose_name=_('موجودی'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
                                 verbose_name=_('دسته‌بندی'))
    tags = models.CharField(max_length=200, verbose_name=_('تگ‌ها'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))

    @property
    def available(self):
        return self.stock > 0

    @property
    def primary_image(self):
        try:
            return self.images.get(image_type=ProductImage.PRIMARY).image.url
        except ProductImage.DoesNotExist:
            return None

    def decrease_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        self.stock += quantity
        self.save()

    class Meta:
        verbose_name = _('محصول')
        verbose_name_plural = _('محصولات')

    def __str__(self):
        return f"{self.name} - {self.coffee_type} - {self.weight}"


class ProductImage(models.Model):
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    TERTIARY = 'tertiary'

    IMAGE_TYPES = [
        (PRIMARY, _('عکس اصلی')),
        (SECONDARY, _('عکس دوم')),
        (TERTIARY, _('عکس سوم')),
    ]

    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default=PRIMARY)

    def clean(self):
        if not self.product.id:  # بررسی ذخیره بودن محصول
            return
        
        existing_images = ProductImage.objects.filter(
            product=self.product,
            image_type=self.image_type
        ).exclude(id=self.id)
        
        if existing_images.exists():
            raise ValidationError(f"محصول قبلا یک تصویر {self.get_image_type_display()} داشته است.")

    def save(self, *args, **kwargs):
        if self.product is not None and self.product.id is None:
            return  # جلوگیری از ذخیره قبل از ذخیره محصول
        self.clean()
        super(ProductImage, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('عکس')
        verbose_name_plural = _('عکس ها')

    def __str__(self):
        return f"{self.get_image_type_display()} for {self.product.name}"

