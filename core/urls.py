from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sobre/", views.sobre, name="sobre"),
    path("contato/", views.contato, name="contato"),
    path("politica-de-privacidade/", views.privacy_policy, name="privacy_policy"),
    path("loja/info/", views.store_public_info, name="store_public_info"),
    path("banho-e-tosa/", views.banho_e_tosa, name="banho_e_tosa"),
    path("veterinario/", views.veterinario, name="veterinario"),
    path("boutique-pet/", views.boutique_pet, name="boutique_pet"),
    path("medicamentos/", views.medicamentos, name="medicamentos"),
    path("disk-racao/", views.disk_racao, name="disk_racao"),
    path("interacoes/registrar/", views.track_interaction, name="track_interaction"),
    path("__debug__/sentry/", views.sentry_debug, name="sentry_debug"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
