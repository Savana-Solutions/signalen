# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Your Organization

from django.db import migrations


def forward_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")
    CategoryAssignment = apps.get_model("signals", "CategoryAssignment")
    StatusMessageTemplate = apps.get_model("signals", "StatusMessageTemplate")
    
    # Get the existing overig categories
    old_overig_categories = Category.objects.filter(slug='overig')
    
    # Store references to signals that need to be updated
    signals_to_update = set()
    for cat in old_overig_categories:
        assignments = CategoryAssignment.objects.filter(category=cat)
        for assignment in assignments:
            signals_to_update.add(assignment._signal_id)  # Note the underscore
    
    # Store existing status message templates
    existing_templates = list(StatusMessageTemplate.objects.filter(
        category__slug='overig'
    ))
    
    # First remove parent references to break circular dependencies
    old_overig_categories.update(parent=None)
    
    # Now we can safely delete the categories
    old_overig_categories.delete()
    
    # Create the parent 'Overig' category (with no parent)
    parent_overig = Category.objects.create(
        slug="overig",
        name="Overig",
        handling="REST",
        is_active=True,
        is_public_accessible=True,
        parent=None
    )
    
    # Create the child 'Overig' category
    child_overig = Category.objects.create(
        slug="overig",
        name="Overig",
        handling="REST",
        is_active=True,
        is_public_accessible=True,
        parent=parent_overig
    )
    
    # Update category assignments
    Signal = apps.get_model("signals", "Signal")
    for signal_id in signals_to_update:
        CategoryAssignment.objects.create(
            _signal_id=signal_id,  # Note the underscore
            category=child_overig,
            created_by='migration_script'
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
        ('signals', '0205_rename_category_slug'),  # Adjust this to your previous migration
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]