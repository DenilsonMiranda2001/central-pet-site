from django import forms
from django.core.exceptions import ValidationError
from products.models import Product, Category
from services.models import Service
from core.models import StoreConfig, Banner, Testimonial


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE_MB = 5


def validate_panel_image(image):
    if not image:
        return

    extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Envie uma imagem em JPG, JPEG, PNG ou WEBP.")

    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"A imagem deve ter até {MAX_IMAGE_SIZE_MB} MB.")


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'short_description', 'description',
            'price', 'original_price', 'image',
            'is_featured', 'is_available', 'is_active', 'order',
        ]
        labels = {
            'name': 'Nome do produto',
            'category': 'Categoria',
            'short_description': 'Descrição curta',
            'description': 'Descrição completa',
            'price': 'Preço (R$)',
            'original_price': 'Preço original / De (R$)',
            'image': 'Imagem',
            'is_featured': 'Produto em destaque',
            'is_available': 'Disponível em estoque',
            'is_active': 'Ativo no site',
            'order': 'Ordem de exibição',
        }
        help_texts = {
            'original_price': 'Preencha para exibir o desconto. Deixe em branco se não houver.',
            'order': 'Número menor aparece primeiro. Ex: 1, 2, 3...',
            'short_description': 'Aparece nos cards de produto (máx. 120 caracteres).',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Ração Royal Canin 15kg'}),
            'category': forms.Select(attrs={'class': 'panel-input'}),
            'short_description': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Resumo curto do produto'}),
            'description': forms.Textarea(attrs={'class': 'panel-input', 'rows': 4, 'placeholder': 'Descrição detalhada...'}),
            'price': forms.NumberInput(attrs={'class': 'panel-input', 'step': '0.01', 'min': '0', 'placeholder': '0,00'}),
            'original_price': forms.NumberInput(attrs={'class': 'panel-input', 'step': '0.01', 'min': '0', 'placeholder': '0,00'}),
            'image': forms.ClearableFileInput(attrs={'class': 'panel-file-input', 'accept': 'image/*'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'order': forms.NumberInput(attrs={'class': 'panel-input', 'min': '0', 'placeholder': '0'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_panel_image(image)
        return image


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'is_active', 'order']
        labels = {
            'name': 'Nome da categoria',
            'icon': 'Ícone (emoji)',
            'is_active': 'Ativa no site',
            'order': 'Ordem de exibição',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Rações'}),
            'icon': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: 🍖'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'order': forms.NumberInput(attrs={'class': 'panel-input', 'min': '0'}),
        }


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'name', 'icon', 'short_description', 'description',
            'price_from', 'image',
            'is_featured', 'is_active', 'order',
        ]
        labels = {
            'name': 'Nome do serviço',
            'icon': 'Ícone (emoji)',
            'short_description': 'Descrição curta',
            'description': 'Descrição completa',
            'price_from': 'Preço a partir de (R$)',
            'image': 'Imagem',
            'is_featured': 'Serviço em destaque',
            'is_active': 'Ativo no site',
            'order': 'Ordem de exibição',
        }
        help_texts = {
            'price_from': 'Deixe em branco se o preço for variável.',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Banho & Tosa'}),
            'icon': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: ✂️'}),
            'short_description': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Resumo do serviço'}),
            'description': forms.Textarea(attrs={'class': 'panel-input', 'rows': 4}),
            'price_from': forms.NumberInput(attrs={'class': 'panel-input', 'step': '0.01', 'min': '0', 'placeholder': '0,00'}),
            'image': forms.ClearableFileInput(attrs={'class': 'panel-file-input', 'accept': 'image/*'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'order': forms.NumberInput(attrs={'class': 'panel-input', 'min': '0'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_panel_image(image)
        return image


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'image', 'button_text', 'button_link', 'is_active', 'order']
        labels = {
            'title': 'Título do banner',
            'subtitle': 'Subtítulo',
            'image': 'Imagem',
            'button_text': 'Texto do botão',
            'button_link': 'Link do botão',
            'is_active': 'Ativo no site',
            'order': 'Ordem de exibição',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Promoção de Verão'}),
            'subtitle': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Subtítulo do banner'}),
            'image': forms.ClearableFileInput(attrs={'class': 'panel-file-input', 'accept': 'image/*'}),
            'button_text': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Ver promoção'}),
            'button_link': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: /produtos/'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'order': forms.NumberInput(attrs={'class': 'panel-input', 'min': '0'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_panel_image(image)
        return image


class DepoimentoForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['customer_name', 'pet_name', 'rating', 'comment', 'is_active', 'order']
        labels = {
            'customer_name': 'Nome do cliente',
            'pet_name': 'Nome do pet',
            'rating': 'Nota (1 a 5)',
            'comment': 'Comentário',
            'is_active': 'Ativo no site',
            'order': 'Ordem de exibição',
        }
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Ana Paula S.'}),
            'pet_name': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'Ex: Golden (opcional)'}),
            'rating': forms.Select(choices=[(i, f'{i} estrela{"s" if i > 1 else ""}') for i in range(1, 6)], attrs={'class': 'panel-input'}),
            'comment': forms.Textarea(attrs={'class': 'panel-input', 'rows': 3, 'placeholder': 'O depoimento do cliente...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'order': forms.NumberInput(attrs={'class': 'panel-input', 'min': '0'}),
        }


class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = StoreConfig
        fields = [
            'store_name', 'slogan', 'whatsapp_number', 'phone_number',
            'instagram_url', 'facebook_url', 'tiktok_url', 'email',
            'address', 'maps_url', 'opening_hours', 'delivery_text', 'about_text',
        ]
        labels = {
            'store_name': 'Nome da loja',
            'slogan': 'Slogan',
            'whatsapp_number': 'Número do WhatsApp',
            'phone_number': 'Telefone fixo',
            'instagram_url': 'Instagram (usuário, sem @)',
            'facebook_url': 'Facebook (URL ou usuário)',
            'tiktok_url': 'TikTok (usuário, sem @)',
            'email': 'E-mail de contato',
            'address': 'Endereço completo',
            'maps_url': 'Link do Google Maps',
            'opening_hours': 'Horário de funcionamento',
            'delivery_text': 'Texto de entrega (destaque)',
            'about_text': 'Texto "Sobre a loja"',
        }
        help_texts = {
            'whatsapp_number': 'Somente números. Ex: 5561996600007',
            'maps_url': 'Cole o link completo do Google Maps.',
        }
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'panel-input'}),
            'slogan': forms.TextInput(attrs={'class': 'panel-input'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': '5561999999999'}),
            'phone_number': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': '(61) 3000-0000'}),
            'instagram_url': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'indogpet'}),
            'facebook_url': forms.TextInput(attrs={'class': 'panel-input'}),
            'tiktok_url': forms.TextInput(attrs={'class': 'panel-input'}),
            'email': forms.EmailInput(attrs={'class': 'panel-input'}),
            'address': forms.Textarea(attrs={'class': 'panel-input', 'rows': 2}),
            'maps_url': forms.URLInput(attrs={'class': 'panel-input'}),
            'opening_hours': forms.Textarea(attrs={'class': 'panel-input', 'rows': 2}),
            'delivery_text': forms.TextInput(attrs={'class': 'panel-input'}),
            'about_text': forms.Textarea(attrs={'class': 'panel-input', 'rows': 5}),
        }

    def clean_whatsapp_number(self):
        number = "".join(ch for ch in self.cleaned_data.get('whatsapp_number', '') if ch.isdigit())
        if len(number) in (10, 11):
            number = f"55{number}"
        if len(number) < 12 or len(number) > 13:
            raise ValidationError("Informe o WhatsApp com DDD e país. Ex: 5561999999999.")
        return number
