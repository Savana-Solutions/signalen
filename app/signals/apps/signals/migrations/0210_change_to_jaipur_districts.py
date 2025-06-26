from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("signals", "0209_fix_moon_categories"),
    ]

    operations = [
        # First, clear existing district data to remove all Oss district references
        migrations.RunSQL(
            "UPDATE signals_location SET stadsdeel = NULL WHERE stadsdeel IS NOT NULL;",
            reverse_sql="-- No reverse operation needed for data cleanup"
        ),
        
        # Then update the field choices to use the new Jaipur districts
        migrations.AlterField(
            model_name="location",
            name="stadsdeel",
            field=models.CharField(
                choices=[
                    ("vidyadhar-nagar", "Vidyadhar Nagar"),
                    ("jhotwara", "Jhotwara"),
                    ("sanganer", "Sanganer"),
                    ("bagru", "Bagru"),
                    ("malviya-nagar", "Malviya Nagar"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
