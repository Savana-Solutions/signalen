# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2023 Your Organization

from django.db import migrations, models
from django.utils.text import slugify

categories = {
    "Wegen, fietspaden en troittoirs": [
        "Bestrating_schade",
        "Zwerfvuil/illegale stort",
        "Gladheidsbestrijding_Modder/olie",
        "Gladheidsbestrijding_Winter",
        "Verkeersbord/paal_schade",
        "Wegwerkzaamheden_hinder",
        "Voertuigen_lek",
        "Voertuigen_wrak",
        "Gevaarlijke_verkeerssituatie",
        "Wegen_overig",
    ],
    "Groenvoorziening": [
        "Gras_maaien",
        "Onkruid",
        "Heggen / hagen snoeien",
        "Overhangend_groen",
        "Gebroken_takken_bomen_",
        "Dode_boom",
        "Takken_groen",
        "Zwerfvuil/illegale sort",
        "Dode_dieren",
        "Invasieve exoten",
        "Groen_k&l",
        "Groen_overig",
    ],
    "afval": [
        "Zwerfvuil",
        "Illegale_stort",
        "Wietafval",
        "Drugsafval",
        "Prullenbak_kapot",
        "Bijplaatsing",
        "Afval_overig",
    ],
    "Openbare verlichting": [
        "Lamp_stuk",
        "Lamp(en)_knippert",
        "Lampen_branden_overdag",
        "Schade_paal_kap",
        "Luik_open",
        "Paal_ kapot",
        "Schakeltijd",
        "openbare_verlichting_overig",
    ],
    "Straatmeubilair": [
        "Stadsafsluiting_schade",
        "Speeltoestel_schade",
        "Bank_prullenbak_schade",
        "Bushalte_schade",
        "Hek_paal_zuil_schade",
        "Kunstwerken_schade",
        "straatmeubilair_overig",
    ],
    "Verkeersobjecten": [
        "VRI_schade",
        "VRI_regeling",
        "Verkeersbord_schade",
        "Straatnaambord_schade",
        "Snelheidsremmende_maatregelen",
        "Verkeersonveilige_situatie",
        "Parkeerverwijzing_schade",
        "Verkeersobjecten_overig",
        "Parkeergarage_slagboom_schade",
    ],
    "Sloten, (vaar)water en haven": [
        "Water_dichtgegroeid",
        "Waterkwaliteit_probleem",
        "Bruggen_tunnels_viaducten_schade",
        "Duikers_kapot",
        "Havenvoorzieningen_schade",
        "Waterstand",
        "Water_overig",
    ],
    "Riolering": [
        "Put_kolk_verstopt",
        "Bestrating_put",
        "Kolkdeksel_ontbreekt",
        "Putdeksel_ontbreekt",
        "Riolering_verstopt",
        "Stankoverlast",
        "Lamp_pompkast",
        "Druk- persriool",
        "Plassen",
        "Riool_borrelt",
        "Riolering_overig",
    ],
    "Overlast": [
        "Hondenpoep",
        "Loslopende_hond_kat",
        "Vandalisme",
        "Parkeren_klein_hinder",
        "Parkeren_groot_hinder",
        "Parkeren_fietsen_hinder",
        "Geluidsoverlast_continu",
        "Geluidsoverlast_evenementen",
        "Onbeheerd_voertuig",
        "Jeugdoverlast",
        "Grafitti",
        "Bouwmateriaal_gemeentegrond",
        "Reclameborden",
        "Gevaarlijke_verkeerssituatie",
        "Snelheid",
        "Straat_vegen",
        "Overlast_overig",
    ],
    "Plaagdieren": ["Ratten", "Vogels", "Eikenprocessierupsen", "Wespen"],
    "Overig": ["overig"],
}


def forward_func(apps, schema_editor):
    Category = apps.get_model("signals", "Category")
    Signal = apps.get_model("signals", "Signal")
    CategoryAssignment = apps.get_model("signals", "CategoryAssignment")
    StatusMessageTemplate = apps.get_model("signals", "StatusMessageTemplate")

    # Step 1: Ensure "Overig -> Overig" category exists
    overig_parent, _ = Category.objects.get_or_create(
        slug="overig",
        defaults={
            "name": "Overig",
            "handling": "REST",
            "is_active": True,
            "is_public_accessible": True,
        },
    )
    overig_category, _ = Category.objects.get_or_create(
        slug="overig",
        parent=overig_parent,
        defaults={
            "name": "overig",
            "handling": "REST",
            "is_active": True,
            "is_public_accessible": True,
        },
    )

    # Step 2: Assign all signals to "Overig -> Overig" category
    for signal in Signal.objects.all():
        CategoryAssignment.objects.get_or_create(
            signal=signal,
            defaults={
                "category": overig_category,
                "created_by": "migration_script",
            }
        )

    # Step 3: Rename existing categories (except Overig -> Overig)
    for category in Category.objects.exclude(id__in=[overig_parent.id, overig_category.id]):
        old_name = f"OLD_{category.name}"
        old_slug = f"old-{category.slug}"
        category.name = old_name
        category.slug = old_slug
        category.is_active = False
        category.save()

    # Step 4: Create new categories
    for main_category, sub_categories in categories.items():
        if main_category != "Overig":
            parent, _ = Category.objects.get_or_create(
                slug=slugify(main_category),
                defaults={
                    "name": main_category,
                    "handling": "REST",
                    "is_active": True,
                    "is_public_accessible": True,
                },
            )

            for sub_category in sub_categories:
                if sub_category != "overig":
                    Category.objects.get_or_create(
                        slug=slugify(sub_category),
                        defaults={
                            "name": sub_category,
                            "parent": parent,
                            "handling": "REST",
                            "is_active": True,
                            "is_public_accessible": True,
                        },
                    )

    # Step 5: Update StatusMessageTemplate references
    StatusMessageTemplate.objects.filter(category__name__startswith="OLD_").update(category=overig_category)

    # Step 6: Remove parent references from old categories and delete them
    Category.objects.filter(name__startswith="OLD_").update(parent=None)
    Category.objects.filter(name__startswith="OLD_").delete()


def reverse_func(apps, schema_editor):
    # This migration is not reversible
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "signals",
            "0202_create_missing_cats",
        ),  # Make sure this matches your previous migration
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
