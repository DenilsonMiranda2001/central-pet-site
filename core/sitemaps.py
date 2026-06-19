from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "sobre",
            "contato",
            "banho_e_tosa",
            "veterinario",
            "boutique_pet",
            "disk_racao",
            "products:list",
            "services:list",
        ]

    def location(self, item):
        return reverse(item)
