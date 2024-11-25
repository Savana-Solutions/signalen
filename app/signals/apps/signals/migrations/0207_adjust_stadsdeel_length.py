from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals", "0206_fix_overig_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="stadsdeel",
            field=models.CharField(
                choices=[
                    ("berghem", "Berghem"),
                    ("ckm", "CKM"),
                    ("geffen", "Geffen"),
                    ("herpen", "Herpen"),
                    ("lith", "Lith"),
                    ("mhm", "MHM"),
                    ("nw", "NW"),
                    ("oijen-teeffelen", "Oijen-Teeffelen"),
                    ("oss-zuid", "Oss-Zuid"),
                    ("ravenstein", "Ravenstein"),
                    ("ruwaard", "Ruwaard"),
                    ("schadewijk", "Schadewijk"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
