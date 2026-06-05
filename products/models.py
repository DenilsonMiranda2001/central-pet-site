from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Nome", max_length=100)
    slug = models.SlugField("Identificador (URL)", unique=True)
    icon = models.CharField("Ícone (emoji)", max_length=20, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    order = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:list") + f"?categoria={self.slug}"


class Product(models.Model):
    name = models.CharField("Nome", max_length=200)
    slug = models.SlugField("Identificador (URL)", unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Categoria", related_name="products"
    )
    short_description = models.CharField("Descrição curta", max_length=300, blank=True)
    description = models.TextField("Descrição completa", blank=True)
    price = models.DecimalField("Preço (R$)", max_digits=10, decimal_places=2)
    original_price = models.DecimalField(
        "Preço original (deixe vazio se não houver desconto)",
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    image = models.ImageField("Imagem", upload_to="products/", blank=True, null=True)
    is_featured = models.BooleanField("Destaque na home", default=False)
    is_available = models.BooleanField("Disponível em estoque", default=True)
    is_active = models.BooleanField("Ativo", default=True)
    order = models.PositiveIntegerField("Ordem", default=0)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["order", "-is_featured", "-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    @property
    def has_discount(self):
        return bool(self.original_price and self.original_price > self.price)

    @property
    def discount_percent(self):
        if self.has_discount:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def whatsapp_message(self):
        return (
            f"Olá, vi o produto *{self.name}* no site da Central Pet "
            f"e gostaria de saber se está disponível."
        )
