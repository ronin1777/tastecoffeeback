import factory
from faker import Faker
from .models import Product, Category, ProductImage

fake = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyAttribute(lambda _: fake.unique.word())  # نام تصادفی و یکتا
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))  # اسلاگ تصادفی


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.LazyAttribute(lambda _: fake.unique.word())  # نام تصادفی و یکتا
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))  # توضیحات تصادفی
    coffee_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[choice[0] for choice in Product.COFFEE_TYPE_CHOICES]))  # نوع قهوه
    weight = factory.LazyAttribute(lambda _: fake.random_element(elements=[choice[0] for choice in Product.WEIGHT_CHOICES]))  # وزن تصادفی
    variety = factory.LazyAttribute(lambda _: fake.word())  # گونه تصادفی
    flavor_notes = factory.LazyAttribute(lambda _: fake.word())  # طعم‌یادها تصادفی
    origin = factory.LazyAttribute(lambda _: fake.country())  # خاستگاه تصادفی
    brewing_method = factory.LazyAttribute(lambda _: fake.word())  # دم‌افزار تصادفی
    body = factory.LazyAttribute(lambda _: fake.word())  # جان‌مایه تصادفی
    sweetness = factory.LazyAttribute(lambda _: fake.word())  # شیرینی تصادفی
    bitterness = factory.LazyAttribute(lambda _: fake.word())  # تلخی تصادفی
    packaging_color = factory.LazyAttribute(lambda _: fake.color_name())  # رنگ بسته‌بندی تصادفی
    roast_level = factory.LazyAttribute(lambda _: fake.word())  # درجه برشته‌کاری تصادفی
    base_price = factory.LazyAttribute(lambda _: fake.pydecimal(left_digits=5, right_digits=2, positive=True))  # قیمت پایه تصادفی
    stock = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=100))  # موجودی تصادفی
    category = factory.SubFactory(CategoryFactory)  # دسته‌بندی تصادفی

    created_at = factory.LazyAttribute(lambda _: fake.date_time_this_year())  # تاریخ ایجاد تصادفی
    updated_at = factory.LazyAttribute(lambda _: fake.date_time_this_year())  # تاریخ بروزرسانی تصادفی


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)  # محصول تصادفی
    image = factory.django.ImageField(color='blue')  # تولید تصویر تصادفی
    image_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[ProductImage.PRIMARY, ProductImage.SECONDARY, ProductImage.TERTIARY]))  # نوع تصویر تصادفی