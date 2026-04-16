from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'product_count')
    search_fields = ('name',)
    list_filter = ('created_at',)

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = "Nombre de produits"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'stock_status', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at', 'stock')
    list_editable = ('price', 'stock')
    readonly_fields = ('created_at', 'updated_at')

    def stock_status(self, obj):
        if obj.stock <= 0:
            return '⚠️ Rupture'
        elif obj.stock <= 5:
            return '⚠️ Stock faible'
        return '✓ Normal'
    stock_status.short_description = "État du stock"