# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Your Organization

from django.db import migrations

def forward_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")
    CategoryAssignment = apps.get_model("signals", "CategoryAssignment")
    StatusMessageTemplate = apps.get_model("signals", "StatusMessageTemplate")
    
    # Store existing category assignments before deletion
    existing_assignments = list(CategoryAssignment.objects.filter(
        category__slug='overig'
    ).select_related('signal'))
    
    # Store existing status message templates
    existing_templates = list(StatusMessageTemplate.objects.filter(
        category__slug='overig'
    ))
    
    # Clean up any existing 'Overig' categories
    Category.objects.filter(slug='overig').delete()
    
    # Create the parent 'Overig' category (with no parent)
    parent_overig = Category.objects.create(
        slug="overig",
        name="Overig",
        handling="REST",
        is_active=True,
        is_public_accessible=True,
        parent=None  # Explicitly set no parent
    )
    
    # Create the child 'Overig' category
    child_overig = Category.objects.create(
        slug="overig",  # Same slug as parent
        name="Overig",
        handling="REST",
        is_active=True,
        is_public_accessible=True,
        parent=parent_overig
    )
    
    # Update existing category assignments to use the new child category
    for assignment in existing_assignments:
        CategoryAssignment.objects.create(
            signal=assignment.signal,
            category=child_overig,
            created_by=assignment.created_by or 'migration_script'
        )
    
    # Update status message templates to use the new child category
    for template in existing_templates:
        template.category = child_overig
        template.save()


def reverse_func(apps, schema_editor):
    # This migration is not safely reversible due to potential data loss
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0205_rename_category_slug'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]