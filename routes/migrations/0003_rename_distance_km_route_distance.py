from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("routes", "0002_rating"),
    ]

    operations = [
        migrations.RenameField(
            model_name="route",
            old_name="distance_km",
            new_name="distance",
        ),
    ]
