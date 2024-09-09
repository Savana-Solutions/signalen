# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Your Organization

from django.db import migrations, models
from django.utils.text import slugify

categories = {
    'groenvoorziening': [
        'Gebroken_takken_bomen_', 'Overhangend_groen', 'Onkruid', 'Takken_groen',
        'Groen_overig', 'Gras_maaien', 'Heggen / hagen snoeien', 'Dode_boom',
        'Dode_dieren', 'Invasieve exoten', 'Hondenpoep', 'Zwerfvuil/illegale sort',
        'Eikenprocessierupsen', 'Groen_k&l'
    ],
    'wegen fietspaden troitoirs': [
        'Wegen_overig', 'Bestrating_schade', 'Gevaarlijke_verkeerssituatie',
        'Wegwerkzaamheden_hinder', 'Verkeersbord/paal_schade',
        'Gladheidsbestrijding_Modder/olie', 'Onkruid', 'Plassen',
        'Zwerfvuil/illegale stort', 'Voertuigen_lek', 'Voertuigen_wrak',
        'Dode_dieren', 'Gladheidsbestrijding_Winter', 'Drugsafval'
    ],
    'afval': [
        'Zwerfvuil', 'Bijplaatsing', 'Illegale_stort', 'Afval_overig',
        'Prullenbak_kapot', 'Wietafval', 'Drugsafval', 'Voertuigen_wrak',
        'Voertuigen_lek', 'Drugsnaalden'
    ],
    'overig': ['overig'],
    'straatmeubilair': [
        'straatmeubilair_overig', 'Hek_paal_zuil_schade', 'Kunstwerken_schade',
        'Verkeersbord_schade', 'Bank_prullenbak_schade', 'Speeltoestel_schade',
        'Straatnaambord_schade', 'Parkeergarage_slagboom_schade', 'Grafitti',
        'Bruggen_viaducten_schade', 'Bushalte_schade'
    ],
    'overlast': [
        'Geluidsoverlast_continu', 'Loslopende_hond_kat', 'Hondenpoep',
        'Parkeren_klein_hinder', 'Overlast_overig', 'Straat_vegen', 'Vandalisme',
        'Parkeren_fietsen_hinder', 'Gevaarlijke_verkeerssituatie',
        'Bouwmateriaal_gemeentegrond', 'Geluidsoverlast_evenementen',
        'Parkeren_groot_hinder', 'Jeugdoverlast', 'Onbeheerd_voertuig',
        'Snelheid', 'Reclameborden', 'Illegale_stort', 'Grafitti'
    ],
    'plaagdieren': ['Ratten', 'Wespen', 'Vogels', 'Eikenprocessierupsen'],
    'riolering': [
        'Riolering_verstopt', 'Druk- persriool', 'Lamp_pompkast', 'Plassen',
        'Put_kolk_verstopt', 'Riolering_overig', 'Bestrating_put', 'Riool_borrelt',
        'Kolkdeksel_ontbreekt', 'Stankoverlast', 'Putdeksel_ontbreekt', 'Ratten'
    ],
    'verkeersobjecten': [
        'VRI_regeling', 'Verkeersobjecten_overig', 'Verkeersonveilige_situatie',
        'Verkeersbord_schade', 'VRI_werkt_niet', 'Snelheidsremmende_maatregelen',
        'Straatnaambord_schade', 'VRI_knippert', 'VRI_schade',
        'VRI_armatuur_beschadigd', 'VRI_lamp_kapot', 'Reclamebord_schade',
        'Parkeerverwijzing_schade', 'Bruggen_tunnels_viaducten_kapot'
    ],
    'sloten water haven': [
        'Illegale_stort', 'Water_dichtgegroeid', 'Water_overig',
        'Duikers_kapot', 'Waterkwaliteit_probleem',
        'Bruggen_tunnels_viaducten_kapot', 'Havenvoorzieningen_schade',
        'Waterstand', 'Waterplanten_berm'
    ]
}

def forward_categories(apps, schema_editor):
    Category = apps.get_model('signals', 'Category')
    
    # Mark all existing categories as old and set them to inactive and not public accessible
    for category in Category.objects.all():
        category.name = f"OLD_{category.name}"
        category.is_active = False
        category.is_public_accessible = False
        category.save()
    
    for main_category, sub_categories in categories.items():
        parent, created = Category.objects.get_or_create(
            slug=slugify(main_category),
            defaults={
                'name': main_category,
                'handling': 'REST',
                'is_active': True,
                'is_public_accessible': True
            }
        )
        if not created:
            parent.name = main_category
            parent.is_active = True
            parent.is_public_accessible = True
            parent.save()
        
        for sub_category in sub_categories:
            sub_cat, created = Category.objects.get_or_create(
                slug=slugify(sub_category),
                parent=parent,
                defaults={
                    'name': sub_category,
                    'handling': 'REST',
                    'is_active': True,
                    'is_public_accessible': True
                }
            )
            if not created:
                sub_cat.name = sub_category
                sub_cat.is_active = True
                sub_cat.is_public_accessible = True
                sub_cat.save()

def reverse_categories(apps, schema_editor):
    Category = apps.get_model('signals', 'Category')
    
    # Revert new categories
    for main_category, sub_categories in categories.items():
        Category.objects.filter(slug=slugify(main_category)).update(is_active=False, is_public_accessible=False)
        for sub_category in sub_categories:
            Category.objects.filter(slug=slugify(sub_category)).update(is_active=False, is_public_accessible=False)
    
    # Reactivate old categories and remove the "OLD_" prefix
    for category in Category.objects.filter(name__startswith="OLD_"):
        category.name = category.name[4:]  # Remove "OLD_" prefix
        category.is_active = True
        category.is_public_accessible = True
        category.save()

class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0197_auto_20231030_1323'),  # Update this to your last migration
    ]

    operations = [
        migrations.RunPython(forward_categories, reverse_categories),
    ]