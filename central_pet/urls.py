from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap
from products.sitemaps import ProductSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

admin.site.site_header = "In Dog — Painel Administrativo"
admin.site.site_title = "In Dog Admin"
admin.site.index_title = "Gerenciamento da Loja"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('painel/', include('panel.urls', namespace='panel')),
    path('', include('core.urls')),
    path('produtos/', include('products.urls')),
    path('servicos/', include('services.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
