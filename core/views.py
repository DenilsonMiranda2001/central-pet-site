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
        "page_title": f"{config.store_name} — {config.slogan}",
        "meta_description": (
            "Pet shop em Brasília com Banho & Tosa, Táxi Dog, rações premium, medicamentos "
            "e Disk Ração com entrega grátis. Fale pelo WhatsApp!"
        ),
    })


def sobre(request):
    config = StoreConfig.get_config()
    return render(request, "core/sobre.html", {
        "config": config,
        "page_title": f"Sobre a {config.store_name} — Quem Somos",
        "meta_description": f"Conheça a {config.store_name}, pet shop em Brasília com atendimento premium, Banho & Tosa, Disk Ração e entrega grátis.",
    })


def contato(request):
    config = StoreConfig.get_config()
    return render(request, "core/contato.html", {
        "config": config,
        "page_title": f"Contato — {config.store_name}",
        "meta_description": "Entre em contato com a Central Pet pelo WhatsApp, telefone ou visite nossa loja em Brasília.",
    })


def disk_racao(request):
    config = StoreConfig.get_config()
    racoes = Product.objects.filter(
        is_active=True, is_available=True, category__slug="racoes"
    ).select_related("category").order_by("order", "name")[:8]
    return render(request, "core/disk_racao.html", {
        "config": config,
        "racoes": racoes,
        "page_title": "Disk Ração — Entrega Grátis | Central Pet",
        "meta_description": "Ficou sem ração? A Central Pet entrega no mesmo dia, sem taxa. Peça pelo WhatsApp agora!",
    })


def robots_txt(request):
    from django.http import HttpResponse
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
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
    raise RuntimeError("Teste de integração Sentry - Central Pet")
