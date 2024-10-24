# Generated by Django 5.0.9 on 2024-10-24 22:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام دسته\u200cبندی')),
                ('slug', models.SlugField(allow_unicode=True, unique=True, verbose_name='اسلاگ')),
            ],
            options={
                'verbose_name': 'دسته بندی',
                'verbose_name_plural': 'دسته بندی ها',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='نام')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('coffee_type', models.CharField(choices=[('bean', 'دان قهوه'), ('ground', 'پودر قهوه')], max_length=10, verbose_name='نوع قهوه')),
                ('weight', models.CharField(choices=[('250g', '۲۵۰ گرم'), ('500g', 'نیم کیلو'), ('1000g', 'یک کیلو')], max_length=10, verbose_name='وزن')),
                ('variety', models.CharField(blank=True, max_length=100, null=True, verbose_name='گونه')),
                ('flavor_notes', models.CharField(blank=True, max_length=100, null=True, verbose_name='طعم\u200cیادها')),
                ('origin', models.CharField(blank=True, max_length=100, null=True, verbose_name='خاستگاه')),
                ('brewing_method', models.CharField(blank=True, max_length=100, null=True, verbose_name='دم افزار')),
                ('body', models.CharField(blank=True, max_length=100, null=True, verbose_name='جان\u200cمایه (بادی)')),
                ('sweetness', models.CharField(blank=True, max_length=100, null=True, verbose_name='شیرینی')),
                ('bitterness', models.CharField(blank=True, max_length=100, null=True, verbose_name='میزان تلخی')),
                ('packaging_color', models.CharField(blank=True, max_length=30, null=True, verbose_name='رنگ بسته\u200cبندی')),
                ('roast_level', models.CharField(blank=True, max_length=50, null=True, verbose_name='درجه برشته\u200cکاری')),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='قیمت پایه')),
                ('stock', models.PositiveSmallIntegerField(verbose_name='موجودی')),
                ('tags', models.CharField(blank=True, max_length=200, null=True, verbose_name='تگ\u200cها')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='product.category', verbose_name='دسته\u200cبندی')),
            ],
            options={
                'verbose_name': 'محصول',
                'verbose_name_plural': 'محصولات',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='product_images/')),
                ('image_type', models.CharField(choices=[('primary', 'عکس اصلی'), ('secondary', 'عکس دوم'), ('tertiary', 'عکس سوم')], default='primary', max_length=20)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.product')),
            ],
            options={
                'verbose_name': 'عکس',
                'verbose_name_plural': 'عکس ها',
            },
        ),
    ]
