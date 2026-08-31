from django.db import migrations


def update_store_name(apps, schema_editor):
    StoreConfig = apps.get_model("core", "StoreConfig")
    StoreConfig.objects.filter(store_name="In Dog").update(
        store_name="In Dog - We trust Pet Boutique"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_repair_storeconfig_about_image"),
    ]

    operations = [
        migrations.RunPython(update_store_name, migrations.RunPython.noop),
    ]