from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_profile_cover_letters'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='privacy_agreed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='terms_agreed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
