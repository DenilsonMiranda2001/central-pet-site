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


def privacy_policy(request):
    config = StoreConfig.get_config()
    return render(request, "core/privacy.html", {
        "config": config,
        "page_title": "Política de Privacidade | In Dog",
        "meta_description": "Saiba como a In Dog trata dados usados no site, no carrinho, no agendamento e nos contatos via WhatsApp.",
    })


def store_public_info(request):
    """Informações públicas usadas para manter elementos globais sincronizados com o Admin."""
    config = StoreConfig.get_config()
    return JsonResponse({
        "opening_hours": config.opening_hours,
        "phone_number": config.phone_number,
    })


def _service_detail(request, service_slug, fallback):
    service = Service.objects.filter(slug=service_slug, is_active=True).first()
    context = dict(fallback)
    context["service"] = service
    related_products = Product.objects.none()

    if service:
        context["title"] = service.name
        context["description"] = service.description or service.short_description or context["description"]
        context["eyebrow"] = service.name
        context["whatsapp_text"] = service.whatsapp_message or context["whatsapp_text"]
        related_products = service.related_products.filter(
            is_active=True,
            is_available=True,
        ).select_related("category").order_by("order", "name")[:12]

    # Medicamentos é uma categoria comercial importante. Se o Admin ainda não
    # relacionou itens manualmente ao serviço, mostramos os produtos ativos da
    # categoria em vez de deixar a página parecer vazia/incompleta.
    if service_slug == "medicamentos" and not related_products.exists():
        related_products = Product.objects.filter(
            is_active=True,
            is_available=True,
            category__slug="medicamentos",
        ).select_related("category").order_by("order", "name")[:12]

    context["related_products"] = related_products
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
        "highlights": [
            {"title": "Banho completo", "text": "Higiene completa com produtos adequados ao tipo de pelagem e às necessidades do pet."},
            {"title": "Tosa higiênica", "text": "Acabamento cuidadoso nas áreas que exigem mais higiene e conforto no dia a dia."},
            {"title": "Tosa personalizada", "text": "Corte alinhado ao estilo desejado, respeitando raça, pelagem e bem-estar."},
            {"title": "Escovação", "text": "Finalização para desembaraçar, remover pelos soltos e valorizar a pelagem."},
            {"title": "Limpeza de ouvidos", "text": "Higiene externa feita com delicadeza como parte da rotina de cuidados."},
            {"title": "Corte de unhas", "text": "Manutenção das unhas para mais conforto e segurança na movimentação do pet."},
            {"title": "Produtos premium", "text": "Seleção de produtos de qualidade para uma experiência mais confortável."},
            {"title": "Atendimento cuidadoso", "text": "Cada pet é atendido respeitando seu comportamento, tempo e necessidades individuais."},
        ],
        "cta": "Agendar Banho e Tosa no WhatsApp",
        "whatsapp_text": "Olá, gostaria de agendar Banho e Tosa Premium na In Dog.",
    })


def veterinario(request):
    return _service_detail(request, "consultorio-veterinario", {
        "page_title": "Consultório Veterinário no Lago Sul | In Dog",
        "meta_description": "Consultório veterinário no Lago Sul com foco em prevenção, saúde e bem-estar dos pets.",
        "slug": "consultorio-veterinario",
        "eyebrow": "Veterinário",
        "icon": "🩺",
        "title": "Consultório Veterinário no Lago Sul",
        "description": "Atendimento veterinário com foco em prevenção, saúde e bem-estar dos pets.",
        "highlights": [
            {"title": "Consultas veterinárias", "text": "Avaliação clínica com atenção ao histórico, sinais apresentados e rotina do pet."},
            {"title": "Vacinação", "text": "Orientação sobre protocolos preventivos conforme idade, histórico e avaliação profissional."},
            {"title": "Check-up preventivo", "text": "Acompanhamento periódico para observar a saúde do pet e identificar necessidades precocemente."},
            {"title": "Vermifugação", "text": "Orientação responsável sobre prevenção e controle de parasitas conforme cada caso."},
            {"title": "Pulgas e carrapatos", "text": "Avaliação e orientação para estratégias de prevenção adequadas ao pet e ao ambiente."},
            {"title": "Orientação nutricional", "text": "Recomendações de rotina alimentar de acordo com fase de vida e necessidades individuais."},
            {"title": "Acompanhamento clínico", "text": "Continuidade do cuidado para acompanhar evolução, prevenção e qualidade de vida."},
        ],
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
        "highlights": [
            {"title": "Acessórios", "text": "Itens selecionados para deixar a rotina do pet mais prática, confortável e bonita."},
            {"title": "Roupinhas", "text": "Opções para diferentes estilos, tamanhos e ocasiões, sempre priorizando conforto."},
            {"title": "Camas", "text": "Modelos pensados para descanso, aconchego e bem-estar dentro de casa."},
            {"title": "Guias e coleiras", "text": "Produtos para passeios com diferentes propostas de tamanho, resistência e acabamento."},
            {"title": "Brinquedos", "text": "Alternativas para diversão, estímulo e enriquecimento da rotina do pet."},
            {"title": "Itens de higiene", "text": "Produtos úteis para os cuidados cotidianos de cães e gatos."},
            {"title": "Seleção In Dog", "text": "Curadoria de produtos escolhidos para unir qualidade, utilidade e estilo."},
        ],
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
        "description": "Consulte a disponibilidade de medicamentos veterinários, antiparasitários, suplementos e produtos de cuidado na In Dog. Para itens que exigem orientação profissional, nossa equipe direciona você ao atendimento adequado.",
        "highlights": [
            {"title": "Antiparasitários", "text": "Consulte opções disponíveis para prevenção e controle de parasitas em cães e gatos."},
            {"title": "Vermífugos", "text": "Disponibilidade sob consulta, com orientação adequada à necessidade do pet."},
            {"title": "Suplementos", "text": "Produtos de suporte nutricional e bem-estar selecionados para diferentes necessidades."},
            {"title": "Cuidados dermatológicos", "text": "Itens para higiene e cuidado da pele e pelagem, conforme indicação e necessidade."},
            {"title": "Higiene e saúde", "text": "Produtos de rotina para complementar os cuidados do seu pet no dia a dia."},
            {"title": "Consulta rápida", "text": "Envie o nome do produto pelo WhatsApp e confirme disponibilidade antes de sair de casa."},
        ],
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
