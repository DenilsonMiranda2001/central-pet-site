from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from functools import wraps
from datetime import datetime, timedelta

from products.models import Product, Category
from services.models import Service
from core.models import StoreConfig, Banner, Testimonial, InteractionLog
from .forms import (
    ProdutoForm, CategoriaForm, ServicoForm,
    BannerForm, DepoimentoForm, ConfiguracaoForm,
)


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/painel/login/?next={request.path}")
        if not request.user.is_active or not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Você não tem permissão para acessar o painel.")
            return render(request, "painel/403.html", {"page_title": "Acesso bloqueado"}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped


# ── AUTH ──────────────────────────────────────────────────────────────────────

def painel_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('panel:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect(request.POST.get('next', '/painel/'))
        messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'painel/login.html', {'next': request.GET.get('next', '/painel/')})


@login_required(login_url='/painel/login/')
def painel_logout(request):
    logout(request)
    return redirect('/painel/login/')


# ── DASHBOARD ────────────────────────────────────────────────────────────────

@staff_required
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    logs = InteractionLog.objects.all()
    logs_today = logs.filter(created_at__date=today)
    logs_month = logs.filter(created_at__date__gte=month_start)

    return render(request, 'painel/dashboard.html', {
        'total_produtos': Product.objects.count(),
        'produtos_ativos': Product.objects.filter(is_active=True).count(),
        'produtos_destaque': Product.objects.filter(is_active=True, is_featured=True).count(),
        'servicos_ativos': Service.objects.filter(is_active=True).count(),
        'depoimentos_ativos': Testimonial.objects.filter(is_active=True).count(),
        'banners_ativos': Banner.objects.filter(is_active=True).count(),
        'whatsapp_hoje': logs_today.filter(tipo__in=[
            InteractionLog.PRODUCT_WHATSAPP,
            InteractionLog.GENERAL_WHATSAPP,
            InteractionLog.DISK_RACAO,
        ]).count(),
        'whatsapp_mes': logs_month.filter(tipo__in=[
            InteractionLog.PRODUCT_WHATSAPP,
            InteractionLog.GENERAL_WHATSAPP,
            InteractionLog.DISK_RACAO,
        ]).count(),
        'agendamentos_abertos': logs_month.filter(tipo=InteractionLog.SERVICE_APPOINTMENT_OPENED).count(),
        'agendamentos_enviados': logs_month.filter(tipo=InteractionLog.APPOINTMENT_SENT).count(),
        'cliques_instagram': logs_month.filter(tipo=InteractionLog.INSTAGRAM).count(),
        'top_produtos': _top_products(logs_month),
        'top_servicos': _top_services(logs_month),
        'ultimas_interacoes': logs.select_related('produto', 'servico')[:8],
        'page_title': 'Dashboard',
    })


@staff_required
def relatorios(request):
    period = request.GET.get('periodo', '30')
    start_date, period_label = _period_start(period)
    logs = InteractionLog.objects.filter(created_at__gte=start_date)

    whatsapp_types = [
        InteractionLog.PRODUCT_WHATSAPP,
        InteractionLog.GENERAL_WHATSAPP,
        InteractionLog.DISK_RACAO,
    ]

    return render(request, 'painel/relatorios.html', {
        'page_title': 'Relatórios',
        'periodo': period,
        'period_label': period_label,
        'total_interacoes': logs.count(),
        'produtos_mais_clicados': _top_products(logs, limit=10),
        'servicos_mais_procurados': _top_services(logs, limit=10),
        'cliques_whatsapp': logs.filter(tipo__in=whatsapp_types).count(),
        'cliques_instagram': logs.filter(tipo=InteractionLog.INSTAGRAM).count(),
        'agendamentos_enviados': logs.filter(tipo=InteractionLog.APPOINTMENT_SENT).count(),
        'tipo_labels': [
            'Produtos',
            'WhatsApp geral',
            'Produtos Pet',
            'Agendamentos abertos',
            'Agendamentos enviados',
            'Instagram',
        ],
        'tipo_values': [
            logs.filter(tipo=InteractionLog.PRODUCT_WHATSAPP).count(),
            logs.filter(tipo=InteractionLog.GENERAL_WHATSAPP).count(),
            logs.filter(tipo=InteractionLog.DISK_RACAO).count(),
            logs.filter(tipo=InteractionLog.SERVICE_APPOINTMENT_OPENED).count(),
            logs.filter(tipo=InteractionLog.APPOINTMENT_SENT).count(),
            logs.filter(tipo=InteractionLog.INSTAGRAM).count(),
        ],
    })


def _period_start(period):
    now = timezone.now()
    if period == 'hoje':
        return timezone.make_aware(datetime.combine(timezone.localdate(), datetime.min.time())), 'Hoje'
    if period == '7':
        return now - timedelta(days=7), 'Últimos 7 dias'
    return now - timedelta(days=30), 'Últimos 30 dias'


def _top_products(queryset, limit=5):
    return queryset.filter(
        tipo=InteractionLog.PRODUCT_WHATSAPP
    ).exclude(
        nome_produto_snapshot=''
    ).values(
        'produto_id', 'nome_produto_snapshot', 'categoria_produto_snapshot'
    ).annotate(total=Count('id')).order_by('-total', 'nome_produto_snapshot')[:limit]


def _top_services(queryset, limit=5):
    return queryset.filter(
        tipo__in=[InteractionLog.SERVICE_APPOINTMENT_OPENED, InteractionLog.APPOINTMENT_SENT]
    ).exclude(
        nome_servico_snapshot=''
    ).values(
        'servico_id', 'nome_servico_snapshot'
    ).annotate(total=Count('id')).order_by('-total', 'nome_servico_snapshot')[:limit]


# ── PRODUTOS ─────────────────────────────────────────────────────────────────

@staff_required
def produto_lista(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('categoria', '')
    produtos = Product.objects.select_related('category').order_by('order', 'name')
    if q:
        produtos = produtos.filter(name__icontains=q)
    if cat:
        produtos = produtos.filter(category__slug=cat)
    return render(request, 'painel/produtos/lista.html', {
        'produtos': produtos,
        'categorias': Category.objects.filter(is_active=True).order_by('name'),
        'q': q, 'cat_ativa': cat, 'page_title': 'Produtos',
    })


@staff_required
def produto_novo(request):
    form = ProdutoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        produto = form.save(commit=False)
        produto.slug = _gerar_slug(Product, produto.name)
        produto.save()
        messages.success(request, f'Produto "{produto.name}" criado com sucesso!')
        return redirect('panel:produto_lista')
    return render(request, 'painel/produtos/form.html', {
        'form': form, 'page_title': 'Novo Produto', 'acao': 'criar',
    })


@staff_required
def produto_editar(request, pk):
    produto = get_object_or_404(Product, pk=pk)
    form = ProdutoForm(request.POST or None, request.FILES or None, instance=produto)
    if form.is_valid():
        form.save()
        messages.success(request, f'Produto "{produto.name}" atualizado!')
        return redirect('panel:produto_lista')
    return render(request, 'painel/produtos/form.html', {
        'form': form, 'objeto': produto, 'page_title': 'Editar Produto', 'acao': 'editar',
    })


@staff_required
def produto_excluir(request, pk):
    produto = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        nome = produto.name
        produto.delete()
        messages.success(request, f'Produto "{nome}" excluído.')
        return redirect('panel:produto_lista')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': produto, 'tipo': 'produto', 'page_title': 'Excluir Produto',
        'voltar_url': 'panel:produto_lista',
    })


# ── CATEGORIAS ───────────────────────────────────────────────────────────────

@staff_required
def categoria_lista(request):
    return render(request, 'painel/categorias/lista.html', {
        'categorias': Category.objects.order_by('order', 'name'),
        'page_title': 'Categorias',
    })


@staff_required
def categoria_nova(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        cat = form.save(commit=False)
        cat.slug = _gerar_slug(Category, cat.name)
        cat.save()
        messages.success(request, f'Categoria "{cat.name}" criada!')
        return redirect('panel:categoria_lista')
    return render(request, 'painel/categorias/form.html', {
        'form': form, 'page_title': 'Nova Categoria', 'acao': 'criar',
    })


@staff_required
def categoria_editar(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    form = CategoriaForm(request.POST or None, instance=cat)
    if form.is_valid():
        form.save()
        messages.success(request, f'Categoria "{cat.name}" atualizada!')
        return redirect('panel:categoria_lista')
    return render(request, 'painel/categorias/form.html', {
        'form': form, 'objeto': cat, 'page_title': 'Editar Categoria', 'acao': 'editar',
    })


@staff_required
def categoria_excluir(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        nome = cat.name
        cat.delete()
        messages.success(request, f'Categoria "{nome}" excluída.')
        return redirect('panel:categoria_lista')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': cat, 'tipo': 'categoria', 'page_title': 'Excluir Categoria',
        'voltar_url': 'panel:categoria_lista',
    })


# ── SERVIÇOS ─────────────────────────────────────────────────────────────────

@staff_required
def servico_lista(request):
    return render(request, 'painel/servicos/lista.html', {
        'servicos': Service.objects.order_by('order', 'name'),
        'page_title': 'Serviços',
    })


@staff_required
def servico_novo(request):
    form = ServicoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        sv = form.save(commit=False)
        sv.slug = _gerar_slug(Service, sv.name)
        sv.save()
        messages.success(request, f'Serviço "{sv.name}" criado!')
        return redirect('panel:servico_lista')
    return render(request, 'painel/servicos/form.html', {
        'form': form, 'page_title': 'Novo Serviço', 'acao': 'criar',
    })


@staff_required
def servico_editar(request, pk):
    sv = get_object_or_404(Service, pk=pk)
    form = ServicoForm(request.POST or None, request.FILES or None, instance=sv)
    if form.is_valid():
        form.save()
        messages.success(request, f'Serviço "{sv.name}" atualizado!')
        return redirect('panel:servico_lista')
    return render(request, 'painel/servicos/form.html', {
        'form': form, 'objeto': sv, 'page_title': 'Editar Serviço', 'acao': 'editar',
    })


@staff_required
def servico_excluir(request, pk):
    sv = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        nome = sv.name
        sv.delete()
        messages.success(request, f'Serviço "{nome}" excluído.')
        return redirect('panel:servico_lista')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': sv, 'tipo': 'serviço', 'page_title': 'Excluir Serviço',
        'voltar_url': 'panel:servico_lista',
    })


# ── BANNERS ──────────────────────────────────────────────────────────────────

@staff_required
def banner_lista(request):
    return render(request, 'painel/banners/lista.html', {
        'banners': Banner.objects.order_by('order', 'title'),
        'page_title': 'Banners',
    })


@staff_required
def banner_novo(request):
    form = BannerForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Banner criado com sucesso!')
        return redirect('panel:banner_lista')
    return render(request, 'painel/banners/form.html', {
        'form': form, 'page_title': 'Novo Banner', 'acao': 'criar',
    })


@staff_required
def banner_editar(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    form = BannerForm(request.POST or None, request.FILES or None, instance=banner)
    if form.is_valid():
        form.save()
        messages.success(request, f'Banner "{banner.title}" atualizado!')
        return redirect('panel:banner_lista')
    return render(request, 'painel/banners/form.html', {
        'form': form, 'objeto': banner, 'page_title': 'Editar Banner', 'acao': 'editar',
    })


@staff_required
def banner_excluir(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        titulo = banner.title
        banner.delete()
        messages.success(request, f'Banner "{titulo}" excluído.')
        return redirect('panel:banner_lista')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': banner, 'tipo': 'banner', 'page_title': 'Excluir Banner',
        'voltar_url': 'panel:banner_lista',
    })


# ── DEPOIMENTOS ───────────────────────────────────────────────────────────────

@staff_required
def depoimento_lista(request):
    return render(request, 'painel/depoimentos/lista.html', {
        'depoimentos': Testimonial.objects.order_by('order', 'customer_name'),
        'page_title': 'Depoimentos',
    })


@staff_required
def depoimento_novo(request):
    form = DepoimentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Depoimento adicionado!')
        return redirect('panel:depoimento_lista')
    return render(request, 'painel/depoimentos/form.html', {
        'form': form, 'page_title': 'Novo Depoimento', 'acao': 'criar',
    })


@staff_required
def depoimento_editar(request, pk):
    dep = get_object_or_404(Testimonial, pk=pk)
    form = DepoimentoForm(request.POST or None, instance=dep)
    if form.is_valid():
        form.save()
        messages.success(request, f'Depoimento de "{dep.customer_name}" atualizado!')
        return redirect('panel:depoimento_lista')
    return render(request, 'painel/depoimentos/form.html', {
        'form': form, 'objeto': dep, 'page_title': 'Editar Depoimento', 'acao': 'editar',
    })


@staff_required
def depoimento_excluir(request, pk):
    dep = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        nome = dep.customer_name
        dep.delete()
        messages.success(request, f'Depoimento de "{nome}" excluído.')
        return redirect('panel:depoimento_lista')
    return render(request, 'painel/confirmar_exclusao.html', {
        'objeto': dep, 'tipo': 'depoimento', 'page_title': 'Excluir Depoimento',
        'voltar_url': 'panel:depoimento_lista',
    })


# ── CONFIGURAÇÕES ─────────────────────────────────────────────────────────────

@staff_required
def configuracoes(request):
    config = StoreConfig.get_config()
    form = ConfiguracaoForm(request.POST or None, instance=config)
    if form.is_valid():
        form.save()
        messages.success(request, 'Configurações da loja salvas com sucesso!')
        return redirect('panel:configuracoes')
    return render(request, 'painel/configuracoes/form.html', {
        'form': form, 'page_title': 'Configurações da Loja',
    })


# ── HELPERS ──────────────────────────────────────────────────────────────────

def _gerar_slug(model, name):
    import re
    import unicodedata
    slug = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^\w\s-]', '', slug).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    original = slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f'{original}-{counter}'
        counter += 1
    return slug
