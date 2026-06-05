from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def product_list(request):
    categoria_slug = request.GET.get("categoria")
    search = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.filter(is_active=True).order_by("order", "name")
    categoria_ativa = None

    if categoria_slug:
        categoria_ativa = get_object_or_404(Category, slug=categoria_slug, is_active=True)
        products = products.filter(category=categoria_ativa)

    if search:
        products = products.filter(name__icontains=search)

    products = products.order_by("order", "-is_featured", "-created_at")

    return render(request, "products/list.html", {
        "products": products,
        "categories": categories,
        "categoria_ativa": categoria_ativa,
        "search": search,
        "page_title": f"Produtos{' — ' + categoria_ativa.name if categoria_ativa else ''} | Central Pet",
        "meta_description": "Encontre rações, medicamentos, petiscos, brinquedos e acessórios premium para o seu pet na Central Pet.",
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related = Product.objects.filter(
        is_active=True, category=product.category
    ).select_related("category").exclude(pk=product.pk).order_by("order", "-is_featured")[:4]

    return render(request, "products/detail.html", {
        "product": product,
        "related_products": related,
        "page_title": f"{product.name} | Central Pet",
        "meta_description": product.short_description or f"Compre {product.name} na Central Pet. Entrega rápida e sem taxa pelo WhatsApp.",
    })
