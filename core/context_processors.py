from .models import StoreConfig


def normalize_whatsapp_number(number):
    digits = "".join(ch for ch in str(number or "") if ch.isdigit())
    if len(digits) in (10, 11):
        return f"55{digits}"
    return digits


def store_config(request):
    config = StoreConfig.get_config()
    # Importações internas para evitar circular import
    from products.models import Category
    from services.models import Service

    nav_categories = Category.objects.filter(is_active=True).order_by("order", "name")
    nav_services = Service.objects.filter(is_active=True).order_by("order", "name")

    whatsapp_number = "5561996600007"

    return {
        "store": config,
        "whatsapp_number": whatsapp_number,
        "whatsapp_url": f"https://wa.me/{whatsapp_number}",
        "nav_categories": nav_categories,
        "nav_services": nav_services,
    }
