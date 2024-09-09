# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2021 Gemeente Amsterdam
from django.db import migrations


def create_initial_data_departments(apps, schema_editor):
    """Creating initial data for all departments."""
    departments = {
        # code, name,                    intern/extern
        'POA': ('Port of Amsterdam',     'E'),
        'THO': ('THOR',                  'I'),
        'WAT': ('Waternet',              'E'),
        'STW': ('Stadswerken',           'I'),
        'AEG': ('Afval en Grondstoffen', 'I'),
        'ASC': ('Actie Service Centrum', 'I'),
        'POL': ('Politie',               'E'),
        'GGD': ('GGD',                   'E'),
        'VOR': ('V&OR',                  'I'),  # Onderscheid V&OR OVL en V&OR VRI ???
        'OVL': ('V&OR OVL',              'I'),  # Onderscheid V&OR OVL en V&OR VRI ???
        'VRI': ('V&OR VRI',              'I'),  # Onderscheid V&OR OVL en V&OR VRI ???
        'CCA': ('CCA',                   'I'),
        'STL': ('Stadsloket',            'I'),
        'OMG': ('Omgevingsdienst',       'I'),  # Intern/extern ???
        'VTH': ('VTH',                   'I'),  # Wat is VTH ? Intern/Extern ?
        'FB':  ('FB',                    'I'),  # ?? what is FB
    }

    Department = apps.get_model('signals', 'Department')
    for department_code, department_values in departments.items():
        name = department_values[0]
        is_intern = department_values[1] == 'I'
        Department.objects.create(code=department_code, name=name, is_intern=is_intern)


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0008_department_maincategory_subcategory'),
    ]

    operations = [
        migrations.RunPython(create_initial_data_departments),
    ]
