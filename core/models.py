from django.db import models


class StoreConfig(models.Model):
    store_name = models.CharField("Nome da loja", max_length=100, default="In Dog")
    slogan = models.CharField("Slogan", max_length=200, default="Cuidado especial para seu pet desde 2016.")
    whatsapp_number = models.CharField(
        "WhatsApp (apenas números)", max_length=20, default="5561996600007",
        help_text="Ex: 5561996600007 — sem espaços, traços ou parênteses"
    )
    phone_number = models.CharField("Telefone fixo", max_length=20, default="(61) 99660-0007")
    instagram_url = models.CharField("Instagram (usuário, sem @)", max_length=100, default="indogpet")
    facebook_url = models.CharField("Facebook (URL ou usuário)", max_length=200, blank=True)
    tiktok_url = models.CharField("TikTok (usuário, sem @)", max_length=100, blank=True)
    email = models.EmailField("E-mail de contato", blank=True)
    address = models.TextField(
        "Endereço completo",
        default="Lago Sul / Altiplano Leste\nBrasília — DF"
    )
    maps_url = models.URLField(
        "Link Google Maps", blank=True,
        help_text="Cole o link de compartilhamento do Google Maps"
    )
    opening_hours = models.TextField(
        "Horário de funcionamento",
        default="Seg à Sex: 8h às 17h\nSábado: 8h às 16h"
    )
    delivery_text = models.CharField(
        "Destaque da entrega (navbar/hero)",
        max_length=200,
        default="Pet shop premium no Lago Sul — Brasília/DF"
    )
    about_text = models.TextField(
        "Texto sobre a loja",
        default=(
            "Desde 2016 a In Dog oferece cuidados especiais para pets em Brasília. "
            "Localizada no Lago Sul / Altiplano Leste, contamos com Banho e Tosa Premium, "
            "Consultório Veterinário, Boutique Pet e uma linha completa de medicamentos e "
            "produtos para o bem-estar do seu companheiro. Cuidado com amor, profissionalismo "
            "e a atenção que seu pet merece."
        )
    )
    hero_title = models.CharField(
        "Título principal (Hero)", max_length=200,
        default="Cuidado que seu pet sente, amor que fica."
    )
    hero_subtitle = models.TextField(
        "Subtítulo (Hero)",
        default="Banho e Tosa Premium, Consultório Veterinário, Boutique Pet, Medicamentos e Produtos Pet. Pet shop no Lago Sul — Brasília/DF desde 2016."
    )

    class Meta:
        verbose_name = "Configuração da Loja"
        verbose_name_plural = "Configurações da Loja"

    def __str__(self):
        return "Configurações — In Dog"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Banner(models.Model):
    title = models.CharField("Título", max_length=200)
    subtitle = models.CharField("Subtítulo", max_length=300, blank=True)
    image = models.ImageField("Imagem", upload_to="banners/", blank=True)
    button_text = models.CharField("Texto do botão", max_length=100, blank=True)
    button_link = models.CharField("Link do botão", max_length=200, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    order = models.PositiveIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ["order"]

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    customer_name = models.CharField("Nome do cliente", max_length=100)
    pet_name = models.CharField("Nome do pet", max_length=100, blank=True)
    rating = models.PositiveSmallIntegerField("Avaliação (1-5)", default=5)
    comment = models.TextField("Depoimento")
    is_active = models.BooleanField("Ativo", default=True)
    order = models.PositiveIntegerField("Ordem", default=0)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Depoimento"
        verbose_name_plural = "Depoimentos"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.customer_name} — {self.rating}★"


class InteractionLog(models.Model):
    PRODUCT_WHATSAPP = "produto_whatsapp"
    SERVICE_APPOINTMENT_OPENED = "servico_agendamento_aberto"
    APPOINTMENT_SENT = "agendamento_enviado"
    DISK_RACAO = "disk_racao"
    GENERAL_WHATSAPP = "whatsapp_geral"
    INSTAGRAM = "instagram"

    TYPE_CHOICES = [
        (PRODUCT_WHATSAPP, "Produto para WhatsApp"),
        (SERVICE_APPOINTMENT_OPENED, "Agendamento aberto"),
        (APPOINTMENT_SENT, "Agendamento enviado"),
        (DISK_RACAO, "Disk Ração"),
        (GENERAL_WHATSAPP, "WhatsApp geral"),
        (INSTAGRAM, "Instagram"),
    ]

    tipo = models.CharField("Tipo", max_length=40, choices=TYPE_CHOICES, db_index=True)
    produto = models.ForeignKey(
        "products.Product",
        verbose_name="Produto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interacoes",
        db_index=True,
    )
    servico = models.ForeignKey(
        "services.Service",
        verbose_name="Serviço",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interacoes",
        db_index=True,
    )
    nome_produto_snapshot = models.CharField("Nome do produto", max_length=200, blank=True)
    preco_produto_snapshot = models.DecimalField(
        "Preço do produto", max_digits=10, decimal_places=2, null=True, blank=True
    )
    categoria_produto_snapshot = models.CharField("Categoria do produto", max_length=100, blank=True)
    nome_servico_snapshot = models.CharField("Nome do serviço", max_length=150, blank=True)
    ip_hash = models.CharField("Hash do IP", max_length=64, blank=True)
    user_agent = models.TextField("Navegador", blank=True)
    created_at = models.DateTimeField("Registrado em", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Registro de Interação"
        verbose_name_plural = "Registros de Interações"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tipo", "created_at"]),
            models.Index(fields=["produto", "created_at"]),
            models.Index(fields=["servico", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.created_at:%d/%m/%Y %H:%M}"
