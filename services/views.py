from django.shortcuts import render
from .models import Service
from core.models import StoreConfig


def service_list(request):
    services = Service.objects.filter(is_active=True).order_by("order", "name")
    config = StoreConfig.get_config()

    return render(request, "services/list.html", {
        "services": services,
        "config": config,
        "page_title": "Serviços — Banho & Tosa, Táxi Dog | Central Pet",
        "meta_description": "Banho & Tosa profissional, Táxi Dog, Hidratação e muito mais. Agende pelo WhatsApp com a Central Pet.",
    })
