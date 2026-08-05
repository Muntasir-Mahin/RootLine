from django.contrib import admin

from .models import Bid, Category, Order, Product, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "shop_name",
        "phone",
        "seller_requested",
        "seller_approved",
    ]

    list_filter = [
        "seller_requested",
        "seller_approved",
    ]

    search_fields = [
        "user__username",
        "user__email",
        "shop_name",
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
    ]

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "seller",
        "category",
        "sale_type",
        "price",
        "stock",
        "is_active",
        "created_at",
    ]

    list_filter = [
        "sale_type",
        "category",
        "is_active",
    ]

    search_fields = [
        "title",
        "seller__username",
        "description",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "bidder",
        "amount",
        "created_at",
    ]

    search_fields = [
        "product__title",
        "bidder__username",
    ]

    readonly_fields = [
        "created_at",
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product",
        "buyer",
        "quantity",
        "unit_price",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
    ]

    search_fields = [
        "product__title",
        "buyer__username",
    ]

    readonly_fields = [
        "created_at",
    ]


admin.site.site_header = "RootLine Administration"
admin.site.site_title = "RootLine Admin"
admin.site.index_title = "Manage RootLine Marketplace"