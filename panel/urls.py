from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('login/', views.painel_login, name='login'),
    path('logout/', views.painel_logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('relatorios/', views.relatorios, name='relatorios'),

    path('produtos/', views.produto_lista, name='produto_lista'),
    path('produtos/novo/', views.produto_novo, name='produto_novo'),
    path('produtos/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('produtos/<int:pk>/excluir/', views.produto_excluir, name='produto_excluir'),

    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nova/', views.categoria_nova, name='categoria_nova'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/excluir/', views.categoria_excluir, name='categoria_excluir'),

    path('servicos/', views.servico_lista, name='servico_lista'),
    path('servicos/novo/', views.servico_novo, name='servico_novo'),
    path('servicos/<int:pk>/editar/', views.servico_editar, name='servico_editar'),
    path('servicos/<int:pk>/excluir/', views.servico_excluir, name='servico_excluir'),

    path('banners/', views.banner_lista, name='banner_lista'),
    path('banners/novo/', views.banner_novo, name='banner_novo'),
    path('banners/<int:pk>/editar/', views.banner_editar, name='banner_editar'),
    path('banners/<int:pk>/excluir/', views.banner_excluir, name='banner_excluir'),

    path('depoimentos/', views.depoimento_lista, name='depoimento_lista'),
    path('depoimentos/novo/', views.depoimento_novo, name='depoimento_novo'),
    path('depoimentos/<int:pk>/editar/', views.depoimento_editar, name='depoimento_editar'),
    path('depoimentos/<int:pk>/excluir/', views.depoimento_excluir, name='depoimento_excluir'),

    path('configuracoes/', views.configuracoes, name='configuracoes'),
]
