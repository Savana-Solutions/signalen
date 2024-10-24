# SPDX-License-Identifier: MPL-2.0

from django.db import migrations


def forward_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")

    try:
        category = Category.objects.get(slug="wegen_fietspaden_en_troittoirs")
        category.slug = "wegen_fietspaden_troittoirs"
        category.save()
    except Category.DoesNotExist:
        pass


def reverse_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")

    try:
        category = Category.objects.get(slug="wegen_fietspaden_troittoirs")
        category.slug = "wegen_fietspaden_en_troittoirs"
        category.save()
    except Category.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "signals",
            "0204_rename_slugs",
        ),  # Adjust this to your previous migration
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
