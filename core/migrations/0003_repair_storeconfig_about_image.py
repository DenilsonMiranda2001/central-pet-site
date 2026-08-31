from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_storeconfig_about_image"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "core_storeconfig" '
                'ADD COLUMN IF NOT EXISTS "about_image" varchar(100) NULL;'
            ),
            reverse_sql=(
                'ALTER TABLE "core_storeconfig" '
                'DROP COLUMN IF EXISTS "about_image";'
            ),
        ),
    ]
