from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_thumb", "name", "slug", "order", "is_active")
    list_editable = ("order", "is_active")
    list_display_links = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_per_page = 20
    readonly_fields = ("category_image_preview",)
    fieldsets = (
        ("📁 Categoria", {
            "fields": ("name", "slug", "icon"),
        }),
        ("🖼️ Imagem da categoria", {
            "fields": ("category_image_preview", "image"),
            "description": "Esta imagem pode ser usada automaticamente no topo da página da categoria no site.",
        }),
        ("⚙️ Publicação", {
            "fields": ("is_active", "order"),
        }),
    )

    def category_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;border:1px solid #e5e7eb;" />',
                obj.image.url,
            )
        return format_html(
            '<div style="width:50px;height:50px;background:#f3f4f6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🐾</div>'
        )
    category_thumb.short_description = ""

    def category_image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-height:220px;max-width:360px;object-fit:cover;border-radius:12px;" />',
                obj.image.url,
            )
        return "Nenhuma imagem cadastrada"
    category_image_preview.short_description = "Pré-visualização"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "category", "price_display", "is_featured", "is_available", "is_active", "order")
    list_editable = ("is_featured", "is_available", "is_active", "order")
    list_display_links = ("name",)
    list_filter = (("category", admin.RelatedOnlyFieldListFilter), "is_featured", "is_active", "is_available")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "thumb_preview")
    list_per_page = 20
    save_on_top = True
    fieldsets = (
        ("📦 Informações Principais", {"fields": ("name", "slug", "category", "short_description", "description")}),
        ("💰 Preço e Estoque", {"fields": ("price", "original_price", "is_available")}),
        ("🖼️ Imagem e Visibilidade", {"fields": ("thumb_preview", "image", "is_featured", "is_active", "order")}),
        ("📅 Datas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:8px;border:1px solid #e5e7eb;" />', obj.image.url)
        return format_html('<div style="width:50px;height:50px;background:#f3f4f6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🐾</div>')
    thumb.short_description = ""

    def thumb_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:180px;max-width:280px;object-fit:cover;border-radius:8px;" />', obj.image.url)
        return "Nenhuma imagem cadastrada"
    thumb_preview.short_description = "Pré-visualização"

    def price_display(self, obj):
        if obj.has_discount:
            return format_html('<span style="font-weight:700;color:#16a34a;">R$ {}</span> <span style="text-decoration:line-through;color:#9ca3af;font-size:.85em;">R$ {}</span>', obj.price, obj.original_price)
        return format_html('<span style="font-weight:700;">R$ {}</span>', obj.price)
    price_display.short_description = "Preço"
    price_display.admin_order_field = "price"
