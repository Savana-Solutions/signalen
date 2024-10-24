# SPDX-License-Identifier: MPL-2.0

from django.db import migrations
from django.utils.text import slugify

def convert_slug(old_slug):
    """Convert a slug to lowercase and replace hyphens with underscores."""
    return old_slug.lower().replace("-", "_")


def forward_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")

    # Update all category slugs
    for category in Category.objects.all():
        new_slug = convert_slug(category.slug)
        if new_slug != category.slug:
            # Check if the new slug already exists
            while Category.objects.filter(slug=new_slug).exists():
                new_slug = f"{new_slug}_1"
            category.slug = new_slug
            category.save()


def reverse_func(apps, schema_editor):
    # This migration is not reversible
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("signals", "0203_adjust_category_list"),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
