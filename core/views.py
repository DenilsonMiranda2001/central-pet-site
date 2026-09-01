import hashlib
import hmac
import json

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import StoreConfig, Testimonial, Banner
from .models import InteractionLog
from products.models import Product, Category
from services.models import Service


def home(request):
    config = StoreConfig.get_config()
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    ).select_related("category").order_by("order", "-created_at")[:8]
    services = Service.objects.filter(is_active=True, is_featured=True).order_by("order")[:4]
    testimonials = Testimonial.objects.filter(is_active=True).order_by("order", "-created_at")[:6]
    categories = Category.objects.filter(is_active=True).order_by("order", "name")
    banners = Banner.objects.filter(is_active=True).order_by("order")[:5]
    banner = banners.first()

    return render(request, "home.html", {
        "config": config,
        "featured_products": featured_products,
        "services": services,
        "testimonials": testimonials,
        "categories": categories,
        "banners": banners,
        "banner": banner,
        "page_title": "In Dog — Banho e Tosa Brasília",
        "meta_description": (
            "In Dog é um pet shop no Lago Sul / Altiplano Leste, Brasília, com Banho e Tosa Premium, "
            "Consultório Veterinário, Boutique Pet, Medicamentos e Produtos Pet."
        ),
    })


def sobre(request):
    config = StoreConfig.get_config()
    product_count = Product.objects.filter(is_active=True).count()
    return render(request, "core/sobre.html", {
        "config": config,
        "product_count": product_count,
        "page_title": "Sobre a In Dog — Quem Somos",
        "meta_description": "Conheça a In Dog, pet shop em Brasília com Banho e Tosa Premium, Consultório Veterinário, Boutique Pet, medicamentos e produtos para pets.",
    })


def contato(request):
    config = StoreConfig.get_config()
    return render(request, "core/contato.html", {
        "config": config,
        "page_title": "Contato — In Dog",
        "meta_description": "Entre em contato com a In Dog pelo WhatsApp ou visite nossa loja no Lago Sul — Brasília/DF.",
    })


def _service_detail(request, service_slug, fallback):
    service = Service.objects.filter(slug=service_slug, is_active=True).first()
    context = dict(fallback)
    context["service"] = service
    context["related_products"] = Product.objects.none()
    if service:
        context["title"] = service.name
        context["description"] = service.description or service.short_description or context["description"]
        context["eyebrow"] = service.name
        context["whatsapp_text"] = service.whatsapp_message or context["whatsapp_text"]
        context["related_products"] = service.related_products.filter(
            is_active=True,
            is_available=True,
        ).select_related("category").order_by("order", "name")[:12]
    return render(request, "core/service_detail.html", context)


def banho_e_tosa(request):
    return _service_detail(request, "banho-e-tosa", {
        "page_title": "Banho e Tosa Premium em Brasília | In Dog",
        "meta_description": "Banho e tosa premium em Brasília com cuidado, carinho, produtos de qualidade e atenção ao bem-estar do pet.",
        "slug": "banho-e-tosa",
        "eyebrow": "Banho e Tosa",
        "icon": "✂️",
        "title": "Banho e Tosa Premium em Brasília",
        "description": "Serviço completo de banho e tosa com cuidado, carinho, produtos de qualidade e atenção ao bem-estar do pet.",
        "highlights": ["Banho completo", "Tosa higiênica", "Tosa personalizada", "Escovação", "Limpeza de ouvidos", "Corte de unhas", "Produtos premium", "Atendimento cuidadoso"],
        "cta": "Agendar Banho e Tosa no WhatsApp",
        "whatsapp_text": "Olá, gostaria de agendar Banho e Tosa Premium na In Dog.",
    })


def veterinario(request):
    return _service_detail(request, "veterinario", {
        "page_title": "Consultório Veterinário no Lago Sul | In Dog",
        "meta_description": "Consultório veterinário no Lago Sul com foco em prevenção, saúde e bem-estar dos pets.",
        "slug": "veterinario",
        "eyebrow": "Veterinário",
        "icon": "🩺",
        "title": "Consultório Veterinário no Lago Sul",
        "description": "Atendimento veterinário com foco em prevenção, saúde e bem-estar dos pets.",
        "highlights": ["Consultas veterinárias", "Vacinação", "Check-up preventivo", "Vermifugação", "Controle de pulgas e carrapatos", "Orientação nutricional", "Acompanhamento clínico"],
        "cta": "Agendar Consulta pelo WhatsApp",
        "whatsapp_text": "Olá, gostaria de agendar uma consulta veterinária na In Dog.",
    })


def boutique_pet(request):
    return _service_detail(request, "boutique-pet", {
        "page_title": "Boutique Pet em Brasília | In Dog",
        "meta_description": "Boutique pet em Brasília com produtos selecionados para pets, acessórios, roupinhas, camas e itens de higiene.",
        "slug": "boutique-pet",
        "eyebrow": "Boutique Pet",
        "icon": "🛍️",
        "title": "Boutique Pet em Brasília",
        "description": "Produtos selecionados para pets com qualidade, estilo e cuidado.",
        "highlights": ["Acessórios", "Roupinhas", "Camas", "Guias e coleiras", "Brinquedos", "Itens de higiene", "Produtos selecionados"],
        "cta": "Falar sobre a Boutique no WhatsApp",
        "whatsapp_text": "Olá, gostaria de conhecer os produtos da Boutique Pet da In Dog.",
    })


def medicamentos(request):
    return _service_detail(request, "medicamentos", {
        "page_title": "Medicamentos Veterinários em Brasília | In Dog",
        "meta_description": "Medicamentos veterinários, antiparasitários, suplementos e produtos de saúde para cães e gatos na In Dog em Brasília.",
        "slug": "medicamentos",
        "eyebrow": "Medicamentos",
        "icon": "💊",
        "title": "Medicamentos e cuidados para a saúde do seu pet",
        "description": "Uma seleção de medicamentos veterinários, antiparasitários, suplementos e produtos de cuidado disponíveis na In Dog.",
        "highlights": ["Antiparasitários", "Vermífugos", "Suplementos", "Cuidados dermatológicos", "Higiene e saúde", "Produtos veterinários"],
        "cta": "Consultar medicamento no WhatsApp",
        "whatsapp_text": "Olá, gostaria de consultar os medicamentos disponíveis na In Dog.",
    })


def disk_racao(request):
    config = StoreConfig.get_config()
    racoes = Product.objects.filter(
        is_active=True, is_available=True, category__slug="racoes"
    ).select_related("category").order_by("order", "name")[:8]
    return render(request, "core/disk_racao.html", {
        "config": config,
        "racoes": racoes,
        "page_title": "Produtos Pet | In Dog",
        "meta_description": "Produtos Pet na In Dog, pet shop no Lago Sul / Altiplano Leste em Brasília. Consulte rações, medicamentos, petiscos e acessórios pelo WhatsApp.",
    })


def robots_txt(request):
    from django.http import HttpResponse
    lines = ["User-agent: *", "Disallow: /admin/", "Allow: /", f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _hash_ip(ip):
    if not ip:
        return ""
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), ip.encode("utf-8"), hashlib.sha256).hexdigest()


@require_POST
def track_interaction(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Dados inválidos."}, status=400)

    tipo = payload.get("tipo")
    allowed_types = {choice[0] for choice in InteractionLog.TYPE_CHOICES}
    if tipo not in allowed_types:
        return JsonResponse({"ok": False, "error": "Tipo de interação inválido."}, status=400)

    product = None
    service = None
    product_id = payload.get("produto_id")
    service_id = payload.get("servico_id")

    if product_id:
        product = Product.objects.select_related("category").filter(pk=product_id, is_active=True).first()
    if service_id:
        service = Service.objects.filter(pk=service_id, is_active=True).first()

    log = InteractionLog(
        tipo=tipo,
        produto=product,
        servico=service,
        ip_hash=_hash_ip(_client_ip(request)),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )

    if product:
        log.nome_produto_snapshot = product.name
        log.preco_produto_snapshot = product.price
        log.categoria_produto_snapshot = product.category.name if product.category else ""
    elif payload.get("nome_produto"):
        log.nome_produto_snapshot = str(payload.get("nome_produto", ""))[:200]

    if service:
        log.nome_servico_snapshot = service.name
    elif payload.get("nome_servico"):
        log.nome_servico_snapshot = str(payload.get("nome_servico", ""))[:150]

    log.save()
    return JsonResponse({"ok": True})


def sentry_debug(request):
    if not settings.DEBUG:
        raise Http404()
    raise RuntimeError("Teste de integração Sentry - In Dog")
