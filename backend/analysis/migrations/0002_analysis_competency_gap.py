from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='competency_gap',
            field=models.JSONField(default=dict),
        ),
    ]
