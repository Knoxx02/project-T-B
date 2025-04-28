from django.contrib import admin
from .models import Product, Category, Brand


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'sale_price', 'brand', 'category', 'in_stock', 'is_featured', 'created']
    list_filter = ['in_stock', 'is_featured', 'is_new', 'brand', 'category', 'created']
    list_editable = ['price', 'sale_price', 'in_stock', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}