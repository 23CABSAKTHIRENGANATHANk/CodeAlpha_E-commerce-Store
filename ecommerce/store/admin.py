import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from .models import Category, Product, Order, OrderItem, Wishlist


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price']


class LowStockFilter(admin.SimpleListFilter):
    title = 'Stock Level Alert'
    parameter_name = 'stock_alert'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Low Stock (5 or less)'),
            ('out', 'Out of Stock (0)'),
            ('adequate', 'Adequate Stock (6+)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock__lte=5, stock__gt=0)
        if self.value() == 'out':
            return queryset.filter(stock=0)
        if self.value() == 'adequate':
            return queryset.filter(stock__gt=5)
        return queryset


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={opts.verbose_name_plural}.csv'
    writer = csv.writer(response)
    
    # Write header
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.name for field in fields])
    
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            data_row.append(value)
        writer.writerow(data_row)
    return response

export_to_csv.short_description = 'Export selected items to CSV'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'price', 'category', 'stock_status', 'created_at']
    list_filter = ['category', LowStockFilter, 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'image_tag']
    fields = ['name', 'description', 'price', 'stock', 'category', 'image', 'image_url', 'image_tag', 'created_at', 'updated_at']
    actions = [export_to_csv]

    def image_tag(self, obj):
        if obj.display_image_url:
            return mark_safe(f'<img src="{obj.display_image_url}" class="admin-thumbnail" width="50" height="50" style="object-fit: cover; border-radius: 6px;" />')
        return "No Image"
    image_tag.short_description = 'Preview'

    def stock_status(self, obj):
        if obj.stock == 0:
            return mark_safe('<span class="badge-stock outstock">Out of Stock (0)</span>')
        elif obj.stock <= 5:
            return mark_safe(f'<span class="badge-stock lowstock">Low Stock ({obj.stock})</span>')
        else:
            return mark_safe(f'<span class="badge-stock instock">In Stock ({obj.stock})</span>')
    stock_status.short_description = 'Stock Status'

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    list_editable = ['status']
    search_fields = ['user__username', 'user__email', 'shipping_city', 'shipping_country', 'shipping_address']
    readonly_fields = ['order_date', 'updated_at']
    inlines = [OrderItemInline]
    actions = [export_to_csv, 'mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price']
    search_fields = ['order__id', 'product__name']

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']
    filter_horizontal = ['products']

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }
