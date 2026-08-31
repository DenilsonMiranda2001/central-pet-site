from django.contrib import admin
from django.utils.html import format_html
from .models import StoreConfig, Banner, Testimonial, InteractionLog


@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    save_on_top = True
    fieldsets = (
        ("Identidade da Loja", {"fields": ("store_name", "slogan")} ),
        ("Contato e Redes Sociais", {"fields": ("whatsapp_number", "phone_number", "email", "instagram_url", "facebook_url", "tiktok_url")} ),
        ("Localização e Horário", {"fields": ("address", "maps_url", "opening_hours")} ),
        ("Hero / Banner Principal", {"fields": ("hero_title", "hero_subtitle", "delivery_text"), "description": "O banner principal é gerenciado em Banners. Estes campos permanecem disponíveis para conteúdo institucional."} ),
        ("Sobre a In Dog", {"fields": ("about_text", "about_image")} ),
    )

    def has_add_permission(self, request):
        return not StoreConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "order", "is_active")
    list_editable = ("order", "is_active")
    list_display_links = ("title",)
    list_per_page = 20

    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:cover;border-radius:8px;" />', obj.image.url)
        return "—"
    thumb.short_description = "Imagem"


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "pet_name", "stars", "is_active", "order")
    list_editable = ("is_active", "order")
    list_display_links = ("customer_name",)
    search_fields = ("customer_name", "comment")
    list_per_page = 20
    fieldsets = (
        ("Cliente", {"fields": ("customer_name", "pet_name")} ),
        ("Depoimento", {"fields": ("comment", "rating")} ),
        ("Configurações", {"fields": ("is_active", "order")} ),
    )

    def stars(self, obj):
        return "★" * obj.rating + "☆" * (5 - obj.rating)
    stars.short_description = "Avaliação"


@admin.register(InteractionLog)
class InteractionLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "tipo", "produto", "servico", "nome_produto_snapshot", "nome_servico_snapshot")
    list_filter = ("tipo", "created_at")
    search_fields = ("nome_produto_snapshot", "categoria_produto_snapshot", "nome_servico_snapshot", "user_agent")
    readonly_fields = ("tipo", "produto", "servico", "nome_produto_snapshot", "preco_produto_snapshot", "categoria_produto_snapshot", "nome_servico_snapshot", "ip_hash", "user_agent", "created_at")
    list_per_page = 30
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
