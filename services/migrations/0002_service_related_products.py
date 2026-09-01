from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="related_products",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Selecione os produtos que devem aparecer nesta página de serviço. "
                    "Ideal para Boutique Pet e Medicamentos."
                ),
                related_name="related_services",
                to="products.product",
                verbose_name="Produtos relacionados",
            ),
        ),
    ]
