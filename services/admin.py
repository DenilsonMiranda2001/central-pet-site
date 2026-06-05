from django.contrib import admin
from django.utils.html import format_html
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("icon_display", "name", "price_display", "is_featured", "is_active", "order")
    list_editable = ("is_featured", "is_active", "order")
    list_display_links = ("name",)
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20
    save_on_top = True
    fieldsets = (
        ("✂️ Informações do Serviço", {
            "fields": ("name", "slug", "icon", "short_description", "description"),
        }),
        ("💰 Preço e Imagem", {
            "fields": ("price_from", "image"),
        }),
        ("💬 Mensagem WhatsApp", {
            "fields": ("whatsapp_message",),
            "description": "Mensagem enviada automaticamente ao cliente ao clicar em 'Agendar'. "
                           "Se vazio, usa o padrão automático.",
        }),
        ("⚙️ Configurações", {
            "fields": ("is_featured", "is_active", "order"),
        }),
    )

    def icon_display(self, obj):
        return format_html(
            '<span style="font-size:1.4rem;">{}</span>', obj.icon or "🐾"
        )
    icon_display.short_description = ""

    def price_display(self, obj):
        if obj.price_from:
            return format_html('<span style="font-weight:700;color:#16a34a;">A partir de R$ {}</span>', obj.price_from)
        return format_html('<span style="color:#9ca3af;">Sob consulta</span>')
    price_display.short_description = "Preço"
    price_display.admin_order_field = "price_from"
