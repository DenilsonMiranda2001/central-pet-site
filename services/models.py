from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    name = models.CharField("Nome", max_length=150)
    slug = models.SlugField("Identificador (URL)", unique=True, blank=True)
    short_description = models.CharField("Descrição curta", max_length=300, blank=True)
    description = models.TextField("Descrição completa")
    price_from = models.DecimalField(
        "Preço a partir de (R$)", max_digits=8, decimal_places=2,
        null=True, blank=True, help_text="Deixe vazio se o preço for variável"
    )
    image = models.ImageField("Imagem", upload_to="services/", blank=True, null=True)
    icon = models.CharField("Ícone (emoji)", max_length=20, blank=True)
    related_products = models.ManyToManyField(
        "products.Product",
        verbose_name="Produtos relacionados",
        blank=True,
        related_name="related_services",
        help_text=(
            "Selecione os produtos que devem aparecer nesta página de serviço. "
            "Ideal para Boutique Pet e Medicamentos."
        ),
    )
    whatsapp_message = models.TextField(
        "Mensagem WhatsApp personalizada", blank=True,
        help_text="Mensagem enviada automaticamente ao clicar em 'Agendar'. Deixe vazio para usar o padrão."
    )
    is_featured = models.BooleanField("Destaque na home", default=False)
    is_active = models.BooleanField("Ativo", default=True)
    order = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.whatsapp_message:
            self.whatsapp_message = f"Olá, gostaria de agendar *{self.name}* para meu pet. Qual a disponibilidade?"
        super().save(*args, **kwargs)
