# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Your Organization

from django.db import migrations

def fix_slugs(apps, schema_editor):
    Category = apps.get_model("signals", "Category")
    
    # Get the parent category
    try:
        parent = Category.objects.get(slug="openbare_verlichting")
        
        # Update all subcategories
        for category in Category.objects.filter(parent=parent):
            # Convert existing slug to correct format
            new_slug = category.slug.replace('-', '_').replace('openbare_verlichting_', '')
            
            # Special case for 'overig'
            if new_slug == "overig":
                new_slug = "lamp_overig"
                
            # Update the slug
            category.slug = new_slug
            category.save()
            
    except Category.DoesNotExist:
        pass

def reverse_func(apps, schema_editor):
    # This migration is not safely reversible
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0208_create_new_moon_categories'),
    ]

    operations = [
        migrations.RunPython(fix_slugs, reverse_func),
    ]