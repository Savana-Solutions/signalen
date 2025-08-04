# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021 Gemeente Amsterdam
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0140_category_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='state',
            field=models.CharField(
                blank=True,
                choices=[
                    ('m', 'Reported'),
                    ('i', 'Awaiting handling'),
                    ('b', 'In progress'),
                    ('h', 'On hold'),
                    ('planned', 'Planned'),
                    ('ready to send', 'To send naar extern systeem'),
                    ('o', 'Completed'),
                    ('a', 'Cancelled'),
                    ('reopened', 'Reopened'),
                    ('s', 'Split'),
                    ('closure requested', 'Verzoek tot afhandeling'),
                    ('reaction requested', 'Reaction requested'),
                    ('reaction received', 'Reaction received'),
                    ('sent', 'Verzonden naar extern systeem'),
                    ('send failed', 'Verzending naar extern systeem mislukt'),
                    ('done external', 'Melding is afgehandeld in extern systeem'),
                    ('reopen requested', 'Request to reopen')
                ],
                default='m',
                help_text='Melding status',
                max_length=20
            ),
        ),
        migrations.AlterField(
            model_name='statusmessagetemplate',
            name='state',
            field=models.CharField(
                choices=[
                    ('m', 'Reported'),
                    ('i', 'Awaiting handling'),
                    ('b', 'In progress'),
                    ('h', 'On hold'),
                    ('planned', 'Planned'),
                    ('ready to send', 'To send naar extern systeem'),
                    ('o', 'Completed'),
                    ('a', 'Cancelled'),
                    ('reopened', 'Reopened'),
                    ('s', 'Split'),
                    ('closure requested', 'Verzoek tot afhandeling'),
                    ('reaction requested', 'Reaction requested'),
                    ('reaction received', 'Reaction received'),
                    ('sent', 'Verzonden naar extern systeem'),
                    ('send failed', 'Verzending naar extern systeem mislukt'),
                    ('done external', 'Melding is afgehandeld in extern systeem'),
                    ('reopen requested', 'Request to reopen')
                ],
                max_length=20
            ),
        ),
    ]
