# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Your Organization

from django.db import migrations
from django.utils.text import slugify

NEW_CATEGORIES = [
    "Lamp brandt niet",
    "Lamp gaat uit",
    "Lamp brandt zwak", 
    "Lamp knippert",
    "Meerdere lampen branden niet",
    "Lamp(en) branden overdag",
    "Armatuur ontbreekt",
    "Armatuur beschadigd",
    "Mast scheef",
    "Mastluikje ontbreekt", 
    "Mast aangereden",
    "Overig"
]

def create_slug(name):
    """Create a consistent slug format using underscores."""
    # First use Django's slugify to handle basic character conversion
    slug = slugify(name)
    # Replace hyphens with underscores
    slug = slug.replace('-', '_')
    # Ensure it's lowercase
    return slug.lower()

def forward_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")
    CategoryAssignment = apps.get_model("signals", "CategoryAssignment")
    StatusMessageTemplate = apps.get_model("signals", "StatusMessageTemplate")

    # Get or create the parent category
    parent_category, _ = Category.objects.get_or_create(
        slug="openbare_verlichting",  # Hardcoded to ensure consistency
        defaults={
            "name": "Openbare Verlichting",
            "handling": "REST",
            "is_active": True,
            "is_public_accessible": True
        }
    )

    # Create new 'Overig' subcategory first
    overig_category, _ = Category.objects.get_or_create(
        slug="openbare_verlichting_overig",  # Hardcoded to ensure consistency
        defaults={
            "name": "Overig",
            "parent": parent_category,
            "handling": "REST",
            "is_active": True,
            "is_public_accessible": True
        }
    )

    # Get all existing subcategories
    old_subcategories = Category.objects.filter(parent=parent_category).exclude(id=overig_category.id)

    # Move all existing category assignments to the new 'Overig' subcategory
    for old_category in old_subcategories:
        CategoryAssignment.objects.filter(category=old_category).update(
            category=overig_category,
            created_by="migration_script"
        )
        
        # Update any status message templates
        StatusMessageTemplate.objects.filter(category=old_category).update(
            category=overig_category
        )

    # Delete old subcategories
    old_subcategories.delete()

    # Create new subcategories
    for category_name in NEW_CATEGORIES:
        if category_name != "Overig":  # Skip Overig as we already created it
            slug = create_slug(category_name)
            # Add prefix to ensure uniqueness and consistency
            full_slug = f"openbare_verlichting_{slug}"
            
            Category.objects.get_or_create(
                slug=full_slug,
                defaults={
                    "name": category_name,
                    "parent": parent_category,
                    "handling": "REST",
                    "is_active": True,
                    "is_public_accessible": True
                }
            )

def reverse_func(apps, schema_editor):
    # This migration is not safely reversible
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0207_adjust_stadsdeel_length'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]