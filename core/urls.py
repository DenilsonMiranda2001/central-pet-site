from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sobre/", views.sobre, name="sobre"),
    path("contato/", views.contato, name="contato"),
    path("disk-racao/", views.disk_racao, name="disk_racao"),
    path("interacoes/registrar/", views.track_interaction, name="track_interaction"),
    path("__debug__/sentry/", views.sentry_debug, name="sentry_debug"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
