# Generated by Django 5.1.3 on 2024-11-28 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_userprofile_stripe_subscription_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='subscription_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]