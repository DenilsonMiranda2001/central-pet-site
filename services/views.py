from django.shortcuts import render
from .models import Service
from core.models import StoreConfig


def service_list(request):
    services = Service.objects.filter(is_active=True).order_by("order", "name")
    config = StoreConfig.get_config()

    return render(request, "services/list.html", {
        "services": services,
        "config": config,
        "page_title": "Serviços Pet no Lago Sul | In Dog",
        "meta_description": "Conheça os serviços pet da In Dog no Lago Sul: banho e tosa premium, consultório veterinário, boutique pet, medicamentos e produtos para pets.",
    })
